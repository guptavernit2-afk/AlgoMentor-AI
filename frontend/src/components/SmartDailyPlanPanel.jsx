import { useState, useEffect, useCallback } from "react";
import { getDailyPlan, DEMO_USER_ID } from "../services/api";
import "./SmartDailyPlanPanel.css";

/** Returns today's date as a YYYY-MM-DD string in local time. */
function todayISO() {
  const d = new Date();
  const yyyy = d.getFullYear();
  const mm = String(d.getMonth() + 1).padStart(2, "0");
  const dd = String(d.getDate()).padStart(2, "0");
  return `${yyyy}-${mm}-${dd}`;
}

/** Mirror of DailyOverridePanel's toUserMessage. */
function toUserMessage(error, context) {
  const status = error?.status;
  if (status === 404) {
    return "No plan exists for this date. (Profile or schedule missing)";
  }
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

export default function SmartDailyPlanPanel() {
  const [date, setDate] = useState(todayISO());
  const [plan, setPlan] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [errorBanner, setErrorBanner] = useState(null);

  const fetchPlan = useCallback(async (targetDate) => {
    setIsLoading(true);
    setErrorBanner(null);
    setPlan(null);

    try {
      const data = await getDailyPlan(DEMO_USER_ID, targetDate);
      setPlan(data);
    } catch (err) {
      if (err.status === 404) {
        // Handle 404 gracefully as "No plan setup" instead of a banner
        setErrorBanner({
          type: "warn",
          title: "Setup Required",
          sub: "Weekly schedule or profile is missing. Please complete setup first."
        });
      } else {
        setErrorBanner({
          type: "error",
          title: "Failed to load plan",
          sub: toUserMessage(err, "loading plan")
        });
      }
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Fetch plan when date changes
  useEffect(() => {
    fetchPlan(date);
  }, [date, fetchPlan]);

  return (
    <div className="sdp-panel">
      <div className="sdp-header-top">
        <h2 className="section-head" style={{ margin: 0 }}>Smart Daily Plan</h2>
        <div className="sdp-date-picker">
          {isLoading && <span className="sdp-loading-hint">Loading plan...</span>}
          <input
            type="date"
            value={date}
            onChange={(e) => setDate(e.target.value)}
          />
        </div>
      </div>

      {errorBanner && (
        <div className={`sdp-banner sdp-banner-${errorBanner.type}`}>
          <div className="sdp-banner-text">{errorBanner.title}</div>
          <div className="sdp-banner-sub">{errorBanner.sub}</div>
        </div>
      )}

      {plan && (
        <>
          <div className="sdp-header">
            <div className="sdp-header-top">
              <span className="sdp-day-name">{plan.day_name}</span>
            </div>
            <div className="sdp-meta">
              <span className={`sdp-badge sdp-badge-intensity-${plan.plan_intensity}`}>
                {plan.plan_intensity} Intensity
              </span>
              <span className="sdp-badge" style={{ background: 'rgba(255,255,255,0.1)', color: '#e2e8f0' }}>
                {plan.derived_workload} Workload
              </span>
              <span className="sdp-badge" style={{ background: 'rgba(56, 189, 248, 0.1)', color: '#bae6fd' }}>
                {plan.available_minutes} mins available
              </span>
              {plan.override_applied && (
                <span className="sdp-badge sdp-badge-override">Override Applied</span>
              )}
            </div>
            <div className="sdp-plan-reason">{plan.plan_reason}</div>
          </div>

          <div className="sdp-revision-banner">
            <strong>Revision Focus: {plan.revision_focus || "None"}</strong>
            <p>{plan.revision_note}</p>
          </div>

          <div>
            <h3 className="sdp-section-title">
              <span>📅</span> Today's Tasks
            </h3>
            <div className="sdp-task-list">
              {plan.tasks.map((task) => (
                <div key={task.task_id} className="sdp-task-card">
                  <div className="sdp-task-header">
                    <span className="sdp-task-title">{task.title}</span>
                    <span className="sdp-task-meta">
                      {task.duration_minutes > 0 ? `${task.duration_minutes}m` : '0m'}
                    </span>
                  </div>
                  <div className="sdp-task-meta" style={{ marginTop: '-0.2rem' }}>
                    <span className="sdp-badge" style={{ background: 'rgba(255,255,255,0.05)' }}>
                      {task.task_type}
                    </span>
                    <span>• {task.topic}</span>
                  </div>
                  <p className="sdp-task-reason">{task.reason}</p>
                </div>
              ))}
            </div>
          </div>

          <div>
            <h3 className="sdp-section-title">
              <span>🎯</span> Recommended Problems
            </h3>
            <div className="sdp-problem-list">
              {plan.recommended_problems.map((problem) => (
                <div key={problem.id} className="sdp-problem-card">
                  <div className="sdp-problem-header">
                    <span className="sdp-problem-title">{problem.title}</span>
                    <span className={`sdp-problem-difficulty sdp-diff-${problem.difficulty}`}>
                      {problem.difficulty}
                    </span>
                  </div>
                  <p className="sdp-problem-reason">{problem.reason}</p>
                  
                  <div className="sdp-problem-meta">
                    <div className="sdp-problem-score">
                      Match Score: {problem.match_score}%
                      <div className="sdp-problem-score-bar-bg">
                        <div 
                          className="sdp-problem-score-bar-fill" 
                          style={{ width: `${problem.match_score}%` }} 
                        />
                      </div>
                    </div>
                    {problem.leetcode_link && (
                      <a 
                        href={problem.leetcode_link} 
                        target="_blank" 
                        rel="noreferrer"
                        className="sdp-problem-link"
                      >
                        Solve ↗
                      </a>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
