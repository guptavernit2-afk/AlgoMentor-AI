/**
 * StepReview.jsx — Step 4: Review & Confirm
 *
 * Displays a read-only summary of all collected data.
 * Confirm button logs the final payload to the console.
 * No API calls in this commit.
 */

export default function StepReview({ data, onBack, onConfirm }) {
  // Build the tag arrays for display
  const completedTopics = data.completed_topics_raw
    .split(",")
    .map((t) => t.trim())
    .filter(Boolean);

  const weakConcepts = data.weak_concepts_raw
    .split(",")
    .map((t) => t.trim())
    .filter(Boolean);

  return (
    <div className="ob-step">
      {/* ── Header ── */}
      <div className="ob-step-header">
        <p className="eyebrow">Step 4 of 4</p>
        <h2>Review Your Setup</h2>
        <p className="ob-step-subtitle">
          Confirm everything looks correct. You can go back to make changes.
          Hit Confirm to save your profile — AlgoMentor will personalise
          your dashboard.
        </p>
      </div>

      {/* ── Review sections ── */}
      <div className="ob-review-sections">

        {/* ── Section: Profile ── */}
        <section className="ob-review-section">
          <div className="ob-review-section-header">
            <span className="ob-review-icon">👤</span>
            <h3 className="ob-review-section-title">Profile</h3>
          </div>
          <div className="ob-review-grid">
            <ReviewRow label="Name" value={data.name || "—"} />
            <ReviewRow label="Goal" value={data.goal} />
            <ReviewRow
              label="Preferred Study Time"
              value={data.preferred_study_time}
            />
            <ReviewRow
              label="Min Daily Study"
              value={`${data.minimum_daily_minutes} min`}
            />
            <ReviewRow
              label="Max Daily Study"
              value={`${data.maximum_daily_minutes} min`}
            />
          </div>
        </section>

        {/* ── Section: Learning Profile ── */}
        <section className="ob-review-section">
          <div className="ob-review-section-header">
            <span className="ob-review-icon">📚</span>
            <h3 className="ob-review-section-title">Learning Profile</h3>
          </div>
          <div className="ob-review-grid">
            <ReviewRow
              label="Current Topic"
              value={data.current_topic || "—"}
            />
            <div className="ob-review-row ob-review-full">
              <span className="ob-review-label">Completed Topics</span>
              <div className="ob-review-tags">
                {completedTopics.length > 0 ? (
                  completedTopics.map((t) => (
                    <span key={t} className="ob-tag ob-tag-success">
                      {t}
                    </span>
                  ))
                ) : (
                  <span className="ob-review-empty">None</span>
                )}
              </div>
            </div>
            <div className="ob-review-row ob-review-full">
              <span className="ob-review-label">Weak Concepts</span>
              <div className="ob-review-tags">
                {weakConcepts.length > 0 ? (
                  weakConcepts.map((t) => (
                    <span key={t} className="ob-tag ob-tag-warning">
                      {t}
                    </span>
                  ))
                ) : (
                  <span className="ob-review-empty">None</span>
                )}
              </div>
            </div>
          </div>
        </section>

        {/* ── Section: Weekly Schedule ── */}
        <section className="ob-review-section">
          <div className="ob-review-section-header">
            <span className="ob-review-icon">📅</span>
            <h3 className="ob-review-section-title">Weekly Schedule</h3>
          </div>
          <div className="ob-review-schedule">
            {data.days.map((d) => (
              <div key={d.day} className="ob-review-day">
                <div className="ob-review-day-name">
                  {d.day.slice(0, 3).toUpperCase()}
                </div>
                <div className="ob-review-day-content">
                  {d.is_free_day ? (
                    <span className="ob-free-badge">Free Day</span>
                  ) : d.classes.length === 0 ? (
                    <span className="ob-review-empty">No classes</span>
                  ) : (
                    d.classes.map((slot, i) => (
                      <span key={i} className="ob-review-slot">
                        <strong>{slot.title || "Untitled"}</strong>{" "}
                        <span className="ob-slot-time">
                          {slot.start_time} – {slot.end_time}
                        </span>
                      </span>
                    ))
                  )}
                </div>
              </div>
            ))}
          </div>
        </section>
      </div>

      {/* ── Console note ── */}
      <p className="ob-console-note">
        ⚡ Confirm logs your setup to the console. Backend API integration
        ships in Commit&nbsp;#2.
      </p>

      {/* ── Navigation ── */}
      <div className="ob-nav ob-nav-between">
        <button className="ob-btn-ghost" onClick={onBack}>
          ← Back
        </button>
        <button className="ob-btn-confirm" onClick={onConfirm}>
          ✓ Confirm &amp; Save Profile
        </button>
      </div>
    </div>
  );
}

// ─── Tiny helper ─────────────────────────────────────────────────────────────

function ReviewRow({ label, value }) {
  return (
    <div className="ob-review-row">
      <span className="ob-review-label">{label}</span>
      <span className="ob-review-value">{value}</span>
    </div>
  );
}
