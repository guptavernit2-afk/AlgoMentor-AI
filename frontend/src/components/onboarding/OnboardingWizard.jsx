/**
 * OnboardingWizard.jsx
 *
 * Root controller for the 4-step onboarding flow.
 * Owns all wizard state and renders the active step component.
 *
 * Commit #2 — Profile Persistence Integration
 *   • On mount: GET /api/users/{userId}/profile
 *     - 200 → populate form with saved data
 *     - 404 → keep defaults (first-time user)
 *     - other → show friendly error, keep defaults
 *   • On confirm: PUT /api/users/{userId}/profile
 *     - 200 → show success banner
 *     - 422/400 → show validation error
 *     - 503 → show backend unavailable message
 *     - network → show connection error
 */

import { useState, useEffect } from "react";
import StepProfile from "./StepProfile";
import StepLearning from "./StepLearning";
import StepSchedule from "./StepSchedule";
import StepReview from "./StepReview";
import {
  getProfile,
  saveProfile,
  getWeeklySchedule,
  saveWeeklySchedule,
  DEMO_USER_ID,
} from "../../services/api";
import "./onboarding.css";

// ─── Default wizard state ───────────────────────────────────────────────────
// Mirrors backend: StudentProfile + WeeklySchedule

const WEEKDAYS = [
  "Monday",
  "Tuesday",
  "Wednesday",
  "Thursday",
  "Friday",
  "Saturday",
  "Sunday",
];

function buildDefaultSchedule() {
  return WEEKDAYS.map((day) => ({
    day,
    is_free_day: false,
    classes: [],
  }));
}

const INITIAL_STATE = {
  // ── StudentProfile fields ──────────────────────────────
  name: "",
  goal: "Placement Prep",
  preferred_study_time: "Evening",
  minimum_daily_minutes: 30,
  maximum_daily_minutes: 120,

  // ── Learning profile ───────────────────────────────────
  current_topic: "",
  // comma-separated raw strings; split to arrays on confirm
  completed_topics_raw: "",
  weak_concepts_raw: "",

  // ── WeeklySchedule ─────────────────────────────────────
  days: buildDefaultSchedule(),
};

const STEP_LABELS = [
  "Basic Profile",
  "Learning Profile",
  "Weekly Schedule",
  "Review",
];

// ─── Error → human-readable message ────────────────────────────────────────

function toUserMessage(error, context) {
  const status = error?.status;
  if (status === 404) return null; // expected — first-time user, not an error
  if (status === 422 || status === 400) {
    return `Validation error: ${error.message.replace(/^API Error \d+: /, "")}`;
  }
  if (status === 503) {
    return "Backend is temporarily unavailable. Please try again in a moment.";
  }
  if (!navigator.onLine || error.message?.includes("fetch")) {
    return "Cannot reach the server. Check your internet connection.";
  }
  return `Something went wrong${context ? ` while ${context}` : ""}. Please try again.`;
}

// ─── Profile API ↔ Wizard state bridge ─────────────────────────────────────

/** Map a backend StudentProfile object onto the wizard's flat state. */
function profileToWizardState(profile) {
  return {
    name: profile.name ?? "",
    goal: profile.goal ?? "Placement Prep",
    preferred_study_time: profile.preferred_study_time ?? "Evening",
    minimum_daily_minutes: profile.minimum_daily_minutes ?? 30,
    maximum_daily_minutes: profile.maximum_daily_minutes ?? 120,
    current_topic: profile.current_topic ?? "",
    completed_topics_raw: (profile.completed_topics ?? []).join(", "),
    weak_concepts_raw: (profile.weak_concepts ?? []).join(", "),
  };
}

/** Build the backend StudentProfile payload from the wizard's flat state. */
function wizardStateToProfile(data) {
  return {
    name: data.name.trim(),
    goal: data.goal,
    preferred_study_time: data.preferred_study_time,
    minimum_daily_minutes: Number(data.minimum_daily_minutes),
    maximum_daily_minutes: Number(data.maximum_daily_minutes),
    current_topic: data.current_topic.trim(),
    completed_topics: data.completed_topics_raw
      .split(",")
      .map((s) => s.trim())
      .filter(Boolean),
    weak_concepts: data.weak_concepts_raw
      .split(",")
      .map((s) => s.trim())
      .filter(Boolean),
  };
}

// ─── Component ──────────────────────────────────────────────────────────────

