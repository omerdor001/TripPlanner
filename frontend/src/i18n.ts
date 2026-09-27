export type Lang = "en" | "he";

export const RTL_LANGS: Lang[] = ["he"];

export function dirOf(lang: Lang): "rtl" | "ltr" {
  return RTL_LANGS.includes(lang) ? "rtl" : "ltr";
}

interface Translation {
  appTitle: string;
  appSubtitle: string;
  citiesLabel: string;
  cityPlaceholder: string;
  daySingular: string;
  dayPlural: string;
  addCity: string;
  addCityLimit: (max: number) => string;
  removeCityAria: (name: string) => string;
  interestsLabel: string;
  interestsHint: string;
  budgetLabel: string;
  submit: string;
  submitting: string;
  submitHint: string;
  errorNoCities: string;
  placeholderIdle: string;
  loadingTitle: string;
  loadingSubtext: string;
  updatingTitle: string;
  tryAgain: string;
  exportPdf: string;
  generalTips: string;
  unverifiedBadge: string;
  bookingRecommended: string;
  bestTime: string;
  hours: string;
  costUnknown: string;
  dayTab: (n: number) => string;
  genericError: string;
  interestOptions: Record<string, string>;
  budgetOptions: Record<string, string>;
  categoryLabels: Record<string, string>;
}

export const translations: Record<Lang, Translation> = {
  en: {
    appTitle: "🧭 European City Trip Planner",
    appSubtitle: "Tell us where you're headed and we'll build a day-by-day itinerary.",
    citiesLabel: "Cities",
    cityPlaceholder: "e.g. Paris",
    daySingular: "day",
    dayPlural: "days",
    addCity: "+ Add another city",
    addCityLimit: (max) => `Up to ${max} cities per trip`,
    removeCityAria: (name) => `Remove ${name || "city"}`,
    interestsLabel: "Interests",
    interestsHint: "Leave blank for a well-rounded mix of top sights.",
    budgetLabel: "Budget level",
    submit: "Plan my trip",
    submitting: "Planning your trip…",
    submitHint: "Generating an itinerary calls Claude live and can take up to ~30 seconds per city.",
    errorNoCities: "Add at least one city.",
    placeholderIdle: "Fill in the form to generate your itinerary.",
    loadingTitle: "Planning your trip…",
    loadingSubtext: "Claude is researching attractions — this can take up to ~30 seconds per city.",
    updatingTitle: "Updating your itinerary…",
    tryAgain: "Try again",
    exportPdf: "Export PDF",
    generalTips: "General tips",
    unverifiedBadge: "unverified — confirm before travel",
    bookingRecommended: "⚠ Booking recommended in advance",
    bestTime: "Best time",
    hours: "Hours",
    costUnknown: "cost unknown",
    dayTab: (n) => `Day ${n}`,
    genericError: "Something went wrong. Please try again.",
    interestOptions: {
      art: "Art", food: "Food", history: "History",
      nightlife: "Nightlife", nature: "Nature", shopping: "Shopping",
    },
    budgetOptions: { budget: "Budget", "mid-range": "Mid-range", luxury: "Luxury" },
    categoryLabels: {
      art: "Art", history: "History", food: "Food",
      nightlife: "Nightlife", nature: "Nature", shopping: "Shopping", other: "Other",
    },
  },
  he: {
    appTitle: "🧭 מתכנן טיולים לערי אירופה",
    appSubtitle: "ספרו לנו לאן אתם נוסעים ונבנה עבורכם מסלול יום־יומי.",
    citiesLabel: "ערים",
    cityPlaceholder: "לדוגמה: פריז",
    daySingular: "יום",
    dayPlural: "ימים",
    addCity: "+ הוספת עיר נוספת",
    addCityLimit: (max) => `עד ${max} ערים בטיול`,
    removeCityAria: (name) => `הסרת ${name || "עיר"}`,
    interestsLabel: "תחומי עניין",
    interestsHint: "השאירו ריק לתמהיל מאוזן של האתרים המובילים.",
    budgetLabel: "רמת תקציב",
    submit: "תכננו לי טיול",
    submitting: "מתכננים את הטיול שלך…",
    submitHint: "יצירת מסלול מבצעת קריאה חיה ל-Claude ועשויה לקחת עד כ-30 שניות לכל עיר.",
    errorNoCities: "הוסיפו עיר אחת לפחות.",
    placeholderIdle: "מלאו את הטופס כדי ליצור את המסלול שלכם.",
    loadingTitle: "מתכננים את הטיול שלך…",
    loadingSubtext: "Claude חוקר אתרים כרגע — זה עשוי לקחת עד כ-30 שניות לכל עיר.",
    updatingTitle: "מעדכנים את המסלול שלך…",
    tryAgain: "נסו שוב",
    exportPdf: "ייצוא ל-PDF",
    generalTips: "טיפים כלליים",
    unverifiedBadge: "לא מאומת — יש לוודא לפני הנסיעה",
    bookingRecommended: "⚠ מומלץ להזמין מקום מראש",
    bestTime: "זמן מומלץ",
    hours: "שעות פתיחה",
    costUnknown: "העלות לא ידועה",
    dayTab: (n) => `יום ${n}`,
    genericError: "משהו השתבש. נסו שוב.",
    interestOptions: {
      art: "אמנות", food: "אוכל", history: "היסטוריה",
      nightlife: "חיי לילה", nature: "טבע", shopping: "קניות",
    },
    budgetOptions: { budget: "חסכוני", "mid-range": "בינוני", luxury: "יוקרתי" },
    categoryLabels: {
      art: "אמנות", history: "היסטוריה", food: "אוכל",
      nightlife: "חיי לילה", nature: "טבע", shopping: "קניות", other: "אחר",
    },
  },
};
