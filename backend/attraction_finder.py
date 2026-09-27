import json
import re

from anthropic import Anthropic, APIError
from pydantic import ValidationError

from config import ANTHROPIC_API_KEY, ANTHROPIC_MODEL
from models import CityAttractionSet, Language
from prompts import build_retry_prompt, build_system_prompt, build_user_prompt

_client = Anthropic(api_key=ANTHROPIC_API_KEY)

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


def get_city_attractions(
    city: str,
    days: int,
    interests: list[str],
    budget_level: str | None,
    language: Language = "en",
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
