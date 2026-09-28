import type { Attraction } from "../types";
import { translations, type Lang } from "../i18n";

function formatCost(attraction: Attraction, costUnknown: string): string {
  if (attraction.approximate_cost_eur != null) {
    const cost = `€${attraction.approximate_cost_eur}`;
    return attraction.cost_notes ? `${cost} (${attraction.cost_notes})` : cost;
  }
  return attraction.cost_notes ?? costUnknown;
}

export default function AttractionCard({ attraction, lang }: { attraction: Attraction; lang: Lang }) {
  const t = translations[lang];
  return (
    <div className="attraction-card">
      <div className="attraction-header">
        <h4>{attraction.name}</h4>
        <span className={`category-badge category-${attraction.category}`}>
          {t.categoryLabels[attraction.category] ?? attraction.category}
        </span>
      </div>
      <p className="attraction-description">{attraction.description}</p>
      <div className="attraction-meta">
        <span>⏱ {t.minutes(attraction.estimated_duration_minutes)}</span>
        <span>💶 {formatCost(attraction, t.costUnknown)}</span>
        {attraction.neighborhood && <span>📍 {attraction.neighborhood}</span>}
      </div>
      {(attraction.best_time_to_visit || attraction.opening_hours || attraction.booking_recommended) && (
        <div className="attraction-tips">
          {attraction.best_time_to_visit && (
            <div>
              {t.bestTime}: {attraction.best_time_to_visit}
            </div>
          )}
          {attraction.opening_hours && (
            <div>
              {t.hours}: {attraction.opening_hours}
            </div>
          )}
          {attraction.booking_recommended && <div>{t.bookingRecommended}</div>}
        </div>
      )}
      {attraction.unverified && <div className="unverified-badge">{t.unverifiedBadge}</div>}
    </div>
  );
}
