import { useState, useEffect, useCallback } from "react";
import { getDailyPlan, DEMO_USER_ID } from "../services/api";

function todayISO() {
  const d = new Date();
  const yyyy = d.getFullYear();
  const mm = String(d.getMonth() + 1).padStart(2, "0");
  const dd = String(d.getDate()).padStart(2, "0");
  return `${yyyy}-${mm}-${dd}`;
}

export default function SmartDailyPlanPanel({ onProblemSelect }) {
  const [date, setDate] = useState(todayISO());
  const [plan, setPlan] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  const fetchPlan = useCallback(async (targetDate) => {
    setIsLoading(true);
    try {
      const data = await getDailyPlan(DEMO_USER_ID, targetDate);
      setPlan(data);
    } catch (err) {
      console.warn("Failed to fetch plan", err);
      setPlan(null);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => { fetchPlan(date); }, [date, fetchPlan]);

  return (
    <div className="widget-card" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', height: '100%' }}>
      
      {/* ── Header ── */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h2 style={{ fontSize: '1.25rem', margin: 0, color: 'var(--text-primary)' }}>Smart Daily Plan</h2>
        <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', background: 'var(--bg-dark)', border: '1px solid var(--border-strong)', borderRadius: 'var(--radius-sm)', padding: '0.25rem 0.5rem', gap: '0.5rem' }}>
            <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>{date.split('-').reverse().join('-')}</span>
            <input 
              type="date" 
              value={date} 
              onChange={e => setDate(e.target.value)}
              style={{ background: 'transparent', border: 'none', color: 'transparent', width: '20px', cursor: 'pointer', outline: 'none' }}
              title="Select Date"
            />
          </div>
          <button onClick={() => fetchPlan(date)} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', background: 'var(--bg-dark)', border: '1px solid var(--border-strong)', color: 'var(--text-primary)', padding: '0.4rem 0.75rem', borderRadius: 'var(--radius-sm)', cursor: 'pointer', fontSize: '0.8rem' }}>
            Refresh ↻
          </button>
        </div>
      </div>

      {isLoading && <p style={{ fontSize: '0.85rem', color: 'var(--accent-indigo)' }}>Optimizing plan...</p>}

      {plan && (
        <>
          {/* ── Badges Row ── */}
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.75rem' }}>
            
            <div style={{ flex: '1 1 auto', minWidth: '140px', background: 'var(--bg-dark)', border: '1px solid var(--border-strong)', borderRadius: 'var(--radius-sm)', padding: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <span style={{ fontSize: '1.25rem', color: 'var(--accent-blue)', background: 'rgba(59, 130, 246, 0.1)', width: '32px', height: '32px', display: 'flex', alignItems: 'center', justifyContent: 'center', borderRadius: '50%' }}>📅</span>
              <div style={{ display: 'flex', flexDirection: 'column' }}>
                <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-primary)' }}>{plan.day_name}</span>
                <span style={{ fontSize: '0.7rem', color: 'var(--text-secondary)' }}>Day</span>
              </div>
            </div>

            <div style={{ flex: '1 1 auto', minWidth: '140px', background: 'var(--bg-dark)', border: '1px solid var(--border-strong)', borderRadius: 'var(--radius-sm)', padding: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <span style={{ fontSize: '1.25rem', color: 'var(--accent-green)', background: 'rgba(16, 185, 129, 0.1)', width: '32px', height: '32px', display: 'flex', alignItems: 'center', justifyContent: 'center', borderRadius: '50%' }}>🌳</span>
              <div style={{ display: 'flex', flexDirection: 'column' }}>
                <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-primary)' }}>{plan.plan_intensity}</span>
                <span style={{ fontSize: '0.7rem', color: 'var(--text-secondary)' }}>Intensity</span>
              </div>
            </div>

            <div style={{ flex: '1 1 auto', minWidth: '140px', background: 'var(--bg-dark)', border: '1px solid var(--border-strong)', borderRadius: 'var(--radius-sm)', padding: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <span style={{ fontSize: '1.25rem', color: 'var(--accent-red)', background: 'rgba(239, 68, 68, 0.1)', width: '32px', height: '32px', display: 'flex', alignItems: 'center', justifyContent: 'center', borderRadius: '50%' }}>🎯</span>
              <div style={{ display: 'flex', flexDirection: 'column' }}>
                <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-primary)' }}>{plan.derived_workload}</span>
                <span style={{ fontSize: '0.7rem', color: 'var(--text-secondary)' }}>Workload</span>
              </div>
            </div>

            <div style={{ flex: '1 1 auto', minWidth: '140px', background: 'var(--bg-dark)', border: '1px solid var(--border-strong)', borderRadius: 'var(--radius-sm)', padding: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <span style={{ fontSize: '1.25rem', color: 'var(--accent-green)', background: 'rgba(16, 185, 129, 0.1)', width: '32px', height: '32px', display: 'flex', alignItems: 'center', justifyContent: 'center', borderRadius: '50%' }}>✅</span>
              <div style={{ display: 'flex', flexDirection: 'column' }}>
                <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-primary)' }}>{plan.available_minutes}</span>
                <span style={{ fontSize: '0.7rem', color: 'var(--text-secondary)' }}>Available Minutes</span>
              </div>
            </div>

            {plan.override_applied && (
              <div style={{ flex: '1 1 auto', minWidth: '160px', background: 'var(--bg-dark)', border: '1px solid var(--accent-orange)', borderRadius: 'var(--radius-sm)', padding: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                <span style={{ fontSize: '1.25rem', color: 'var(--accent-orange)', background: 'rgba(245, 158, 11, 0.1)', width: '32px', height: '32px', display: 'flex', alignItems: 'center', justifyContent: 'center', borderRadius: '50%' }}>⚡</span>
                <div style={{ display: 'flex', flexDirection: 'column' }}>
                  <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--accent-orange)' }}>Override Applied</span>
                  <span style={{ fontSize: '0.65rem', color: 'var(--text-secondary)' }}>Internal Exam / Test</span>
                </div>
              </div>
            )}
            
          </div>

          {/* ── Info Banner ── */}
          <div style={{ background: 'rgba(59, 130, 246, 0.1)', color: '#bae6fd', padding: '0.75rem 1rem', borderRadius: 'var(--radius-sm)', fontSize: '0.8rem', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <span style={{ background: 'var(--accent-blue)', color: '#fff', width: '18px', height: '18px', display: 'flex', alignItems: 'center', justifyContent: 'center', borderRadius: '50%', fontSize: '0.65rem', fontWeight: 'bold' }}>i</span>
            Plan generated based on your profile, SM-2 revision data, and today's override.
          </div>

          {/* ── Plan Reason ── */}
          <div>
            <h4 style={{ fontSize: '0.9rem', margin: '0 0 0.5rem 0', color: 'var(--text-primary)' }}>Plan Reason</h4>
            <p style={{ margin: 0, fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
              {plan.plan_reason}
            </p>
          </div>

          {/* ── 2 Columns: Revision Focus & Today's Tasks ── */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1.5rem', marginTop: '0.5rem', borderTop: '1px solid var(--border-light)', paddingTop: '1.5rem' }}>
            
            <div>
              <h4 style={{ fontSize: '0.9rem', margin: '0 0 1rem 0', color: 'var(--text-primary)' }}>Revision Focus</h4>
              <div style={{ background: 'var(--bg-dark)', border: '1px solid var(--border-strong)', padding: '1rem', borderRadius: 'var(--radius-sm)' }}>
                <strong style={{ display: 'block', color: 'var(--accent-red)', marginBottom: '0.5rem', fontSize: '0.85rem' }}>{plan.revision_focus || "General Practice"}</strong>
                <p style={{ margin: 0, fontSize: '0.8rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>{plan.revision_note}</p>
              </div>
            </div>

            <div>
              <h4 style={{ fontSize: '0.9rem', margin: '0 0 1rem 0', color: 'var(--text-primary)' }}>Today's Tasks ({plan.tasks.length})</h4>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                {plan.tasks.map((task, i) => (
                  <button 
                    key={i} 
                    onClick={() => onProblemSelect ? onProblemSelect(task) : null}
                    style={{ 
                      display: 'flex', 
                      alignItems: 'flex-start', 
                      gap: '0.75rem', 
                      background: 'var(--bg-dark)', 
                      padding: '0.75rem', 
                      borderRadius: 'var(--radius-sm)', 
                      border: '1px solid var(--border-strong)',
                      cursor: 'pointer',
                      textAlign: 'left',
                      transition: 'border-color 0.2s',
                      width: '100%'
                    }}
                    onMouseOver={(e) => e.currentTarget.style.borderColor = 'var(--accent-indigo)'}
                    onMouseOut={(e) => e.currentTarget.style.borderColor = 'var(--border-strong)'}
                  >
                    <div style={{ background: 'var(--bg-panel)', padding: '0.2rem 0.5rem', borderRadius: '4px', fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)' }}>
                      {task.duration_minutes}m
                    </div>
                    <div>
                      <div style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-primary)' }}>{task.title}</div>
                      <div style={{ fontSize: '0.7rem', color: 'var(--text-secondary)', marginTop: '0.15rem' }}>{task.topic}</div>
                    </div>
                    <div style={{ marginLeft: 'auto', color: 'var(--accent-indigo)', fontSize: '1.2rem', display: 'flex', alignItems: 'center' }}>
                      ›
                    </div>
                  </button>
                ))}
              </div>
            </div>

          </div>

        </>
      )}
      {!plan && !isLoading && <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>No plan available for this date.</p>}
    </div>
  );
}
