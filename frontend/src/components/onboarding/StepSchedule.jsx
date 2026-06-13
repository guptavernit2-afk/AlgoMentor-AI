/**
 * StepSchedule.jsx — Step 3: Weekly Schedule
 *
 * Renders one collapsible day-row for each of the 7 weekdays.
 * Each day supports:
 *   - Free Day toggle
 *   - Add Class Slot (Title, Start Time, End Time)
 *   - Remove individual slots
 *
 * Validation rules (must match backend ClassSlot Pydantic model):
 *   - slot.title:      trim().length >= 2
 *   - slot.end_time:   must be strictly later than slot.start_time
 *
 * Next is disabled while ANY non-free-day slot violates these rules.
 * All mutations go through update() passed from OnboardingWizard.
 */

import { useState } from "react";

// ─── Time helpers ────────────────────────────────────────────────────────────

/** Convert "HH:MM" string to total minutes since midnight. */
function toMinutes(timeStr) {
  if (!timeStr || !timeStr.includes(":")) return 0;
  const [h, m] = timeStr.split(":");
  return parseInt(h, 10) * 60 + parseInt(m, 10);
}

/** Returns an error string if the slot is invalid, null otherwise. */
function getSlotError(slot) {
  const titleTrimmed = slot.title.trim();
  if (titleTrimmed.length === 0) {
    return "Class title is required.";
  }
  if (titleTrimmed.length < 2) {
    return "Class title must be at least 2 characters.";
  }
  if (toMinutes(slot.end_time) <= toMinutes(slot.start_time)) {
    return "End time must be later than start time.";
  }
  return null;
}

/** Returns true if a day has at least one invalid slot. */
function dayHasErrors(dayData) {
  if (dayData.is_free_day) return false;
  return dayData.classes.some((slot) => getSlotError(slot) !== null);
}

// ─── DayRow ─────────────────────────────────────────────────────────────────

function DayRow({ dayData, dayIndex, onUpdateDay }) {
  const [expanded, setExpanded] = useState(false);

  function toggleFreeDay() {
    onUpdateDay(dayIndex, {
      is_free_day: !dayData.is_free_day,
      // Clear classes when marking as free
      classes: !dayData.is_free_day ? [] : dayData.classes,
    });
  }

  function addSlot() {
    onUpdateDay(dayIndex, {
      classes: [
        ...dayData.classes,
        { title: "", start_time: "09:00", end_time: "10:00" },
      ],
    });
  }

  function removeSlot(slotIndex) {
    onUpdateDay(dayIndex, {
      classes: dayData.classes.filter((_, i) => i !== slotIndex),
    });
  }

  function updateSlot(slotIndex, patch) {
    const updated = dayData.classes.map((slot, i) =>
      i === slotIndex ? { ...slot, ...patch } : slot
    );
    onUpdateDay(dayIndex, { classes: updated });
  }

  const hasSlots = dayData.classes.length > 0;
  const hasErrors = dayHasErrors(dayData);

  return (
    <div
      className={`ob-day-row ${dayData.is_free_day ? "ob-day-free" : ""} ${
        expanded ? "ob-day-expanded" : ""
      } ${hasErrors ? "ob-day-has-errors" : ""}`}
    >
      {/* ── Day header (always visible) ── */}
      <div className="ob-day-header">
        <div className="ob-day-left">
          <button
            className="ob-day-toggle-btn"
            onClick={() => setExpanded((v) => !v)}
            aria-expanded={expanded}
            aria-label={`Toggle ${dayData.day}`}
          >
            <span className="ob-day-chevron">{expanded ? "▼" : "▶"}</span>
            <span className="ob-day-name">{dayData.day}</span>
          </button>
          {hasSlots && !dayData.is_free_day && (
            <span className={`ob-slot-count ${hasErrors ? "ob-slot-count-error" : ""}`}>
              {dayData.classes.length} class{dayData.classes.length > 1 ? "es" : ""}
              {hasErrors && " · fix errors"}
            </span>
          )}
          {dayData.is_free_day && (
            <span className="ob-free-badge">Free Day</span>
          )}
        </div>

        <div className="ob-day-right">
          {/* Free Day toggle */}
          <label className="ob-toggle-label" htmlFor={`free-${dayData.day}`}>
            <span className="ob-toggle-text">Free Day</span>
            <div
              className={`ob-toggle ${dayData.is_free_day ? "ob-toggle-on" : ""}`}
              onClick={toggleFreeDay}
              role="switch"
              aria-checked={dayData.is_free_day}
              id={`free-${dayData.day}`}
            >
              <div className="ob-toggle-thumb" />
            </div>
          </label>
        </div>
      </div>

      {/* ── Expandable slot area ── */}
      {expanded && !dayData.is_free_day && (
        <div className="ob-day-body">
          {dayData.classes.length === 0 && (
            <p className="ob-no-slots">
              No classes scheduled — add a slot or mark as Free Day.
            </p>
          )}

          {dayData.classes.map((slot, slotIdx) => {
            const slotError = getSlotError(slot);
            return (
              <div
                key={slotIdx}
                className={`ob-slot ${slotError ? "ob-slot-invalid" : ""}`}
              >
                <div className="ob-slot-fields">
                  {/* Title */}
                  <div className="ob-slot-field ob-slot-title">
                    <label className="ob-slot-label">
                      Class Title <span className="ob-required">*</span>
                    </label>
                    <input
                      className={`ob-input ob-input-sm ${
                        slot.title.trim().length < 2 ? "ob-input-error" : ""
                      }`}
                      type="text"
                      placeholder="e.g. Operating Systems"
                      value={slot.title}
                      onChange={(e) =>
                        updateSlot(slotIdx, { title: e.target.value })
                      }
                    />
                  </div>

                  {/* Start Time */}
                  <div className="ob-slot-field">
                    <label className="ob-slot-label">Start</label>
                    <input
                      className="ob-input ob-input-sm ob-input-time"
                      type="time"
                      value={slot.start_time}
                      onChange={(e) =>
                        updateSlot(slotIdx, { start_time: e.target.value })
                      }
                    />
                  </div>

                  {/* End Time */}
                  <div className="ob-slot-field">
                    <label className="ob-slot-label">End</label>
                    <input
                      className={`ob-input ob-input-sm ob-input-time ${
                        toMinutes(slot.end_time) <= toMinutes(slot.start_time)
                          ? "ob-input-error"
                          : ""
                      }`}
                      type="time"
                      value={slot.end_time}
                      onChange={(e) =>
                        updateSlot(slotIdx, { end_time: e.target.value })
                      }
                    />
                  </div>
                </div>

                {/* Per-slot error message */}
                {slotError && (
                  <span className="ob-slot-error-msg">{slotError}</span>
                )}

                {/* Remove */}
                <button
                  className="ob-slot-remove"
                  onClick={() => removeSlot(slotIdx)}
                  aria-label="Remove slot"
                >
                  ✕
                </button>
              </div>
            );
          })}

          <button className="ob-add-slot-btn" onClick={addSlot}>
            + Add Class Slot
          </button>
        </div>
      )}

      {/* If free day but expanded — show a note */}
      {expanded && dayData.is_free_day && (
        <div className="ob-day-body">
          <p className="ob-no-slots ob-free-note">
            This day is marked as a free day. No classes will be scheduled.
            Toggle off to add classes.
          </p>
        </div>
      )}
    </div>
  );
}

