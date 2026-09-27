import { useState } from "react";
import TripForm from "./components/TripForm";
import ItineraryView from "./components/ItineraryView";
import { createTripPlan, TripPlanApiError } from "./api";
import { dirOf, translations, type Lang } from "./i18n";
import type { TripPlan, TripPlanRequest } from "./types";

type Status = "idle" | "loading" | "error" | "success";

function App() {
  const [lang, setLang] = useState<Lang>("en");
  const [status, setStatus] = useState<Status>("idle");
  const [tripPlan, setTripPlan] = useState<TripPlan | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [lastRequest, setLastRequest] = useState<TripPlanRequest | null>(null);

  const t = translations[lang];

  async function runRequest(request: TripPlanRequest) {
    setLastRequest(request);
    setStatus("loading");
    setErrorMessage(null);
    try {
      const plan = await createTripPlan(request);
      setTripPlan(plan);
      setStatus("success");
    } catch (err) {
      const message = err instanceof TripPlanApiError ? err.message : t.genericError;
      setErrorMessage(message);
      setStatus("error");
    }
  }

  function handleRetry() {
    if (lastRequest) runRequest(lastRequest);
  }

  const showingStalePlan = tripPlan !== null && (status === "loading" || status === "error");

  return (
    <div className="app-shell" dir={dirOf(lang)} lang={lang}>
      <div className="lang-switcher">
        <button
          className={`lang-btn ${lang === "en" ? "lang-btn-active" : ""}`}
          onClick={() => setLang("en")}
        >
          EN
        </button>
        <button
          className={`lang-btn ${lang === "he" ? "lang-btn-active" : ""}`}
          onClick={() => setLang("he")}
        >
          עברית
        </button>
      </div>

      <header className="app-header">
        <h1>{t.appTitle}</h1>
        <p className="app-subtitle">{t.appSubtitle}</p>
      </header>

      <main className="app-main">
        <aside className="form-panel">
          <TripForm onSubmit={runRequest} isLoading={status === "loading"} lang={lang} />
        </aside>

        <section className="results-panel">
          {status === "idle" && (
            <div className="placeholder">
              <p>{t.placeholderIdle}</p>
            </div>
          )}

          {status === "loading" && !tripPlan && (
            <div className="placeholder">
              <div className="spinner" />
              <p>{t.loadingTitle}</p>
              <p className="placeholder-subtext">{t.loadingSubtext}</p>
            </div>
          )}

          {status === "error" && !tripPlan && (
            <div className="placeholder placeholder-error">
              <p>⚠ {errorMessage}</p>
              <button className="retry-btn" onClick={handleRetry}>
                {t.tryAgain}
              </button>
            </div>
          )}

          {status === "error" && tripPlan && (
            <div className="error-banner">
              <span>⚠ {errorMessage}</span>
              <button className="retry-btn" onClick={handleRetry}>
                {t.tryAgain}
              </button>
            </div>
          )}

          {tripPlan && (
            <div className={showingStalePlan ? "results-stale" : undefined}>
              {status === "loading" && (
                <div className="results-loading-overlay">
                  <div className="spinner" />
                  <p>{t.updatingTitle}</p>
                </div>
              )}
              <ItineraryView tripPlan={tripPlan} lang={tripPlan.language} />
            </div>
          )}
        </section>
      </main>
    </div>
  );
}

export default App;
