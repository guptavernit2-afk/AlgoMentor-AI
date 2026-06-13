/**
 * OnboardingWizard.jsx
 *
 * Root controller for the 4-step onboarding flow.
 * Owns all wizard state and renders the active step component.
 * State shape is designed to match StudentProfile + WeeklySchedule
 * backend models for zero-friction future API integration.
 */

import { useState } from "react";
import StepProfile from "./StepProfile";
import StepLearning from "./StepLearning";
import StepSchedule from "./StepSchedule";
import StepReview from "./StepReview";
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

export default function OnboardingWizard() {
  const [step, setStep] = useState(0); // 0-indexed
  const [data, setData] = useState(INITIAL_STATE);

  // Partial-update helper — keeps all other keys intact
  function update(patch) {
    setData((prev) => ({ ...prev, ...patch }));
  }

  function next() {
    setStep((s) => Math.min(s + 1, STEP_LABELS.length - 1));
  }

  function back() {
    setStep((s) => Math.max(s - 1, 0));
  }

  function handleConfirm() {
    // Build the final payload matching backend models
    const payload = {
      profile: {
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
      },
      weekly_schedule: {
        days: data.days,
      },
    };

    // Phase 1 — local only. API call goes here in Commit #2.
    console.log("[AlgoMentor] Onboarding payload:", payload);
  }

  const totalSteps = STEP_LABELS.length;

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
            <StepReview data={data} onBack={back} onConfirm={handleConfirm} />
          )}
        </div>
      </main>
    </div>
  );
}
