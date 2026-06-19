/**
 * DailyOverridePanel.jsx
 *
 * Commit #4 — Daily Override Persistence Integration
 *
 * Provides a self-contained panel that lets the student record a one-day
 * exception to their normal weekly timetable.
 *
 * Load behaviour  (date change)
 *   GET /api/users/{userId}/daily-overrides/{date}
 *   • 200  → populate fields from backend
 *   • 404  → treat as "no override exists"; populate blank defaults silently
 *   • other → show error banner
 *
 * Save behaviour  (Save Override button)
 *   PUT /api/users/{userId}/daily-overrides/{date}
 *   • 200  → show success banner
 *   • error → show error banner (validation detail or generic message)
 *
 * Delete behaviour  (Delete Override button)
 *   DELETE /api/users/{userId}/daily-overrides/{date}
 *   • 200  → clear form, show confirmation banner
 *   • 404  → treat gracefully (already gone), clear form
 *   • other → show error banner
 *
 * Error messages follow the same toUserMessage pattern as OnboardingWizard.
 */

import { useState, useEffect, useCallback } from "react";
import {
  getDailyOverride,
  saveDailyOverride,
  deleteDailyOverride,
  DEMO_USER_ID,
} from "../services/api";
import "./DailyOverridePanel.css";

// ─── Constants matching backend Literal types ─────────────────────────────────

const SITUATIONS = [
  "Normal day",
  "Assignment",
  "Internal exam / Test",
  "Project work",
  "Event / Hackathon",
  "Free day",
];

const ENERGY_LEVELS = ["Low", "Normal", "High"];

// ─── Helpers ──────────────────────────────────────────────────────────────────

/** Returns today's date as a YYYY-MM-DD string in local time. */
function todayISO() {
  const d = new Date();
  const yyyy = d.getFullYear();
  const mm = String(d.getMonth() + 1).padStart(2, "0");
  const dd = String(d.getDate()).padStart(2, "0");
  return `${yyyy}-${mm}-${dd}`;
}

