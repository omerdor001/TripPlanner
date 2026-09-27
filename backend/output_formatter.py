from models import Attraction, Language, TripPlan

_LABELS: dict[Language, dict[str, str]] = {
    "en": {
        "trip_plan": "Trip Plan",
        "days": "days",
        "interests": "Interests",
        "budget_level": "Budget level",
        "day": "Day",
        "notes": "Notes",
        "general_tips": "General tips",
        "neighborhood": "Neighborhood",
        "best_time_to_visit": "Best time to visit",
        "opening_hours": "Opening hours",
        "booking_recommended": "Booking recommended in advance",
        "cost_unknown": "cost unknown",
    },
    "he": {
        "trip_plan": "תוכנית טיול",
        "days": "ימים",
        "interests": "תחומי עניין",
        "budget_level": "רמת תקציב",
        "day": "יום",
        "notes": "הערות",
        "general_tips": "טיפים כלליים",
        "neighborhood": "שכונה",
        "best_time_to_visit": "זמן מומלץ לביקור",
        "opening_hours": "שעות פתיחה",
        "booking_recommended": "מומלץ להזמין מקום מראש",
        "cost_unknown": "עלות לא ידועה",
    },
}


def _format_cost(attraction: Attraction, labels: dict[str, str]) -> str:
    if attraction.approximate_cost_eur is not None:
        cost = f"€{attraction.approximate_cost_eur:g}"
        return f"{cost} ({attraction.cost_notes})" if attraction.cost_notes else cost
    return attraction.cost_notes or labels["cost_unknown"]


def _format_attraction(attraction: Attraction, labels: dict[str, str]) -> str:
    lines = [
        f"- **{attraction.name}** ({attraction.category}, "
        f"~{attraction.estimated_duration_minutes} min, {_format_cost(attraction, labels)})",
        f"  {attraction.description}",
    ]
    if attraction.neighborhood:
        lines.append(f"  - {labels['neighborhood']}: {attraction.neighborhood}")
    if attraction.best_time_to_visit:
        lines.append(f"  - {labels['best_time_to_visit']}: {attraction.best_time_to_visit}")
    if attraction.opening_hours:
        lines.append(f"  - {labels['opening_hours']}: {attraction.opening_hours}")
    if attraction.booking_recommended:
        lines.append(f"  - {labels['booking_recommended']}")
    return "\n".join(lines)


def trip_plan_to_markdown(trip_plan: TripPlan) -> str:
    labels = _LABELS[trip_plan.language]
    parts = [
        f"# {labels['trip_plan']}: {', '.join(trip_plan.cities)} "
        f"({trip_plan.total_days} {labels['days']})"
    ]
    parts.append(f"\n_{trip_plan.disclaimer}_\n")

    if trip_plan.interests:
        parts.append(f"**{labels['interests']}:** {', '.join(trip_plan.interests)}  ")
    if trip_plan.budget_level:
        parts.append(f"**{labels['budget_level']}:** {trip_plan.budget_level}  ")

    for day in trip_plan.day_plans:
        parts.append(f"\n## {day.city} — {labels['day']} {day.day_number}")
        if day.getting_around_tip:
            parts.append(f"_{day.getting_around_tip}_\n")
        for attraction in day.attractions:
            parts.append(_format_attraction(attraction, labels))
        if day.notes:
            parts.append(f"\n**{labels['notes']}:** {day.notes}")

    if trip_plan.general_tips:
        parts.append(f"\n## {labels['general_tips']}")
        for tip in trip_plan.general_tips:
            parts.append(f"- {tip}")

    return "\n".join(parts) + "\n"


def trip_plan_to_json(trip_plan: TripPlan) -> str:
    return trip_plan.model_dump_json(indent=2)