export default function OnboardingWizard() {
  const [step, setStep] = useState(0); // 0-indexed
  const [data, setData] = useState(INITIAL_STATE);

  // ── Async UI states ──────────────────────────────────────────────────────
  const [isLoadingProfile, setIsLoadingProfile] = useState(true);
  const [isSavingProfile, setIsSavingProfile] = useState(false);
  const [loadError, setLoadError] = useState(null);   // friendly string | null
  const [saveError, setSaveError] = useState(null);   // friendly string | null
  const [saveSuccess, setSaveSuccess] = useState(false);

  // ── Load existing data on mount ─────────────────────────────────────────
  useEffect(() => {
    let cancelled = false;

    async function loadData() {
      setIsLoadingProfile(true);
      setLoadError(null);
      
      // Load Profile
      try {
        const res = await getProfile(DEMO_USER_ID);
        if (!cancelled && res?.profile) {
          setData((prev) => ({
            ...prev,
            ...profileToWizardState(res.profile),
          }));
          console.log("[AlgoMentor] Loaded profile from backend:", res.profile);
        }
      } catch (err) {
        if (cancelled) return;
        if (err?.status === 404) {
          console.log("[AlgoMentor] No existing profile — using defaults.");
        } else {
          setLoadError(toUserMessage(err, "loading your profile"));
          console.warn("[AlgoMentor] Profile load failed:", err.message);
        }
      }

      // Load Schedule
      try {
        const res = await getWeeklySchedule(DEMO_USER_ID);
        if (!cancelled && res?.schedule?.days) {
          setData((prev) => ({
            ...prev,
            days: res.schedule.days,
          }));
          console.log("[AlgoMentor] Loaded schedule from backend:", res.schedule);
        }
      } catch (err) {
        if (cancelled) return;
        if (err?.status === 404) {
          console.log("[AlgoMentor] No existing schedule — using defaults.");
        } else {
          setLoadError((prev) =>
            prev
              ? `${prev} | ${toUserMessage(err, "loading your schedule")}`
              : toUserMessage(err, "loading your schedule")
          );
          console.warn("[AlgoMentor] Schedule load failed:", err.message);
        }
      }

      if (!cancelled) setIsLoadingProfile(false);
    }

    loadData();
    return () => {
      cancelled = true;
    };
  }, []);

  // ── Partial-update helper ────────────────────────────────────────────────
  function update(patch) {
    setData((prev) => ({ ...prev, ...patch }));
  }

  function next() {
    setStep((s) => Math.min(s + 1, STEP_LABELS.length - 1));
  }

  function back() {
    setStep((s) => Math.max(s - 1, 0));
  }

  // ── Save data on confirm ─────────────────────────────────────────────────
  async function handleConfirm() {
    if (isSavingProfile) return;

    setSaveError(null);
    setSaveSuccess(false);
    setIsSavingProfile(true);

    const profile = wizardStateToProfile(data);
    const schedule = { days: data.days };

    try {
      await saveProfile(DEMO_USER_ID, profile);
      await saveWeeklySchedule(DEMO_USER_ID, schedule);
      
      setSaveSuccess(true);
      console.log("[AlgoMentor] Profile and schedule saved successfully");
    } catch (err) {
      const msg = toUserMessage(err, "saving your setup");
      setSaveError(msg);
      console.error("[AlgoMentor] Save failed:", err.message);
    } finally {
      setIsSavingProfile(false);
    }
  }

  const totalSteps = STEP_LABELS.length;

  // ── Loading skeleton (profile fetch in progress) ─────────────────────────
  if (isLoadingProfile) {
    return (
      <div className="ob-root">
        <nav className="top-nav">
          <div className="nav-logo">
            <span className="nav-logo-icon">⬡</span>
            <span className="nav-logo-text">
              AlgoMentor<span className="nav-logo-accent"> AI</span>
            </span>
            <span className="prototype-badge">SETUP</span>
          </div>
        </nav>
        <main className="ob-shell">
          <div className="ob-card ob-loading-card">
            <div className="ob-loading-spinner" />
            <p className="ob-loading-text">Loading your setup…</p>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="ob-root">
      {/* ── Top navigation bar (matches dashboard) ── */}
      <nav className="top-nav">
        <div className="nav-logo">
          <span className="nav-logo-icon">⬡</span>
          <span className="nav-logo-text">
            AlgoMentor<span className="nav-logo-accent"> AI</span>
          </span>
          <span className="prototype-badge">SETUP</span>
        </div>

        {/* Step progress pills */}
        <div className="ob-step-pills">
          {STEP_LABELS.map((label, i) => (
            <div
              key={label}
              className={`ob-step-pill ${
                i === step
                  ? "ob-pill-active"
                  : i < step
                  ? "ob-pill-done"
                  : "ob-pill-future"
              }`}
            >
              <span className="ob-pill-num">{i + 1}</span>
              <span className="ob-pill-label">{label}</span>
            </div>
          ))}
        </div>

        <div className="ob-step-counter">
          Step {step + 1} of {totalSteps}
        </div>
      </nav>

      {/* ── Wizard body ── */}
      <main className="ob-shell">

        {/* ── Load error banner (non-fatal: form still usable) ── */}
        {loadError && (
          <div className="ob-banner ob-banner-warn" role="alert">
            <span className="ob-banner-icon">⚠️</span>
            <span className="ob-banner-text">{loadError}</span>
            <span className="ob-banner-sub">
              Using default values — your changes will still save normally.
            </span>
          </div>
        )}

        {/* Progress bar */}
        <div className="ob-progress-track">
          <div
            className="ob-progress-fill"
            style={{ width: `${((step + 1) / totalSteps) * 100}%` }}
          />
        </div>

        {/* Active step */}
        <div className="ob-card">
          {step === 0 && (
            <StepProfile data={data} update={update} onNext={next} />
          )}
          {step === 1 && (
            <StepLearning
              data={data}
              update={update}
              onNext={next}
              onBack={back}
            />
          )}
          {step === 2 && (
            <StepSchedule
              data={data}
              update={update}
              onNext={next}
              onBack={back}
            />
          )}
          {step === 3 && (
            <StepReview
              data={data}
              onBack={back}
              onConfirm={handleConfirm}
              isSaving={isSavingProfile}
              saveError={saveError}
              saveSuccess={saveSuccess}
            />
          )}
        </div>
      </main>
    </div>
  );
}



