import json
import logging
import re

from anthropic import Anthropic, APIError
from pydantic import ValidationError

from cache import JsonCache, make_key
from config import (
    ANTHROPIC_API_KEY,
    ANTHROPIC_MODEL,
    CACHE_DIR,
    CACHE_ENABLED,
    CACHE_TTL_SECONDS,
)
from models import CityAttractionSet, Language
from prompts import (
    JSON_SCHEMA_HINT,
    build_retry_prompt,
    build_system_prompt,
    build_user_prompt,
)

logger = logging.getLogger(__name__)

_client = Anthropic(api_key=ANTHROPIC_API_KEY)
_cache = JsonCache(CACHE_DIR, CACHE_TTL_SECONDS, enabled=CACHE_ENABLED)

_FENCE_RE = re.compile(r"^```(?:json)?\s*|\s*```$", re.MULTILINE)


class AttractionGenerationError(RuntimeError):
    """Raised when the LLM fails to produce valid, schema-conforming JSON."""


def _strip_fences(text: str) -> str:
    return _FENCE_RE.sub("", text).strip()


def _call_model(messages: list[dict], system_prompt: str) -> str:
    response = _client.messages.create(
        model=ANTHROPIC_MODEL,
        max_tokens=4096,
        system=system_prompt,
        messages=messages,
    )
    return "".join(
        block.text for block in response.content if block.type == "text"
    )


def _cache_key(
    city: str,
    days: int,
    interests: list[str],
    budget_level: str | None,
    language: Language,
) -> str:
    # Inputs are normalized so "Vienna " / "vienna" and reordered interests share
    # an entry. The model and the full prompt + schema are part of the key, so
    # changing any of them automatically stops serving stale results.
    return make_key(
        " ".join(city.split()).casefold(),
        days,
        sorted({i.strip().casefold() for i in interests if i.strip()}),
        (budget_level or "").strip().casefold(),
        language,
        ANTHROPIC_MODEL,
        build_system_prompt(language),
        JSON_SCHEMA_HINT,
    )


def get_city_attractions(
    city: str,
    days: int,
    interests: list[str],
    budget_level: str | None,
    language: Language = "en",
    refresh: bool = False,
) -> CityAttractionSet:
    """Return the attraction set for a city, served from cache when possible.

    Pass `refresh=True` to skip the cache read and regenerate (the fresh
    result still replaces the cached entry)."""
    key = _cache_key(city, days, interests, budget_level, language)

    # Hold the per-key lock across the LLM call so identical concurrent
    # requests wait for one generation instead of each paying for their own.
    with _cache.lock_for(key):
        cached = None if refresh else _cache.get(key)
        if cached is not None:
            try:
                city_set = CityAttractionSet.model_validate(cached)
                logger.info("Cache hit for %s (%d day(s))", city, days)
                return city_set
            except ValidationError:
                logger.warning("Discarding cache entry that no longer matches the schema")
                _cache.delete(key)

        logger.info("Cache miss for %s (%d day(s)) — calling the model", city, days)
        city_set = _generate_city_attractions(city, days, interests, budget_level, language)
        _cache.set(key, city_set.model_dump(mode="json"))
        return city_set


def _generate_city_attractions(
    city: str,
    days: int,
    interests: list[str],
    budget_level: str | None,
    language: Language,
) -> CityAttractionSet:
    system_prompt = build_system_prompt(language)
    user_prompt = build_user_prompt(city, days, interests, budget_level, language)
    messages = [{"role": "user", "content": user_prompt}]

    try:
        raw_text = _call_model(messages, system_prompt)
    except APIError as error:
        raise AttractionGenerationError(
            f"Claude API request failed while planning {city}: {error}"
        ) from error

    try:
        return CityAttractionSet.model_validate_json(_strip_fences(raw_text))
    except (ValidationError, json.JSONDecodeError) as first_error:
        messages.append({"role": "assistant", "content": raw_text})
        messages.append(
            {"role": "user", "content": build_retry_prompt(str(first_error))}
        )
        try:
            retry_text = _call_model(messages, system_prompt)
        except APIError as error:
            raise AttractionGenerationError(
                f"Claude API request failed while retrying {city}: {error}"
            ) from error
        try:
            return CityAttractionSet.model_validate_json(_strip_fences(retry_text))
        except (ValidationError, json.JSONDecodeError) as second_error:
            raise AttractionGenerationError(
                f"Model failed to produce valid attraction data for {city} "
                f"after retry: {second_error}"
            ) from second_error
