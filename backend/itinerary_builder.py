import math
from collections import OrderedDict
from typing import List

from models import Attraction, DayPlan, Language

UNKNOWN_NEIGHBORHOOD = "Other"

_SAME_AREA_TIP: dict[Language, str] = {
    "en": "All stops today are in the same area — easily walkable.",
    "he": "כל התחנות היום נמצאות באותו אזור — ניתן להגיע ברגל בקלות.",
}


def _spans_areas_tip(language: Language, count: int, neighborhoods: List[str]) -> str:
    joined = ", ".join(neighborhoods)
    if language == "he":
        return f"היום המסלול פרוש על פני {count} אזורים ({joined}) — כדאי להשתמש בתחבורה ציבורית או במונית בין התחנות."
    return (
        f"Today spans {count} areas ({joined}) — "
        "consider public transit or a taxi between stops."
    )


def _group_by_neighborhood(attractions: List[Attraction]) -> "OrderedDict[str, List[Attraction]]":
    groups: "OrderedDict[str, List[Attraction]]" = OrderedDict()
    for attraction in attractions:
        key = attraction.neighborhood or UNKNOWN_NEIGHBORHOOD
        groups.setdefault(key, []).append(attraction)
    return groups


def build_day_plans(
    city: str, days: int, attractions: List[Attraction], language: Language = "en"
) -> List[DayPlan]:
    """Split attractions into `days` DayPlans. Whole neighborhoods are kept
    together and balanced across days (largest-cluster-first bin packing),
    then any day left empty is topped up from the fullest day so every day
    gets at least one attraction whenever there are enough to go around."""
    if days < 1:
        raise ValueError("days must be >= 1")

    total = len(attractions)
    groups = list(_group_by_neighborhood(attractions).values())

    # Cap how much of a single neighborhood can land in one bucket, so one
    # oversized neighborhood doesn't dominate a single day while others sit
    # empty — split it into same-neighborhood chunks instead.
    target_per_day = max(1, math.ceil(total / days))
    pieces: List[List[Attraction]] = []
    for group in groups:
        if len(group) > target_per_day:
            pieces.extend(
                group[i : i + target_per_day] for i in range(0, len(group), target_per_day)
            )
        else:
            pieces.append(group)

    day_buckets: List[List[Attraction]] = [[] for _ in range(days)]
    for piece in sorted(pieces, key=len, reverse=True):
        target_day = min(range(days), key=lambda i: len(day_buckets[i]))
        day_buckets[target_day].extend(piece)

    while total >= days and any(len(bucket) == 0 for bucket in day_buckets):
        empty_idx = next(i for i, b in enumerate(day_buckets) if len(b) == 0)
        donor_idx = max(range(days), key=lambda i: len(day_buckets[i]))
        if len(day_buckets[donor_idx]) <= 1:
            break
        day_buckets[empty_idx].append(day_buckets[donor_idx].pop())

    day_plans: List[DayPlan] = []
    for day_idx, bucket in enumerate(day_buckets):
        neighborhoods = list(
            dict.fromkeys(a.neighborhood or UNKNOWN_NEIGHBORHOOD for a in bucket)
        )
        if len(neighborhoods) <= 1:
            tip = _SAME_AREA_TIP[language]
        else:
            tip = _spans_areas_tip(language, len(neighborhoods), neighborhoods)
        day_plans.append(
            DayPlan(
                day_number=day_idx + 1,
                city=city,
                attractions=bucket,
                getting_around_tip=tip if bucket else None,
            )
        )
    return day_plans
