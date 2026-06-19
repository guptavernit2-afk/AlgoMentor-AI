import { useState, useEffect } from 'react';
import CheckInModal from '../components/CheckInModal';
import ActivityGraph from '../components/ActivityGraph';
import AccuracyChart from '../components/AccuracyChart';
import WeeklyHoursChart from '../components/WeeklyHoursChart';
import TopicMasteryWidget from '../components/TopicMasteryWidget';
import StudyCalendarWidget from '../components/StudyCalendarWidget';
import FocusAreasWidget from '../components/FocusAreasWidget';
import AchievementsWidget from '../components/AchievementsWidget';
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
    <div className="layout-view layout-view-padded dashboard-container">
      
      {/* ── 1. Profile / Hero Section ── */}
      <section className="dashboard-hero">
        <div style={{ flex: 1 }}>
          <h1 className="hero-title">Welcome back, Vernit! 👋</h1>
          <p className="hero-subtitle">Keep up the momentum, you're doing great!</p>
        </div>
      </section>

      {/* ── 2. Top KPIs (5 cards) ── */}
      <section className="dashboard-kpi-grid">
        <div className="widget-card kpi-card">
          <div className="kpi-header">
            <div className="kpi-icon" style={{ background: 'rgba(236, 72, 153, 0.1)' }}>🎯</div>
            <div className="kpi-info">
              <div className="kpi-label">Problems Solved</div>
              <div className="kpi-value">
                {progressData ? progressData.stats.total_solved : '...'} <span className="kpi-unit">/ 1000</span>
              </div>
            </div>
          </div>
          <div className="kpi-progress-bar-container">
            <div className="kpi-progress-bar-segment" style={{ width: '50%', background: 'var(--accent-green)' }} />
            <div className="kpi-progress-bar-segment" style={{ width: '40%', background: 'var(--accent-indigo)' }} />
            <div className="kpi-progress-bar-segment" style={{ width: '10%', background: 'var(--accent-red)' }} />
          </div>
          <div className="kpi-difficulty-text">
            <span style={{ color: 'var(--accent-green)' }}>Easy {progressData?.stats.difficulty_counts.Easy}</span> • 
            <span style={{ color: 'var(--accent-indigo)' }}>Med {progressData?.stats.difficulty_counts.Medium}</span> • 
            <span style={{ color: 'var(--accent-red)' }}>Hard {progressData?.stats.difficulty_counts.Hard}</span>
          </div>
        </div>

        <div className="widget-card kpi-card">
          <div className="kpi-header">
            <div className="kpi-icon" style={{ background: 'rgba(249, 115, 22, 0.1)' }}>🔥</div>
            <div className="kpi-info">
              <div className="kpi-label">Current Streak</div>
              <div className="kpi-value">
                {progressData ? progressData.stats.current_streak : '...'} <span className="kpi-unit">days</span>
              </div>
            </div>
          </div>
          <div className="kpi-trend" style={{ color: 'var(--accent-orange)' }}>
            Keep it going! 🔥
          </div>
        </div>

        <div className="widget-card kpi-card">
          <div className="kpi-header">
            <div className="kpi-icon" style={{ background: 'rgba(59, 130, 246, 0.1)' }}>🎯</div>
            <div className="kpi-info">
              <div className="kpi-label">Accuracy</div>
              <div className="kpi-value">
                {progressData ? progressData.stats.memory_retention_percent : '...'}%
              </div>
            </div>
          </div>
          <div className="kpi-trend" style={{ color: 'var(--accent-green)' }}>
            ↑ 12% vs last month
          </div>
        </div>

        <div className="widget-card kpi-card">
          <div className="kpi-header">
            <div className="kpi-icon" style={{ background: 'rgba(234, 179, 8, 0.1)' }}>⏱️</div>
            <div className="kpi-info">
              <div className="kpi-label">Study Time</div>
              <div className="kpi-value">
                {progressData ? progressData.stats.study_time_hours : '...'}h
              </div>
            </div>
          </div>
          <div className="kpi-trend" style={{ color: 'var(--accent-green)' }}>
            ↑ 12h vs last month
          </div>
        </div>

        <div className="widget-card kpi-card" style={{ background: 'linear-gradient(135deg, rgba(30,27,75,0.8), rgba(88,28,135,0.2))' }}>
          <div className="kpi-header">
            <div className="kpi-icon" style={{ background: 'rgba(234, 179, 8, 0.2)' }}>🏆</div>
            <div className="kpi-info">
              <div className="kpi-label">Rank</div>
              <div className="kpi-value" style={{ fontSize: '1.5rem' }}>
                {progressData ? progressData.stats.rank.split('-')[0].trim() : '...'}
              </div>
            </div>
          </div>
          <div className="kpi-trend" style={{ color: 'var(--accent-purple)' }}>
            {progressData ? progressData.stats.rank.split('-')[1].trim() : '...'} ✪
          </div>
        </div>
      </section>

      {/* ── 3. Main Data Grid ── */}
      <section className="dashboard-main-grid">
        
        {/* Row 2: Activity (Span 2) | Accuracy Trend (Span 1) | Study Calendar (Span 1) */}
        <div className="widget-card col-span-2">
          <div className="widget-header">
            <h3 className="widget-title">Activity Overview</h3>
          </div>
          <ActivityGraph activityData={progressData?.activity_graph} totalSolved={progressData?.stats.total_solved} />
        </div>
        
        <div className="widget-card">
          <div className="widget-header">
            <h3 className="widget-title">Accuracy Trend <span style={{fontSize:'0.75rem', color:'var(--text-muted)', fontWeight:'normal'}}>(30 Days)</span></h3>
          </div>
          <AccuracyChart data={progressData?.accuracy_trend} />
        </div>

        <div className="widget-card">
          <div className="widget-header">
            <h3 className="widget-title">Study Calendar</h3>
          </div>
          <StudyCalendarWidget />
        </div>

        {/* Row 3: Topic Mastery (Span 2) | Focus Areas (Span 1) | Weekly Hours (Span 1) */}
        <div className="widget-card col-span-2">
          <div className="widget-header">
            <h3 className="widget-title">Topic Mastery</h3>
          </div>
          <TopicMasteryWidget topics={progressData?.topic_mastery} />
        </div>

        <div className="widget-card">
          <div className="widget-header">
            <h3 className="widget-title">Focus Areas</h3>
            <span className="widget-action">View All</span>
          </div>
          <FocusAreasWidget areas={progressData?.focus_areas} />
        </div>

        <div className="widget-card">
          <div className="widget-header">
            <h3 className="widget-title">Weekly Study Hours</h3>
          </div>
          <div style={{ display: 'flex', alignItems: 'flex-end', gap: '0.5rem', marginTop: '0.5rem' }}>
            <span style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--text-primary)' }}>28.4h</span>
            <span style={{ color: 'var(--accent-green)', fontSize: '0.75rem', marginBottom: '0.2rem' }}>↑ 6.2h vs last week</span>
          </div>
          <WeeklyHoursChart data={progressData?.study_hours} />
        </div>

        {/* Row 4: Recent Problems (Span 2) | Achievements (Span 2) */}
        <div className="widget-card col-span-2">
          <div className="widget-header">
            <h3 className="widget-title">Recent Problems Solved</h3>
            <span className="widget-action">View All</span>
          </div>
          
          {/* Simple table for recent problems */}
          <table style={{ width: '100%', marginTop: '1rem', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
            <tbody>
              {['Trapping Rain Water', 'Kth Largest Element in Array', 'Valid Anagram'].map((title, i) => (
                <tr key={i} style={{ borderBottom: i < 2 ? '1px solid var(--border-light)' : 'none' }}>
                  <td style={{ padding: '0.75rem 0', color: 'var(--accent-green)' }}>✔</td>
                  <td style={{ padding: '0.75rem 0', color: 'var(--text-primary)' }}>{title}</td>
                  <td style={{ padding: '0.75rem 0' }}>
                    <span style={{ 
                      fontSize: '0.7rem', 
                      padding: '0.1rem 0.4rem', 
                      borderRadius: '4px', 
                      backgroundColor: i === 0 ? 'rgba(239,68,68,0.1)' : i === 1 ? 'rgba(245,158,11,0.1)' : 'rgba(34,197,94,0.1)',
                      color: i === 0 ? 'var(--accent-red)' : i === 1 ? 'var(--accent-yellow)' : 'var(--accent-green)'
                    }}>
                      {i === 0 ? 'Hard' : i === 1 ? 'Medium' : 'Easy'}
                    </span>
                  </td>
                  <td style={{ padding: '0.75rem 0', color: 'var(--accent-purple)', fontSize: '0.75rem' }}>{i === 0 ? 'Two Pointers' : i === 1 ? 'Heap' : 'Hash Table'}</td>
                  <td style={{ padding: '0.75rem 0', color: 'var(--text-muted)', textAlign: 'right' }}>{i === 0 ? '24 min ago' : i === 1 ? '1 hr ago' : '2 hr ago'}</td>
                  <td style={{ padding: '0.75rem 0', color: 'var(--text-primary)', fontWeight: 'bold', textAlign: 'right' }}>{i === 0 ? '92%' : i === 1 ? '88%' : '100%'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="widget-card col-span-2">
          <div className="widget-header">
            <h3 className="widget-title">Achievements</h3>
            <span className="widget-action">View All</span>
          </div>
          <AchievementsWidget />
        </div>

      </section>

      {showCheckInModal && (
        <CheckInModal 
          onComplete={handleCheckInComplete} 
          onSkip={handleCheckInSkip}
        />
      )}
    </div>
  );
}
