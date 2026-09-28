# European City Trip Planner

A web app that generates a curated, day-by-day itinerary for European city
trips using the Claude API. Enter one or more cities, trip length, interests,
and a budget level, and it returns attractions grouped into a walkable
day-by-day plan with practical tips.

**All attraction data is LLM-generated and unverified.** Every attraction and
the overall trip plan is labeled `unverified — confirm hours/prices before
travel`. There is no live search, maps, or booking integration — hours,
prices, and opening times are the model's best-effort estimate and can be
outdated or wrong.

**Live demo:** [https://trip-planner-sooty-mu.vercel.app/](https://trip-planner-sooty-mu.vercel.app/)

## Architecture

- **Backend** — FastAPI (Python). One Claude API call per city generates a
  pool of attractions; a itinerary builder then groups them into day plans by
  neighborhood (LLM-assigned, not real geo-distance) to keep each day
  walkable. Output is validated against Pydantic schemas before it's ever
  returned to the frontend.
- **Frontend** — React + Vite (TypeScript). A form for cities/interests/
  budget, and a day-by-day itinerary view with per-city and per-day tabs.
- **Language** — an EN/עברית switcher in the top corner. Selecting Hebrew
  sends `language: "he"` to the backend, which instructs Claude to generate
  the itinerary content (names, descriptions, tips) in Hebrew and switches
  the UI to a right-to-left layout with Hebrew fonts. The `category` field
  stays a fixed English enum regardless of language (it drives styling), and
  is translated only for display.

```
trip_planner/
  backend/     FastAPI app, Claude integration, schemas, itinerary logic
  frontend/    React + Vite UI
  examples/    Example output (Vienna, 3 days) as JSON and Markdown
```

## Setup

### Backend

```bash
cd backend
python -m venv .venv
.venv/Scripts/activate        # Windows; use `source .venv/bin/activate` on macOS/Linux
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` and set your Anthropic API key:

```
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_MODEL=claude-sonnet-5
```

Run the API server:

```bash
uvicorn main:app --reload
```

This serves on `http://localhost:8000`. Check `http://localhost:8000/api/health`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

This serves on `http://localhost:5173` and proxies `/api/*` requests to the
backend on port 8000 (see `vite.config.ts`). Open `http://localhost:5173` in
a browser, fill in the form, and submit.

## API

`POST /api/trip-plan`

Request body:

```json
{
  "cities": [{ "name": "Vienna", "days": 3 }],
  "interests": ["art", "food"],
  "budget_level": "mid-range",
  "language": "en"
}
```

`language` is `"en"` (default) or `"he"`.

Add `?format=markdown` to get a rendered Markdown itinerary back instead of
JSON. Multiple cities are supported — each is planned with its own Claude API
call and appended to the trip.

Malformed model output is retried once automatically; if it still doesn't
validate against the schema, the endpoint returns `502` with a description of
the failure. Claude API errors (rate limits, billing, etc.) also return `502`
rather than crashing.

## Example output

See `examples/vienna_3days.json` and `examples/vienna_3days.md` for a real,
generated 3-day Vienna itinerary (art + food interests, mid-range budget).

## Notes / scope

- No external APIs (search, maps, weather, booking) are integrated — day
  grouping is done by the LLM reasoning over neighborhood names, not real
  geo-distance.
- No CLI — this is a web app only.
- Data is not cached or persisted; each request calls the Claude API fresh.
