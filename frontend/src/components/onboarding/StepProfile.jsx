/**
 * StepProfile.jsx — Step 1: Basic Profile
 *
 * Collects: name, goal, preferred_study_time,
 *           minimum_daily_minutes, maximum_daily_minutes
 *
 * Validation rules (must match backend StudentProfile Pydantic model):
 *   - name:                    trim().length >= 2
 *   - minimum_daily_minutes:   >= 10
 *   - maximum_daily_minutes:   >= 20
 *   - maximum_daily_minutes:   >= minimum_daily_minutes
 *
 * Next button is disabled until ALL rules pass.
 */

const GOAL_OPTIONS = [
  "Beginner DSA",
  "College Practice",
  "Internship Prep",
  "Placement Prep",
  "Competitive Programming",
];

const STUDY_TIME_OPTIONS = ["Morning", "Afternoon", "Evening", "Night"];

export default function StepProfile({ data, update, onNext }) {
  // ── Per-field error derivation (pure, no extra state) ──────────────────────
  const nameError =
    data.name.trim().length === 0
      ? "Name is required."
      : data.name.trim().length < 2
      ? "Name must be at least 2 characters."
      : null;

  const minError =
    data.minimum_daily_minutes < 10
      ? "Minimum must be at least 10 minutes."
      : null;

  const maxError =
    data.maximum_daily_minutes < 20
      ? "Maximum must be at least 20 minutes."
      : data.maximum_daily_minutes < data.minimum_daily_minutes
      ? "Maximum must be greater than or equal to minimum."
      : null;

  // ── Master validity gate ───────────────────────────────────────────────────
  const isValid =
    nameError === null &&
    minError === null &&
    maxError === null;

  return (
    <div className="ob-step">
      {/* ── Header ── */}
      <div className="ob-step-header">
        <p className="eyebrow">Step 1 of 4</p>
        <h2>Basic Profile</h2>
        <p className="ob-step-subtitle">
          Tell AlgoMentor about yourself so it can build a personalised
          revision plan.
        </p>
      </div>

      {/* ── Fields ── */}
      <div className="ob-fields">

        {/* Name */}
        <div className="ob-field-group ob-field-full">
          <label htmlFor="ob-name" className="ob-label">
            <span className="ob-label-icon">👤</span>
            Your Name <span className="ob-required">*</span>
          </label>
          <input
            id="ob-name"
            className={`ob-input ${nameError ? "ob-input-error" : ""}`}
            type="text"
            placeholder="e.g. Arjun Sharma"
            value={data.name}
            onChange={(e) => update({ name: e.target.value })}
            autoFocus
          />
          {nameError && (
            <span className="ob-field-hint">{nameError}</span>
          )}
        </div>

        {/* Goal */}
        <div className="ob-field-group">
          <label htmlFor="ob-goal" className="ob-label">
            <span className="ob-label-icon">🏆</span>
            Learning Goal <span className="ob-required">*</span>
          </label>
          <p className="ob-field-helper">Calibrates problem difficulty preference</p>
          <select
            id="ob-goal"
            className="ob-select"
            value={data.goal}
            onChange={(e) => update({ goal: e.target.value })}
          >
            {GOAL_OPTIONS.map((g) => (
              <option key={g} value={g}>
                {g}
              </option>
            ))}
          </select>
        </div>

        {/* Preferred Study Time */}
        <div className="ob-field-group">
          <label htmlFor="ob-study-time" className="ob-label">
            <span className="ob-label-icon">🕐</span>
            Preferred Study Time
          </label>
          <p className="ob-field-helper">When do you study best?</p>
          <select
            id="ob-study-time"
            className="ob-select"
            value={data.preferred_study_time}
            onChange={(e) => update({ preferred_study_time: e.target.value })}
          >
            {STUDY_TIME_OPTIONS.map((t) => (
              <option key={t} value={t}>
                {t}
              </option>
            ))}
          </select>
        </div>

        {/* Min daily minutes */}
        <div className="ob-field-group">
          <label htmlFor="ob-min-minutes" className="ob-label">
            <span className="ob-label-icon">⏱</span>
            Min Daily Study (min)
          </label>
          <p className="ob-field-helper">Minimum commitment per day (≥ 10 min)</p>
          <input
            id="ob-min-minutes"
            className={`ob-input ${minError ? "ob-input-error" : ""}`}
            type="number"
            min="10"
            max="480"
            step="5"
            value={data.minimum_daily_minutes}
            onChange={(e) =>
              update({ minimum_daily_minutes: Number(e.target.value) })
            }
          />
          {minError && (
            <span className="ob-field-hint">{minError}</span>
          )}
        </div>

        {/* Max daily minutes */}
        <div className="ob-field-group">
          <label htmlFor="ob-max-minutes" className="ob-label">
            <span className="ob-label-icon">⏰</span>
            Max Daily Study (min)
          </label>
          <p className="ob-field-helper">Upper limit for daily sessions (≥ min)</p>
          <input
            id="ob-max-minutes"
            className={`ob-input ${maxError ? "ob-input-error" : ""}`}
            type="number"
            min="20"
            max="480"
            step="5"
            value={data.maximum_daily_minutes}
            onChange={(e) =>
              update({ maximum_daily_minutes: Number(e.target.value) })
            }
          />
          {maxError && (
            <span className="ob-field-hint">{maxError}</span>
          )}
        </div>
      </div>

      {/* ── Navigation ── */}
      <div className="ob-nav ob-nav-right">
        <button
          className="ob-btn-primary"
          onClick={onNext}
          disabled={!isValid}
        >
          Next: Learning Profile →
        </button>
      </div>
    </div>
  );
}