/** Mirror of OnboardingWizard's toUserMessage. */
function toUserMessage(error, context) {
  const status = error?.status;
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

/** Blank defaults — mirrors DailyOverride model defaults. */
const BLANK_OVERRIDE = {
  situation: "Normal day",
  extra_available_minutes: 0,
  energy_level: "Normal",
  note: "",
};

// ─── Component ────────────────────────────────────────────────────────────────

export default function DailyOverridePanel() {
  const [date, setDate] = useState(todayISO());
  const [fields, setFields] = useState(BLANK_OVERRIDE);

  // Async UI states
  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  // Banner states  (null = hidden)
  const [loadError, setLoadError] = useState(null);
  const [saveError, setSaveError] = useState(null);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [deleteError, setDeleteError] = useState(null);
  const [deleteSuccess, setDeleteSuccess] = useState(false);

  // ── Load override whenever the selected date changes ────────────────────────
  const loadOverride = useCallback(async (targetDate) => {
    setIsLoading(true);
    setLoadError(null);
    setSaveError(null);
    setSaveSuccess(false);
    setDeleteError(null);
    setDeleteSuccess(false);

    try {
      const res = await getDailyOverride(DEMO_USER_ID, targetDate);
      if (res?.override) {
        setFields({
          situation: res.override.situation ?? "Normal day",
          extra_available_minutes: res.override.extra_available_minutes ?? 0,
          energy_level: res.override.energy_level ?? "Normal",
          note: res.override.note ?? "",
        });
        console.log("[AlgoMentor] Loaded daily override:", res.override);
      }
    } catch (err) {
      if (err?.status === 404) {
        // Expected — no override for this date
        setFields(BLANK_OVERRIDE);
        console.log("[AlgoMentor] No override for", targetDate, "— using defaults.");
      } else {
        setLoadError(toUserMessage(err, "loading the daily override"));
        setFields(BLANK_OVERRIDE);
        console.warn("[AlgoMentor] Override load failed:", err.message);
      }
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    loadOverride(date);
  }, [date, loadOverride]);

  // ── Field helper ────────────────────────────────────────────────────────────
  function update(patch) {
    setFields((prev) => ({ ...prev, ...patch }));
  }

  // ── Save ─────────────────────────────────────────────────────────────────────
  async function handleSave() {
    if (isSaving || isDeleting) return;

    setSaveError(null);
    setSaveSuccess(false);
    setDeleteError(null);
    setDeleteSuccess(false);
    setIsSaving(true);

    // Build payload matching backend DailyOverride model exactly
    const payload = {
      situation: fields.situation,
      extra_available_minutes: Number(fields.extra_available_minutes),
      energy_level: fields.energy_level,
      note: fields.note.trim() || null,   // backend accepts null for optional field
    };

    try {
      await saveDailyOverride(DEMO_USER_ID, date, payload);
      setSaveSuccess(true);
      console.log("[AlgoMentor] Daily override saved for", date);
    } catch (err) {
      setSaveError(toUserMessage(err, "saving the daily override"));
      console.error("[AlgoMentor] Override save failed:", err.message);
    } finally {
      setIsSaving(false);
    }
  }

  // ── Delete ───────────────────────────────────────────────────────────────────
  async function handleDelete() {
    if (isSaving || isDeleting) return;

    setDeleteError(null);
    setDeleteSuccess(false);
    setSaveError(null);
    setSaveSuccess(false);
    setIsDeleting(true);

    try {
      await deleteDailyOverride(DEMO_USER_ID, date);
      setFields(BLANK_OVERRIDE);
      setDeleteSuccess(true);
      console.log("[AlgoMentor] Daily override deleted for", date);
    } catch (err) {
      if (err?.status === 404) {
        // Already gone — treat gracefully, just clear the form
        setFields(BLANK_OVERRIDE);
        setDeleteSuccess(true);
        console.log("[AlgoMentor] Override not found on delete — clearing form.");
      } else {
        setDeleteError(toUserMessage(err, "deleting the daily override"));
        console.error("[AlgoMentor] Override delete failed:", err.message);
      }
    } finally {
      setIsDeleting(false);
    }
  }

  // ── Render ───────────────────────────────────────────────────────────────────
  const busy = isLoading || isSaving || isDeleting;

  return (
    <section className="do-panel" id="daily-override" aria-label="Daily Override">
      {/* ── Header ── */}
      <div className="section-head">
        <div>
          <p className="eyebrow">Daily Override</p>
          <h2>Today's Check-In</h2>
          <p className="section-helper">
            Override your normal schedule for a specific date · Does not affect your weekly timetable
          </p>
        </div>
        <span className="live-pill">
          <span className="live-dot" />
          Persisted
        </span>
      </div>

      {/* ── Load error banner (non-fatal) ── */}
      {loadError && (
        <div className="do-banner do-banner-warn" role="alert">
          <span className="do-banner-icon">⚠️</span>
          <span className="do-banner-text">{loadError}</span>
          <span className="do-banner-sub">Showing blank defaults — your changes will still save normally.</span>
        </div>
      )}

      {/* ── Save success banner ── */}
      {saveSuccess && (
        <div className="do-banner do-banner-success" role="status">
          <span className="do-banner-icon">✅</span>
          <span className="do-banner-text">Daily override saved successfully.</span>
          <span className="do-banner-sub">AlgoMentor will factor this into today's plan.</span>
        </div>
      )}

      {/* ── Save error banner ── */}
      {saveError && (
        <div className="do-banner do-banner-error" role="alert">
          <span className="do-banner-icon">❌</span>
          <span className="do-banner-text">{saveError}</span>
          <span className="do-banner-sub">Your override was not saved. Please try again.</span>
        </div>
      )}

      {/* ── Delete success banner ── */}
      {deleteSuccess && (
        <div className="do-banner do-banner-success" role="status">
          <span className="do-banner-icon">🗑️</span>
          <span className="do-banner-text">Daily override removed.</span>
          <span className="do-banner-sub">Normal weekly timetable will be used for this date.</span>
        </div>
      )}

      {/* ── Delete error banner ── */}
      {deleteError && (
        <div className="do-banner do-banner-error" role="alert">
          <span className="do-banner-icon">❌</span>
          <span className="do-banner-text">{deleteError}</span>
          <span className="do-banner-sub">Override could not be removed. Please try again.</span>
        </div>
      )}

      {/* ── Form ── */}
      <div className="do-grid">
        {/* Date selector */}
        <div className="setup-card do-card-full">
          <label htmlFor="do-date">
            <span className="setup-icon">📅</span>
            Override Date
          </label>
          <p className="setup-helper">Select the date you want to override</p>
          <input
            id="do-date"
            type="date"
            value={date}
            onChange={(e) => setDate(e.target.value)}
            disabled={busy}
          />
          {isLoading && <span className="do-loading-hint">Loading override…</span>}
        </div>

        {/* Situation selector */}
        <div className="setup-card">
          <label htmlFor="do-situation">
            <span className="setup-icon">📌</span>
            Situation
          </label>
          <p className="setup-helper">What's different today?</p>
          <select
            id="do-situation"
            value={fields.situation}
            onChange={(e) => update({ situation: e.target.value })}
            disabled={busy}
          >
            {SITUATIONS.map((s) => (
              <option key={s}>{s}</option>
            ))}
          </select>
        </div>

        {/* Extra available minutes */}
        <div className="setup-card">
          <label htmlFor="do-minutes">
            <span className="setup-icon">⏱</span>
            Extra Available Minutes
          </label>
          <p className="setup-helper">Positive adds time · Negative reduces time (−240 to +480)</p>
          <input
            id="do-minutes"
            type="number"
            min="-240"
            max="480"
            value={fields.extra_available_minutes}
            onChange={(e) =>
              update({ extra_available_minutes: e.target.value })
            }
            disabled={busy}
          />
        </div>

        {/* Energy level */}
        <div className="setup-card">
          <label htmlFor="do-energy">
            <span className="setup-icon">⚡</span>
            Energy Level
          </label>
          <p className="setup-helper">How energetic are you feeling today?</p>
          <select
            id="do-energy"
            value={fields.energy_level}
            onChange={(e) => update({ energy_level: e.target.value })}
            disabled={busy}
          >
            {ENERGY_LEVELS.map((e) => (
              <option key={e}>{e}</option>
            ))}
          </select>
        </div>

        {/* Optional note */}
        <div className="setup-card do-card-full">
          <label htmlFor="do-note">
            <span className="setup-icon">📝</span>
            Note <span className="do-optional-tag">Optional</span>
          </label>
          <p className="setup-helper">Short note about this override (max 200 characters)</p>
          <input
            id="do-note"
            type="text"
            maxLength={200}
            placeholder="e.g. Physics internal exam today"
            value={fields.note}
            onChange={(e) => update({ note: e.target.value })}
            disabled={busy}
          />
        </div>
      </div>

      {/* ── Action row ── */}
      <div className="do-actions">
        <button
          id="do-save-btn"
          className="do-btn do-btn-primary"
          onClick={handleSave}
          disabled={busy}
        >
          {isSaving ? "Saving…" : "Save Override"}
        </button>
        <button
          id="do-delete-btn"
          className="do-btn do-btn-danger"
          onClick={handleDelete}
          disabled={busy}
        >
          {isDeleting ? "Deleting…" : "Delete Override"}
        </button>
      </div>
    </section>
  );
}