// ─── StepSchedule ────────────────────────────────────────────────────────────

export default function StepSchedule({ data, update, onNext, onBack }) {
  function handleUpdateDay(dayIndex, patch) {
    const updatedDays = data.days.map((d, i) =>
      i === dayIndex ? { ...d, ...patch } : d
    );
    update({ days: updatedDays });
  }

  const totalClasses = data.days.reduce((n, d) => n + d.classes.length, 0);
  const freeDays = data.days.filter((d) => d.is_free_day).length;

  // Next is disabled if ANY non-free day contains an invalid slot
  const hasAnyError = data.days.some((d) => dayHasErrors(d));

  return (
    <div className="ob-step">
      {/* ── Header ── */}
      <div className="ob-step-header">
        <p className="eyebrow">Step 3 of 4</p>
        <h2>Weekly College Timetable</h2>
        <p className="ob-step-subtitle">
          Add your regular class schedule for each day. AlgoMentor uses
          this to plan DSA sessions around your commitments.
        </p>
      </div>

      {/* ── Summary chips ── */}
      <div className="ob-schedule-summary">
        <span className="ob-summary-chip">
          <span className="ob-chip-dot ob-chip-dot-cyan" />
          {totalClasses} class{totalClasses !== 1 ? "es" : ""} scheduled
        </span>
        <span className="ob-summary-chip">
          <span className="ob-chip-dot ob-chip-dot-purple" />
          {freeDays} free day{freeDays !== 1 ? "s" : ""}
        </span>
        {hasAnyError && (
          <span className="ob-summary-chip ob-summary-chip-error">
            <span className="ob-chip-dot ob-chip-dot-danger" />
            Fix errors to continue
          </span>
        )}
      </div>

      {/* ── Day rows ── */}
      <div className="ob-days-list">
        {data.days.map((dayData, i) => (
          <DayRow
            key={dayData.day}
            dayData={dayData}
            dayIndex={i}
            onUpdateDay={handleUpdateDay}
          />
        ))}
      </div>

      {/* ── Navigation ── */}
      <div className="ob-nav ob-nav-between">
        <button className="ob-btn-ghost" onClick={onBack}>
          ← Back
        </button>
        <button
          className="ob-btn-primary"
          onClick={onNext}
          disabled={hasAnyError}
        >
          Next: Review →
        </button>
      </div>
    </div>
  );
}



