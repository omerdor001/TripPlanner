from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse

from attraction_finder import AttractionGenerationError, get_city_attractions
from itinerary_builder import build_day_plans
from models import DayPlan, Language, TripPlan, TripPlanRequest
from output_formatter import trip_plan_to_markdown

app = FastAPI(title="European City Trip Planner")

DISCLAIMER_TEXT: dict[Language, str] = {
    "en": "unverified — confirm hours/prices before travel",
    "he": "לא מאומת — יש לוודא שעות ומחירים לפני הנסיעה",
}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/api/trip-plan")
def create_trip_plan(request: TripPlanRequest, format: str = Query("json", pattern="^(json|markdown)$")):
    if not request.cities:
        raise HTTPException(status_code=400, detail="At least one city is required.")

    day_plans: list[DayPlan] = []
    general_tips: list[str] = []

    for city_request in request.cities:
        try:
            city_set = get_city_attractions(
                city=city_request.name,
                days=city_request.days,
                interests=request.interests,
                budget_level=request.budget_level,
                language=request.language,
            )
        except AttractionGenerationError as error:
            raise HTTPException(status_code=502, detail=str(error)) from error

        day_plans.extend(
            build_day_plans(
                city_request.name,
                city_request.days,
                city_set.attractions,
                language=request.language,
            )
        )
        general_tips.extend(city_set.general_tips)

    trip_plan = TripPlan(
        cities=[c.name for c in request.cities],
        total_days=sum(c.days for c in request.cities),
        interests=request.interests,
        budget_level=request.budget_level,
        day_plans=day_plans,
        general_tips=general_tips,
        disclaimer=DISCLAIMER_TEXT[request.language],
        language=request.language,
    )

    if format == "markdown":
        return PlainTextResponse(trip_plan_to_markdown(trip_plan))
    return trip_plan
