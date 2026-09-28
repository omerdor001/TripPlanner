import { useMemo, useState } from "react";
import type { DayPlan, TripPlan } from "../types";
import { dirOf, translations, type Lang } from "../i18n";
import AttractionCard from "./AttractionCard";

function groupByCity(dayPlans: DayPlan[]): Map<string, DayPlan[]> {
  const map = new Map<string, DayPlan[]>();
  for (const day of dayPlans) {
    if (!map.has(day.city)) map.set(day.city, []);
    map.get(day.city)!.push(day);
  }
  return map;
}

export default function ItineraryView({ tripPlan, lang }: { tripPlan: TripPlan; lang: Lang }) {
  const t = translations[lang];
  const byCity = useMemo(() => groupByCity(tripPlan.day_plans), [tripPlan]);
  const cities = useMemo(() => Array.from(byCity.keys()), [byCity]);
  const [selectedCity, setActiveCity] = useState(cities[0]);
  const [activeDay, setActiveDay] = useState(1);

  // A new plan can use different city names (e.g. "Vienna" -> "וינה"), so the
  // remembered selection may no longer exist — fall back to the first city.
  const activeCity = byCity.has(selectedCity) ? selectedCity : cities[0];
  const currentCityDays = byCity.get(activeCity) ?? [];
  const currentDay = currentCityDays.find((d) => d.day_number === activeDay) ?? currentCityDays[0];

  function selectCity(city: string) {
    setActiveCity(city);
    setActiveDay(1);
  }

  return (
    <div className="itinerary-view" dir={dirOf(lang)} lang={lang}>
      <div className="itinerary-header">
        <h2>
          {t.tripTitle(tripPlan.total_days, tripPlan.cities)}
        </h2>
        <button className="export-btn" onClick={() => window.print()}>
          {t.exportPdf}
        </button>
      </div>
      <p className="disclaimer">{tripPlan.disclaimer}</p>

      {/* Interactive tabbed view — screen only. Printing shows every day at once instead. */}
      <div className="screen-only">
        {cities.length > 1 && (
          <div className="tab-row city-tabs">
            {cities.map((city) => (
              <button
                key={city}
                className={`tab ${city === activeCity ? "tab-active" : ""}`}
                onClick={() => selectCity(city)}
              >
                {city}
              </button>
            ))}
          </div>
        )}

        <div className="tab-row day-tabs">
          {currentCityDays.map((day) => (
            <button
              key={day.day_number}
              className={`tab ${day.day_number === activeDay ? "tab-active" : ""}`}
              onClick={() => setActiveDay(day.day_number)}
            >
              {t.dayTab(day.day_number)}
            </button>
          ))}
        </div>

        {currentDay && (
          <div className="day-content">
            {currentDay.getting_around_tip && (
              <p className="getting-around-tip">🚶 {currentDay.getting_around_tip}</p>
            )}
            <div className="attraction-list">
              {currentDay.attractions.map((attraction, i) => (
                <AttractionCard attraction={attraction} lang={lang} key={i} />
              ))}
            </div>
            {currentDay.notes && <p className="day-notes">{currentDay.notes}</p>}
          </div>
        )}
      </div>

      {/* Full day-by-day listing — print only (hidden on screen). */}
      <div className="print-only">
        {tripPlan.day_plans.map((day, i) => (
          <div className="print-day" key={i}>
            <h3>
              {day.city} — {t.dayTab(day.day_number)}
            </h3>
            {day.getting_around_tip && <p className="getting-around-tip">🚶 {day.getting_around_tip}</p>}
            <div className="attraction-list">
              {day.attractions.map((attraction, j) => (
                <AttractionCard attraction={attraction} lang={lang} key={j} />
              ))}
            </div>
            {day.notes && <p className="day-notes">{day.notes}</p>}
          </div>
        ))}
      </div>

      {tripPlan.general_tips.length > 0 && (
        <div className="general-tips">
          <h3>{t.generalTips}</h3>
          <ul>
            {tripPlan.general_tips.map((tip, i) => (
              <li key={i}>{tip}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
