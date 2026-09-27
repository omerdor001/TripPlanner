import type { TripPlan, TripPlanRequest } from "./types";

export class TripPlanApiError extends Error {}

export async function createTripPlan(request: TripPlanRequest): Promise<TripPlan> {
  const response = await fetch("/api/trip-plan", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const body = await response.json().catch(() => null);
    const detail = body?.detail ?? `Request failed with status ${response.status}`;
    throw new TripPlanApiError(detail);
  }

  return response.json();
}
