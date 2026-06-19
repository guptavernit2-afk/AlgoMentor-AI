import { useState, useEffect } from 'react';
import CheckInModal from '../components/CheckInModal';
import ActivityGraph from '../components/ActivityGraph';
import { getDailyPlan, getUserProgress, DEMO_USER_ID } from '../services/api';
import './DashboardView.css';

function todayISO() {
  const d = new Date();
  const yyyy = d.getFullYear();
  const mm = String(d.getMonth() + 1).padStart(2, '0');
  const dd = String(d.getDate()).padStart(2, '0');
  return `${yyyy}-${mm}-${dd}`;
}

export default function DashboardView({ setActiveView }) {
  const [showCheckInModal, setShowCheckInModal] = useState(false);
  const [progressData, setProgressData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const [plan, progress] = await Promise.all([
          getDailyPlan(DEMO_USER_ID, todayISO()).catch(() => null),
          getUserProgress(DEMO_USER_ID).catch(() => null)
        ]);
        
        if (plan && !plan.override_applied) {
          setShowCheckInModal(true);
        }
        
        if (progress) {
          setProgressData(progress);
        }
      } catch (err) {
        console.warn("Failed to fetch dashboard data", err);
      } finally {
        setIsLoading(false);
      }
    }
    fetchData();
  }, []);

  const handleCheckInComplete = () => setShowCheckInModal(false);
  const handleCheckInSkip = () => setShowCheckInModal(false);

  return (
    <div className="layout-view layout-view-padded">
      
      {/* ── 1. Profile / Hero Section ── */}
      <section className="dashboard-hero" style={{ padding: '2rem', display: 'flex', gap: '2rem', alignItems: 'center', background: 'var(--bg-card)', border: '1px solid var(--border-light)', borderRadius: 'var(--radius-lg)' }}>
        <div style={{ position: 'relative' }}>
          <img src="https://i.pravatar.cc/150?u=vernit" alt="Profile" style={{ width: '100px', height: '100px', borderRadius: '50%', border: '4px solid var(--bg-dark)' }} />
          <div style={{ position: 'absolute', bottom: 0, right: 0, background: 'var(--accent-green)', width: '20px', height: '20px', borderRadius: '50%', border: '3px solid var(--bg-card)' }}></div>
        </div>
        <div style={{ flex: 1 }}>
          <h1 style={{ margin: '0 0 0.5rem 0', fontSize: '1.75rem', color: 'var(--text-primary)' }}>Vernit Gupta</h1>
          <p style={{ margin: '0 0 1.25rem 0', color: 'var(--text-secondary)', fontSize: '0.95rem' }}>Top 5% · 124 Day Streak · Master Rank</p>
          <div style={{ display: 'flex', gap: '1rem' }}>
            <button 
              onClick={() => setActiveView('revision')}
              className="btn-primary"
              style={{ background: 'var(--accent-indigo)', color: 'white', border: 'none', padding: '0.6rem 1.2rem', borderRadius: 'var(--radius-md)', fontWeight: 600, cursor: 'pointer' }}
            >
              View Today's Study Plan →
            </button>
            <button 
              style={{ background: 'transparent', color: 'var(--text-primary)', border: '1px solid var(--border-strong)', padding: '0.6rem 1.2rem', borderRadius: 'var(--radius-md)', fontWeight: 500, cursor: 'pointer' }}
            >
              Edit Profile
            </button>
          </div>
        </div>
      </section>

      {/* ── 2. Progress Report (KPI Cards) ── */}
      <section className="dashboard-kpi-grid" style={{ marginTop: '2rem' }}>
        <div className="widget-card kpi-card">
          <div className="kpi-header">
            <div className="kpi-icon" style={{ background: 'rgba(59, 130, 246, 0.1)' }}>🎯</div>
            <div className="kpi-info">
              <div className="kpi-label">Total Solved</div>
              <div className="kpi-value">
                {progressData ? progressData.stats.total_solved : '...'} <span className="kpi-unit">/ 1000</span>
              </div>
            </div>
          </div>
          <div style={{ marginTop: '1rem', display: 'flex', gap: '0.5rem', fontSize: '0.75rem' }}>
            <span style={{ color: 'var(--accent-green)' }}>Easy: {progressData ? progressData.stats.difficulty_counts.Easy : '-'}</span> • 
            <span style={{ color: 'var(--accent-yellow)' }}>Med: {progressData ? progressData.stats.difficulty_counts.Medium : '-'}</span> • 
            <span style={{ color: 'var(--accent-red)' }}>Hard: {progressData ? progressData.stats.difficulty_counts.Hard : '-'}</span>
          </div>
        </div>

        <div className="widget-card kpi-card">
          <div className="kpi-header">
            <div className="kpi-icon" style={{ background: 'rgba(245, 158, 11, 0.1)' }}>🔥</div>
            <div className="kpi-info">
              <div className="kpi-label">Current Streak</div>
              <div className="kpi-value">
                {progressData ? progressData.stats.current_streak : '...'} <span className="kpi-unit">days</span>
              </div>
            </div>
          </div>
          <div className="kpi-trend" style={{ color: 'var(--accent-orange)' }}>
            You're in the top 1% of active learners!
          </div>
        </div>

        <div className="widget-card kpi-card">
          <div className="kpi-header">
            <div className="kpi-icon" style={{ background: 'rgba(139, 92, 246, 0.1)' }}>🧠</div>
            <div className="kpi-info">
              <div className="kpi-label">Memory Retention</div>
              <div className="kpi-value">
                {progressData ? progressData.stats.memory_retention_percent : '...'}% <span className="kpi-unit"></span>
              </div>
            </div>
          </div>
          <div className="kpi-trend" style={{ color: 'var(--accent-green)' }}>
            ↑ 2% vs last month
          </div>
        </div>
      </section>

      {/* ── 3. Lower Grid (Activity Graph) ── */}
      <section className="dashboard-lower-grid" style={{ marginTop: '2rem' }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          <ActivityGraph activityData={progressData?.activity_graph} totalSolved={progressData?.stats.total_solved} />
        </div>
      </section>

      {showCheckInModal && (
        <CheckInModal 
          onClose={handleCheckInSkip} 
          onComplete={handleCheckInComplete} 
        />
      )}

    </div>
  );
}
