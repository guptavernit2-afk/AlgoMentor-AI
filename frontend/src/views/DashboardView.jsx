import React from 'react';
import SmartDailyPlanPanel from '../components/SmartDailyPlanPanel';

export default function DashboardView({ setActiveView }) {
  return (
    <div className="layout-view layout-view-padded">
      
      {/* ── 1. Hero Section ── */}
      <section style={{ 
        display: 'flex', 
        flexWrap: 'wrap',
        alignItems: 'center',
        gap: '2rem',
        background: 'linear-gradient(135deg, rgba(31, 41, 55, 0.4), rgba(15, 23, 42, 0.6))',
        border: '1px solid var(--border-light)',
        borderRadius: 'var(--radius-xl)',
        padding: '2rem',
        position: 'relative',
        overflow: 'hidden',
        marginBottom: '1.5rem'
      }}>
        <div style={{ position: 'absolute', top: '-50%', left: '-10%', width: '300px', height: '300px', background: 'radial-gradient(circle, rgba(99, 102, 241, 0.15) 0%, transparent 70%)', borderRadius: '50%' }} />

        <div style={{ zIndex: 1, minWidth: '300px', flex: '1 1 400px', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
          <p style={{ color: 'var(--accent-indigo)', fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '1rem' }}>
            AI + Spaced Revision For DSA
          </p>
          <h1 style={{ fontSize: '2.5rem', margin: '0 0 1rem 0', fontWeight: 700, color: 'var(--text-primary)', lineHeight: 1.2 }}>
            Welcome back,<br/>
            <span style={{ color: 'var(--accent-indigo)' }}>Vernit</span> 👋
          </h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.95rem', lineHeight: 1.6, marginBottom: '2rem' }}>
            Your intelligent study companion that adapts to your memory, schedule, and goals to help you master DSA consistently.
          </p>
          <div>
            <button 
              onClick={() => setActiveView('revision')}
              style={{ background: 'var(--accent-indigo)', color: 'white', border: 'none', padding: '0.85rem 1.5rem', borderRadius: 'var(--radius-sm)', fontWeight: 600, cursor: 'pointer', display: 'inline-flex', alignItems: 'center', gap: '0.5rem', transition: 'background 0.2s', boxShadow: '0 4px 14px rgba(99, 102, 241, 0.4)' }}
            >
              View Today's Plan →
            </button>
          </div>
        </div>

        <div style={{ zIndex: 1, position: 'relative', display: 'flex', alignItems: 'center', justifyContent: 'center', width: '280px', margin: '0 auto' }}>
          <div style={{ position: 'absolute', width: '220px', height: '220px', borderRadius: '50% 50% 10% 10%', border: '2px solid rgba(99, 102, 241, 0.3)', background: 'linear-gradient(180deg, rgba(99, 102, 241, 0.05) 0%, rgba(99, 102, 241, 0.01) 100%)', boxShadow: 'inset 0 10px 30px rgba(99, 102, 241, 0.2), 0 0 40px rgba(99, 102, 241, 0.1)', top: '10%' }}></div>
          <div style={{ position: 'absolute', width: '260px', height: '10px', background: 'rgba(99, 102, 241, 0.2)', borderRadius: '50%', bottom: '15%', filter: 'blur(4px)' }}></div>
          <div style={{ position: 'absolute', width: '240px', height: '14px', border: '2px solid rgba(99, 102, 241, 0.4)', borderRadius: '50%', bottom: '15%' }}></div>
          
          <svg width="180" height="180" viewBox="0 0 100 100" style={{ filter: 'drop-shadow(0 0 15px rgba(99, 102, 241, 0.6))', position: 'relative', top: '-5%' }}>
            <defs>
              <linearGradient id="brainGrad2" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#818cf8" />
                <stop offset="100%" stopColor="#6366f1" />
              </linearGradient>
            </defs>
            <path d="M50 20 C30 20 15 35 15 55 C15 75 30 90 50 90" fill="none" stroke="url(#brainGrad2)" strokeWidth="1.5" opacity="0.8" />
            <path d="M50 30 C35 30 25 40 25 55 C25 70 35 80 50 80" fill="none" stroke="url(#brainGrad2)" strokeWidth="1.5" opacity="0.5" />
            <path d="M50 20 C70 20 85 35 85 55 C85 75 70 90 50 90" fill="none" stroke="url(#brainGrad2)" strokeWidth="1.5" opacity="0.8" />
            <path d="M50 30 C65 30 75 40 75 55 C75 70 65 80 50 80" fill="none" stroke="url(#brainGrad2)" strokeWidth="1.5" opacity="0.5" />
            
            <circle cx="35" cy="45" r="2" fill="#818cf8" />
            <circle cx="65" cy="45" r="2" fill="#818cf8" />
            <circle cx="50" cy="65" r="2.5" fill="#a5b4fc" />
            <circle cx="30" cy="70" r="1.5" fill="#818cf8" />
            <circle cx="70" cy="70" r="1.5" fill="#818cf8" />
            
            <line x1="35" y1="45" x2="65" y2="45" stroke="#818cf8" strokeWidth="1" strokeDasharray="2 2" opacity="0.6" />
            <line x1="35" y1="45" x2="50" y2="65" stroke="#a5b4fc" strokeWidth="1" opacity="0.8" />
            <line x1="65" y1="45" x2="50" y2="65" stroke="#a5b4fc" strokeWidth="1" opacity="0.8" />
          </svg>
        </div>
      </section>

      {/* ── 2. KPI Cards ── */}
      <section style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1.5rem', marginBottom: '1.5rem' }}>
        {[
          { label: 'Study Time Today', value: '120', unit: 'mins', icon: '⏱️', trend: '↑ 20% vs yesterday', color: 'var(--accent-green)', iconBg: 'rgba(59, 130, 246, 0.1)' },
          { label: 'Problems Solved', value: '8', unit: 'problems', icon: '</>', trend: '↑ 33% vs yesterday', color: 'var(--accent-green)', iconBg: 'rgba(16, 185, 129, 0.1)' },
          { label: 'Revision Accuracy', value: '64%', unit: '', icon: '🎯', trend: '↑ 8% vs last week', color: 'var(--accent-green)', iconBg: 'rgba(139, 92, 246, 0.1)' },
          { label: 'Current Streak', value: '7', unit: 'days', icon: '🔥', trend: '🔥 Keep it going!', color: 'var(--accent-orange)', iconBg: 'rgba(245, 158, 11, 0.1)' }
        ].map((kpi, i) => (
          <div key={i} className="widget-card" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
            <div style={{ display: 'flex', alignItems: 'flex-start', gap: '1rem' }}>
              <div style={{ fontSize: '1.25rem', background: kpi.iconBg, width: '48px', height: '48px', display: 'flex', alignItems: 'center', justifyContent: 'center', borderRadius: '50%' }}>
                {kpi.icon}
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '0.25rem' }}>{kpi.label}</div>
                <div style={{ fontSize: '1.75rem', fontWeight: 700, color: 'var(--text-primary)', display: 'flex', alignItems: 'baseline', gap: '0.25rem' }}>
                  {kpi.value} <span style={{ fontSize: '0.85rem', fontWeight: 400, color: 'var(--text-muted)' }}>{kpi.unit}</span>
                </div>
              </div>
            </div>
            <div style={{ fontSize: '0.75rem', fontWeight: 500, color: kpi.color, marginTop: '1rem', paddingTop: '0.75rem', borderTop: '1px solid var(--border-light)' }}>
              {kpi.trend}
            </div>
          </div>
        ))}
      </section>

      {/* ── 3. Lower Grid (Smart Plan + Memory/Weakness) ── */}
      <section style={{ display: 'flex', flexWrap: 'wrap', gap: '1.5rem' }}>
        
        {/* Left Column: Smart Daily Plan Panel */}
        <div style={{ flex: '1 1 600px', minWidth: 0 }}>
          <SmartDailyPlanPanel />
        </div>

        {/* Right Column: Widgets */}
        <div style={{ flex: '1 1 300px', minWidth: 0, display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          
          {/* Memory Health Widget */}
          <div className="widget-card">
            <div className="widget-header">
              <h3 className="widget-title">Memory Health</h3>
              <a className="widget-action">View Details →</a>
            </div>
            
            <div className="circular-progress">
              <svg viewBox="0 0 120 120">
                <defs>
                  <linearGradient id="memoryGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                    <stop offset="0%" stopColor="var(--accent-orange)" />
                    <stop offset="100%" stopColor="var(--accent-purple)" />
                  </linearGradient>
                </defs>
                <circle className="progress-bg" cx="60" cy="60" r="50" />
                <circle className="progress-value" cx="60" cy="60" r="50" />
              </svg>
              <div className="progress-text">
                <span className="progress-percent">64%</span>
                <span className="progress-label">Medium Risk</span>
              </div>
            </div>

            <div className="memory-health-status">
              <h4>Requires regular revision</h4>
              <p>Focus on weak concepts</p>
            </div>
          </div>

          {/* Weak Concepts Widget */}
          <div className="widget-card" style={{ flex: 1 }}>
            <div className="widget-header">
              <h3 className="widget-title">Weak Concepts</h3>
              <a className="widget-action">View All →</a>
            </div>

            <div className="weak-concept-list">
              <div className="weak-concept-item">
                <div className="wc-info">
                  <span className="wc-icon">🎯</span>
                  <span className="wc-name">Binary Search</span>
                </div>
                <span className="wc-status">2 days overdue</span>
              </div>
              <div className="weak-concept-item">
                <div className="wc-info">
                  <span className="wc-icon">🔄</span>
                  <span className="wc-name">Recursion</span>
                </div>
                <span className="wc-status">Fading fast</span>
              </div>
              <div className="weak-concept-item">
                <div className="wc-info">
                  <span className="wc-icon">🌳</span>
                  <span className="wc-name">Tree Traversals</span>
                </div>
                <span className="wc-status healthy">Recovering</span>
              </div>
            </div>
          </div>

        </div>

      </section>

    </div>
  );
}
