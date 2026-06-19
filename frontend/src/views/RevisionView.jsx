import React, { useState, useEffect, useCallback } from 'react';
import { BarChart, Bar, ResponsiveContainer, Cell } from 'recharts';
import { getDailyPlan, DEMO_USER_ID } from '../services/api';
import './RevisionView.css';

function todayISO() {
  const d = new Date();
  const yyyy = d.getFullYear();
  const mm = String(d.getMonth() + 1).padStart(2, '0');
  const dd = String(d.getDate()).padStart(2, '0');
  return `${yyyy}-${mm}-${dd}`;
}

const mockChartData = [
  { name: 'Mon', val: 30 },
  { name: 'Tue', val: 50 },
  { name: 'Wed', val: 40 },
  { name: 'Thu', val: 80 },
  { name: 'Fri', val: 45 },
  { name: 'Sat', val: 90 },
  { name: 'Sun', val: 30 },
];

export default function RevisionView({ setActiveView, onNavigateWorkspace }) {
  const [date, setDate] = useState(todayISO());
  const [plan, setPlan] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [completedTasks, setCompletedTasks] = useState(new Set());

  const fetchPlan = useCallback(async (targetDate) => {
    setIsLoading(true);
    try {
      const data = await getDailyPlan(DEMO_USER_ID, targetDate);
      setPlan(data);
      setCompletedTasks(new Set());
    } catch (err) {
      console.warn("Failed to fetch plan", err);
      setPlan(null);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => { 
    fetchPlan(date); 
  }, [date, fetchPlan]);

  const handleStartSolving = (task) => {
    if (task.problem && task.problem.id) {
      if (onNavigateWorkspace) {
        onNavigateWorkspace(task.problem.id);
      } else {
        setActiveView('workspace');
      }
    } else {
      toggleTaskCompletion(task.task_id);
    }
  };

  const toggleTaskCompletion = (taskId) => {
    setCompletedTasks(prev => {
      const next = new Set(prev);
      if (next.has(taskId)) {
        next.delete(taskId);
      } else {
        next.add(taskId);
      }
      return next;
    });
  };

  // Progress calculations
  const totalTasks = plan?.tasks?.length || 0;
  const completedCount = completedTasks.size;
  const progressPercent = totalTasks === 0 ? 0 : Math.round((completedCount / totalTasks) * 100);
  
  // SVG Circle calculations
  const radius = 46;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (progressPercent / 100) * circumference;

  return (
    <div className="study-plan-container">
      
      {/* ── HEADER ── */}
      <header className="study-header">
        <div className="study-title-area">
          <h1 className="study-title">Smart Study Plan</h1>
          <div className="study-subtitle-row">
            <span>Personalized. Adaptive. Effective.</span>
            <span className="pill-sm2">SM-2 Active</span>
          </div>
        </div>
        
        <div className="study-actions">
          <div className="date-picker">
            <span>📅</span>
            <input 
              type="date" 
              value={date} 
              onChange={e => setDate(e.target.value)}
              style={{ background: 'transparent', border: 'none', color: '#cbd5e1', outline: 'none', fontFamily: 'inherit' }}
            />
          </div>
          <button className="btn-regenerate" onClick={() => fetchPlan(date)}>Regenerate Plan</button>
        </div>
      </header>

      {/* ── STATS ROW ── */}
      <section className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'rgba(59, 130, 246, 0.1)', color: '#3b82f6' }}>💧</div>
          <div className="stat-info">
            <span className="stat-label">Plan Type</span>
            <span className="stat-value">{plan?.plan_intensity || 'Deep'}</span>
            <span className="stat-subtext">High Focus</span>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'rgba(16, 185, 129, 0.1)', color: '#10b981' }}>☑️</div>
          <div className="stat-info">
            <span className="stat-label">Daily Goal</span>
            <span className="stat-value">{plan?.available_minutes || 120} mins</span>
            <span className="stat-subtext">Daily Target</span>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'rgba(245, 158, 11, 0.1)', color: '#f59e0b' }}>🔥</div>
          <div className="stat-info">
            <span className="stat-label">Plan Streak</span>
            <span className="stat-value">12 Days</span>
            <span className="stat-subtext">Keep it going! 🔥</span>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'rgba(236, 72, 153, 0.1)', color: '#ec4899' }}>🎯</div>
          <div className="stat-info">
            <span className="stat-label">Est. Accuracy</span>
            <span className="stat-value">89%</span>
            <span className="stat-subtext">By plan end</span>
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-icon" style={{ background: 'rgba(139, 92, 246, 0.1)', color: '#8b5cf6' }}>📚</div>
          <div className="stat-info">
            <span className="stat-label">Topics in Plan</span>
            <span className="stat-value">{plan?.tasks?.length || 0}</span>
            <span className="stat-subtext">Focus Areas</span>
          </div>
        </div>
      </section>

      {/* ── MAIN CONTENT GRID ── */}
      <section className="study-main-grid">
        
        {/* LEFT COLUMN: Today's Plan */}
        <div className="plan-panel">
          <div className="panel-header">
            <h2 className="panel-title">Today's Plan</h2>
            <span className="task-count-pill">{totalTasks} Tasks</span>
          </div>

          {isLoading ? (
            <div style={{ padding: '2rem', textAlign: 'center', color: '#6366f1' }}>Loading plan...</div>
          ) : (
            <div className="timeline">
              {plan && plan.tasks.map((task) => {
                const isCompleted = completedTasks.has(task.task_id);
                const isReview = task.task_type === 'Review' || task.task_type === 'Revision';
                
                return (
                  <div key={task.task_id} className={`timeline-item ${isCompleted ? 'completed' : ''}`}>
                    <div className="timeline-time">{task.duration_minutes}m</div>
                    <div className="timeline-dot"></div>
                    
                    <div className="task-content">
                      <div className="task-title">
                        {task.problem ? `${task.topic}: ${task.problem.title}` : task.title}
                      </div>
                      <div className="task-meta">
                        {task.problem?.difficulty && (
                          <span className={`task-difficulty diff-${task.problem.difficulty.toLowerCase()}`}>
                            {task.problem.difficulty}
                          </span>
                        )}
                        <span>•</span>
                        {task.problem?.tags ? (
                          <span>{task.problem.tags.join(', ')}</span>
                        ) : (
                          <span>{task.topic}</span>
                        )}
                      </div>
                    </div>
                    
                    <button 
                      className="task-action-btn"
                      onClick={() => handleStartSolving(task)}
                    >
                      {isCompleted ? 'Completed' : (isReview ? 'Review >' : 'Solve >')}
                    </button>
                  </div>
                );
              })}
            </div>
          )}

          <div className="timeline-actions">
            <button className="btn-start-next">Start Next Task</button>
            <button className="btn-open-leetcode" onClick={() => window.open("https://leetcode.com/problemset/all/", "_blank")}>Open in LeetCode</button>
          </div>
        </div>

        {/* RIGHT COLUMN: Progress & Insights */}
        <div className="right-column">
          
          <div className="progress-panel">
            <div className="progress-panel-header">
              <h2 className="panel-title" style={{margin: 0}}>Plan Progress</h2>
              <span style={{color: '#6366f1', fontSize: '0.85rem', cursor: 'pointer'}}>View Details &gt;</span>
            </div>
            
            <div className="progress-details">
              <div className="progress-ring-container" style={{ width: 120, height: 120 }}>
                <svg className="progress-ring" width="120" height="120">
                  <circle className="progress-ring-circle-bg" cx="60" cy="60" r={radius} />
                  <circle 
                    className="progress-ring-circle" 
                    cx="60" 
                    cy="60" 
                    r={radius} 
                    strokeDasharray={circumference}
                    style={{ strokeDashoffset }}
                  />
                </svg>
                <div className="progress-ring-text">
                  <span className="progress-ring-percent" style={{ fontSize: '1.5rem' }}>{progressPercent}%</span>
                  <span className="progress-ring-label">Overall Progress</span>
                </div>
              </div>
              
              <div style={{ flex: 1, height: '100px' }}>
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={mockChartData}>
                    <Bar dataKey="val" radius={[4, 4, 0, 0]}>
                      {mockChartData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={index === 2 ? '#6366f1' : '#334155'} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '0.5rem', fontSize: '0.65rem', color: '#64748b' }}>
                  <span>Mon</span><span>Tue</span><span>Wed</span><span>Thu</span><span>Fri</span><span>Sat</span><span>Sun</span>
                </div>
              </div>
            </div>
          </div>

          <div className="weak-areas-panel">
            <h2 className="panel-title" style={{marginBottom: '1.5rem'}}>Weak Areas to Improve</h2>
            
            <div className="weak-area-item">
              <div className="weak-area-header">
                <div className="weak-area-label">
                  <div className="weak-area-icon">🧠</div>
                  <span>Dynamic Programming</span>
                </div>
                <span className="weak-area-value">45%</span>
              </div>
              <div className="weak-area-bar-bg">
                <div className="weak-area-bar-fill" style={{width: '45%'}}></div>
              </div>
            </div>

            <div className="weak-area-item">
              <div className="weak-area-header">
                <div className="weak-area-label">
                  <div className="weak-area-icon" style={{background: 'rgba(239, 68, 68, 0.1)', color: '#ef4444'}}>🕸️</div>
                  <span>Graphs</span>
                </div>
                <span className="weak-area-value">35%</span>
              </div>
              <div className="weak-area-bar-bg">
                <div className="weak-area-bar-fill" style={{width: '35%'}}></div>
              </div>
            </div>
          </div>

          <div className="top-tip-panel">
            <h3 className="top-tip-title">Top Tip</h3>
            <p className="top-tip-text">Solve 2-3 more DP problems to boost your accuracy and master overlapping subproblems before the end of this week.</p>
          </div>

        </div>

      </section>

    </div>
  );
}
