import React from 'react';
import SmartDailyPlanPanel from '../components/SmartDailyPlanPanel';
import SM2FeedbackWidget from '../components/SM2FeedbackWidget';
import './DashboardView.css';

export default function DashboardView({ setActiveView }) {
  return (
    <div className="layout-view layout-view-padded">
      
      {/* ── 1. Hero Section ── */}
      <section className="dashboard-hero">
        <div className="dashboard-hero-glow" />

        <div className="dashboard-hero-content">
          <p className="dashboard-hero-eyebrow">
            AI + Spaced Revision For DSA
          </p>
          <h1 className="dashboard-hero-title">
            Welcome back,<br/>
            <span>Vernit</span> 👋
          </h1>
          <p className="dashboard-hero-subtitle">
            Your intelligent study companion that adapts to your memory, schedule, and goals to help you master DSA consistently.
          </p>
          <div>
            <button 
              onClick={() => setActiveView('revision')}
              className="dashboard-hero-button"
            >
              View Today's Plan →
            </button>
          </div>
        </div>

        <div className="dashboard-hero-visual">
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
      <section className="dashboard-kpi-grid">
        {[
          { label: 'Study Time Today', value: '120', unit: 'mins', icon: '⏱️', trend: '↑ 20% vs yesterday', color: 'var(--accent-green, #4ade80)', iconBg: 'rgba(59, 130, 246, 0.1)' },
          { label: 'Problems Solved', value: '8', unit: 'problems', icon: '</>', trend: '↑ 33% vs yesterday', color: 'var(--accent-green, #4ade80)', iconBg: 'rgba(16, 185, 129, 0.1)' },
          { label: 'Revision Accuracy', value: '64%', unit: '', icon: '🎯', trend: '↑ 8% vs last week', color: 'var(--accent-green, #4ade80)', iconBg: 'rgba(139, 92, 246, 0.1)' },
          { label: 'Current Streak', value: '7', unit: 'days', icon: '🔥', trend: '🔥 Keep it going!', color: 'var(--accent-orange, #f59e0b)', iconBg: 'rgba(245, 158, 11, 0.1)' }
        ].map((kpi, i) => (
          <div key={i} className="widget-card kpi-card">
            <div className="kpi-header">
              <div className="kpi-icon" style={{ background: kpi.iconBg }}>
                {kpi.icon}
              </div>
              <div className="kpi-info">
                <div className="kpi-label">{kpi.label}</div>
                <div className="kpi-value">
                  {kpi.value} <span className="kpi-unit">{kpi.unit}</span>
                </div>
              </div>
            </div>
            <div className="kpi-trend" style={{ color: kpi.color }}>
              {kpi.trend}
            </div>
          </div>
        ))}
      </section>

      {/* ── 3. Lower Grid (Smart Plan + Memory/Weakness) ── */}
      <section className="dashboard-lower-grid">
        
        {/* Left Column: Smart Daily Plan Panel */}
        <div className="dashboard-lower-left">
          <SmartDailyPlanPanel onProblemSelect={() => setActiveView('workspace')} />
        </div>

        {/* Right Column: Widgets */}
        <div className="dashboard-lower-right">
          
          <SM2FeedbackWidget />

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
