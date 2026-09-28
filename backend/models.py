from typing import List, Literal, Optional
from urllib.parse import quote_plus

from pydantic import BaseModel, Field, computed_field

Category = Literal[
    "art", "history", "food", "nightlife", "nature", "shopping", "other"
]

Language = Literal["en", "he"]


class Attraction(BaseModel):
    name: str
    description: str
    category: Category
    neighborhood: Optional[str] = None
    address: Optional[str] = Field(
        default=None,
        description=(
            "Full street address of the place as written locally, in Latin "
            "script regardless of response language, including postal code, "
            "city and country, e.g. 'Heldenplatz, 1010 Vienna, Austria'."
        ),
    )
    estimated_duration_minutes: int
    approximate_cost_eur: Optional[float] = None
    cost_notes: Optional[str] = None
    best_time_to_visit: Optional[str] = None
    opening_hours: Optional[str] = None
    booking_recommended: bool = False
    unverified: bool = True

    # Serialization-only: excluded from the LLM's JSON schema, included in API output.
    @computed_field
    @property
    def maps_url(self) -> str:
        """Google Maps search link built from the place name and its address."""
        place = self.name
        if self.address:
            place = f"{self.name}, {self.address}"
        elif self.neighborhood:
            place = f"{self.name}, {self.neighborhood}"
        return f"https://www.google.com/maps/search/?api=1&query={quote_plus(place)}"


class DayPlan(BaseModel):
    day_number: int
    city: str
    attractions: List[Attraction]
    getting_around_tip: Optional[str] = None
    notes: Optional[str] = None


class TripPlan(BaseModel):
    cities: List[str]
    total_days: int
    interests: List[str] = Field(default_factory=list)
    budget_level: Optional[str] = None
    day_plans: List[DayPlan]
    general_tips: List[str] = Field(default_factory=list)
    disclaimer: str = "unverified — confirm hours/prices before travel"
    language: Language = "en"


class CityRequest(BaseModel):
    name: str
    days: int


class TripPlanRequest(BaseModel):
    cities: List[CityRequest]
    interests: List[str] = Field(default_factory=list)
    budget_level: Optional[str] = None
    language: Language = "en"


class CityAttractionSet(BaseModel):
    """Raw LLM output for a single city, before day-grouping."""

    city: str
    resolved_city: str = Field(
        description=(
            "The real, specific city and country this refers to, written in "
            "English regardless of what script/language the input city name "
            "was given in, e.g. 'Vienna, Austria'. Identify this first, "
            "before generating attractions, so every attraction below is "
            "guaranteed to be from this exact city."
        )
    )
    attractions: List[Attraction]
    general_tips: List[str] = Field(default_factory=list)
