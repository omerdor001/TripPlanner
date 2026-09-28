from models import CityAttractionSet, Language

BASE_SYSTEM_PROMPT = """You are a European city-trip planning assistant. Given a \
city, a number of days, traveler interests, and a budget level, you generate \
a curated list of top attractions for that city.

Rules:
- The city name you're given may be in any language, script, or \
transliteration (English, Hebrew, or otherwise) — e.g. "Vienna", "Wien", \
and "וינה" all refer to the same city. First identify the one real, \
specific city (and country) this unambiguously refers to, and put that in \
"resolved_city" as "City, Country" in English. Be careful not to confuse \
cities that sound or look similar (e.g. Vienna vs. Prague, Florence vs. \
Firenze vs. Florida) — if you are not confident, pick the single most \
famous, most populous real city with that name. Every attraction you list \
must be a real place actually located in that resolved city — never mix in \
attractions from a different city.
- Return between (days * 3) and (days * 4) attractions so there is enough \
material to build a day-by-day itinerary without repeats.
- Assign each attraction a "neighborhood" (the area/district it's in) so \
attractions can later be grouped by proximity — pick real, specific \
neighborhood names for the city, not generic labels.
- Give every attraction an "address": its full street address as written \
locally, in Latin script, including postal code, city and country (e.g. \
"Heldenplatz, 1010 Vienna, Austria"). It is used to build a Google Maps \
link, so make it as precise as you can — for a place without a street \
address (a park, a market), give the closest street or entrance. Never \
invent an address; if you are unsure of the exact street, give the \
best-known one.
- Tailor selection to the stated interests and budget level. If interests \
are empty, cover a broad, well-rounded mix (major landmarks, food, culture).
- All factual details (hours, prices) are best-effort and may be outdated — \
always set "unverified": true on every attraction.
- Do not repeat the same attraction twice.
- Respond with ONLY valid JSON matching the provided schema — no prose, no \
markdown code fences, no commentary before or after the JSON.
"""

LANGUAGE_NAMES: dict[Language, str] = {
    "en": "English",
    "he": "Hebrew (עברית)",
}

LANGUAGE_INSTRUCTIONS: dict[Language, str] = {
    "en": "",
    "he": (
        "\nLanguage: write every natural-language text value in Hebrew — "
        '"name", "description", "neighborhood", "cost_notes", '
        '"best_time_to_visit", "opening_hours", and every string in '
        '"general_tips". Use natural, fluent Hebrew, not a literal '
        'transliteration. The "category" field is the one exception: it '
        "must stay exactly one of the fixed English enum values (art, "
        "history, food, nightlife, nature, shopping, other) — do not "
        "translate it. The \"address\" field is the other exception: keep "
        "it in local Latin script so it can be found on Google Maps.\n"
    ),
}

JSON_SCHEMA_HINT = CityAttractionSet.model_json_schema()


def build_system_prompt(language: Language) -> str:
    return BASE_SYSTEM_PROMPT + LANGUAGE_INSTRUCTIONS[language]


def build_user_prompt(
    city: str,
    days: int,
    interests: list[str],
    budget_level: str | None,
    language: Language,
) -> str:
    interests_str = ", ".join(interests) if interests else "no specific preference — broad mix"
    budget_str = budget_level or "not specified — assume mid-range"
    return f"""City: {city}
Trip length in this city: {days} day(s)
Traveler interests: {interests_str}
Budget level: {budget_str}
Response language: {LANGUAGE_NAMES[language]}

Generate the attraction list as JSON matching this schema:
{JSON_SCHEMA_HINT}

Return only the JSON object, with "city" set to "{city}".
"""


def build_retry_prompt(previous_error: str) -> str:
    return (
        "Your previous response was not valid JSON matching the schema. "
        f"Validation error: {previous_error}\n"
        "Return ONLY a corrected valid JSON object matching the schema, "
        "with no prose or markdown fences."
    )
