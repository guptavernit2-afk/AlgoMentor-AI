/**
 * StepLearning.jsx — Step 2: Learning Profile
 *
 * Collects: current_topic, completed_topics_raw, weak_concepts_raw
 *
 * Validation rules (must match backend StudentProfile Pydantic model):
 *   - current_topic: trim().length >= 2  (backend: min_length=2)
 *
 * Completed Topics and Weak Concepts use comma-separated text inputs.
 * Raw strings are split into arrays only on final Confirm.
 */

export default function StepLearning({ data, update, onNext, onBack }) {
  const topicError =
    data.current_topic.trim().length === 0
      ? "Current topic is required."
      : data.current_topic.trim().length < 2
      ? "Topic must be at least 2 characters."
      : null;

  const isValid = topicError === null;

  return (
    <div className="ob-step">
      {/* ── Header ── */}
      <div className="ob-step-header">
        <p className="eyebrow">Step 2 of 4</p>
        <h2>Learning Profile</h2>
        <p className="ob-step-subtitle">
          Help AlgoMentor understand where you are in your DSA journey so
          it can prioritise the right topics.
        </p>
      </div>

      {/* ── Fields ── */}
      <div className="ob-fields">

        {/* Current Topic */}
        <div className="ob-field-group ob-field-full">
          <label htmlFor="ob-current-topic" className="ob-label">
            <span className="ob-label-icon">📍</span>
            Current Topic <span className="ob-required">*</span>
          </label>
          <p className="ob-field-helper">
            What DSA topic are you actively learning right now?
          </p>
          <input
            id="ob-current-topic"
            className={`ob-input ${topicError ? "ob-input-error" : ""}`}
            type="text"
            placeholder="e.g. Hashing"
            value={data.current_topic}
            onChange={(e) => update({ current_topic: e.target.value })}
            autoFocus
          />
          {topicError && (
            <span className="ob-field-hint">{topicError}</span>
          )}
        </div>

        {/* Completed Topics */}
        <div className="ob-field-group ob-field-full">
          <label htmlFor="ob-completed" className="ob-label">
            <span className="ob-label-icon">✅</span>
            Completed Topics
          </label>
          <p className="ob-field-helper">
            Comma-separated list of topics you've finished studying.
            Leave blank if none.
          </p>
          <input
            id="ob-completed"
            className="ob-input"
            type="text"
            placeholder="e.g. Arrays, Strings, Recursion"
            value={data.completed_topics_raw}
            onChange={(e) => update({ completed_topics_raw: e.target.value })}
          />
          {data.completed_topics_raw.trim().length > 0 && (
            <div className="ob-tag-preview">
              {data.completed_topics_raw
                .split(",")
                .map((t) => t.trim())
                .filter(Boolean)
                .map((t) => (
                  <span key={t} className="ob-tag ob-tag-success">
                    {t}
                  </span>
                ))}
            </div>
          )}
        </div>

        {/* Weak Concepts */}
        <div className="ob-field-group ob-field-full">
          <label htmlFor="ob-weak" className="ob-label">
            <span className="ob-label-icon">🎯</span>
            Weak Concepts
          </label>
          <p className="ob-field-helper">
            Comma-separated list of concepts you find difficult. AlgoMentor
            will boost their match score in recommendations.
          </p>
          <input
            id="ob-weak"
            className="ob-input"
            type="text"
            placeholder="e.g. Prefix Sum, Sliding Window, DP"
            value={data.weak_concepts_raw}
            onChange={(e) => update({ weak_concepts_raw: e.target.value })}
          />
          {data.weak_concepts_raw.trim().length > 0 && (
            <div className="ob-tag-preview">
              {data.weak_concepts_raw
                .split(",")
                .map((t) => t.trim())
                .filter(Boolean)
                .map((t) => (
                  <span key={t} className="ob-tag ob-tag-warning">
                    {t}
                  </span>
                ))}
            </div>
          )}
        </div>
      </div>

      {/* ── Navigation ── */}
      <div className="ob-nav ob-nav-between">
        <button className="ob-btn-ghost" onClick={onBack}>
          ← Back
        </button>
        <button
          className="ob-btn-primary"
          onClick={onNext}
          disabled={!isValid}
        >
          Next: Weekly Schedule →
        </button>
      </div>
    </div>
  );
}
