import { useState } from "react";
import type { CityRequest, TripPlanRequest } from "../types";
import { translations, type Lang } from "../i18n";

const INTEREST_OPTIONS = ["art", "food", "history", "nightlife", "nature", "shopping"];
const BUDGET_OPTIONS = ["budget", "mid-range", "luxury"];
const POPULAR_CITIES = [
  "Vienna", "Paris", "Rome", "Prague", "Barcelona", "Amsterdam", "Berlin",
  "Budapest", "Lisbon", "Florence", "Venice", "Madrid", "London", "Munich",
  "Copenhagen", "Dublin", "Krakow", "Athens",
];
const MAX_CITIES = 6;
const MIN_DAYS = 1;
const MAX_DAYS = 14;

interface TripFormProps {
  onSubmit: (request: TripPlanRequest) => void;
  isLoading: boolean;
  lang: Lang;
}

function clampDays(value: number): number {
  if (!Number.isFinite(value) || value < MIN_DAYS) return MIN_DAYS;
  return Math.min(MAX_DAYS, Math.round(value));
}

export default function TripForm({ onSubmit, isLoading, lang }: TripFormProps) {
  const t = translations[lang];
  const [cities, setCities] = useState<CityRequest[]>([{ name: "Vienna", days: 3 }]);
  const [interests, setInterests] = useState<Set<string>>(new Set());
  const [budgetLevel, setBudgetLevel] = useState<string>("mid-range");
  const [error, setError] = useState<string | null>(null);
  const [triedSubmit, setTriedSubmit] = useState(false);

  function updateCity(index: number, patch: Partial<CityRequest>) {
    setCities((prev) => prev.map((c, i) => (i === index ? { ...c, ...patch } : c)));
  }

  function addCity() {
    if (cities.length >= MAX_CITIES) return;
    setCities((prev) => [...prev, { name: "", days: 2 }]);
  }

  function removeCity(index: number) {
    setCities((prev) => prev.filter((_, i) => i !== index));
  }

  function toggleInterest(interest: string) {
    setInterests((prev) => {
      const next = new Set(prev);
      if (next.has(interest)) next.delete(interest);
      else next.add(interest);
      return next;
    });
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setTriedSubmit(true);
    const trimmed = cities
      .map((c) => ({ name: c.name.trim(), days: clampDays(Number(c.days)) }))
      .filter((c) => c.name.length > 0);

    if (trimmed.length === 0) {
      setError(t.errorNoCities);
      return;
    }
    setError(null);
    onSubmit({
      cities: trimmed,
      interests: Array.from(interests),
      budget_level: budgetLevel,
      language: lang,
    });
  }

  return (
    <form className="trip-form" onSubmit={handleSubmit}>
      <div className="field-group">
        <label className="field-label">{t.citiesLabel}</label>
        {cities.map((city, index) => {
          const isInvalid = triedSubmit && city.name.trim().length === 0;
          return (
            <div className="city-row" key={index}>
              <input
                type="text"
                placeholder={t.cityPlaceholder}
                list="city-suggestions"
                autoFocus={index === 0}
                className={isInvalid ? "input-invalid" : ""}
                value={city.name}
                onChange={(e) => updateCity(index, { name: e.target.value })}
              />
              <input
                type="number"
                min={MIN_DAYS}
                max={MAX_DAYS}
                value={city.days}
                onChange={(e) => updateCity(index, { days: Number(e.target.value) })}
                onBlur={(e) => updateCity(index, { days: clampDays(Number(e.target.value)) })}
              />
              <span className="days-label">{city.days === 1 ? t.daySingular : t.dayPlural}</span>
              {cities.length > 1 && (
                <button
                  type="button"
                  className="remove-city-btn"
                  onClick={() => removeCity(index)}
                  aria-label={t.removeCityAria(city.name)}
                >
                  ×
                </button>
              )}
            </div>
          );
        })}
        <datalist id="city-suggestions">
          {POPULAR_CITIES.map((c) => (
            <option key={c} value={c} />
          ))}
        </datalist>
        <button
          type="button"
          className="add-city-btn"
          onClick={addCity}
          disabled={cities.length >= MAX_CITIES}
          title={cities.length >= MAX_CITIES ? t.addCityLimit(MAX_CITIES) : undefined}
        >
          {t.addCity}
        </button>
      </div>

      <div className="field-group">
        <label className="field-label">{t.interestsLabel}</label>
        <div className="interest-chips">
          {INTEREST_OPTIONS.map((interest) => (
            <button
              type="button"
              key={interest}
              className={`chip ${interests.has(interest) ? "chip-selected" : ""}`}
              onClick={() => toggleInterest(interest)}
            >
              {t.interestOptions[interest]}
            </button>
          ))}
        </div>
        <p className="field-hint">{t.interestsHint}</p>
      </div>

      <div className="field-group">
        <label className="field-label">{t.budgetLabel}</label>
        <select value={budgetLevel} onChange={(e) => setBudgetLevel(e.target.value)}>
          {BUDGET_OPTIONS.map((option) => (
            <option key={option} value={option}>
              {t.budgetOptions[option]}
            </option>
          ))}
        </select>
      </div>

      {error && <p className="form-error">{error}</p>}

      <button type="submit" className="submit-btn" disabled={isLoading}>
        {isLoading ? t.submitting : t.submit}
      </button>
      <p className="field-hint submit-hint">{t.submitHint}</p>
    </form>
  );
}
