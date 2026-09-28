export type Category =
  | "art"
  | "history"
  | "food"
  | "nightlife"
  | "nature"
  | "shopping"
  | "other";

export interface Attraction {
  name: string;
  description: string;
  category: Category;
  neighborhood: string | null;
  address: string | null;
  maps_url: string;
  estimated_duration_minutes: number;
  approximate_cost_eur: number | null;
  cost_notes: string | null;
  best_time_to_visit: string | null;
  opening_hours: string | null;
  booking_recommended: boolean;
  unverified: boolean;
}

export interface DayPlan {
  day_number: number;
  city: string;
  attractions: Attraction[];
  getting_around_tip: string | null;
  notes: string | null;
}

export interface TripPlan {
  cities: string[];
  total_days: number;
  interests: string[];
  budget_level: string | null;
  day_plans: DayPlan[];
  general_tips: string[];
  disclaimer: string;
  language: "en" | "he";
}

export interface CityRequest {
  name: string;
  days: number;
}

export interface TripPlanRequest {
  cities: CityRequest[];
  interests: string[];
  budget_level: string | null;
  language: "en" | "he";
}
