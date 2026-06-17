import React from 'react';

export default function AnalyticsView() {
  return (
    <div className="layout-view layout-view-padded">
      <div className="section-head" style={{ marginBottom: '2rem' }}>
        <div>
          <p className="eyebrow" style={{ color: 'var(--accent-blue)', fontSize: '0.85rem', fontWeight: 600, textTransform: 'uppercase', marginBottom: '0.5rem' }}>Performance Metrics</p>
          <h2 style={{ fontSize: '1.75rem', margin: '0 0 0.5rem 0', color: 'var(--text-primary)' }}>Analytics Dashboard</h2>
          <p style={{ color: 'var(--text-secondary)' }}>Track your spaced repetition efficiency and problem solving trends.</p>
        </div>
      </div>

      {/* ── Top KPIs ── */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1.5rem', marginBottom: '2rem' }}>
        {[
          { label: 'Total Study Time', val: '142h', desc: '+12h this month', color: 'var(--accent-indigo)' },
          { label: 'Avg Accuracy', val: '89%', desc: 'SM-2 Recall Score', color: 'var(--accent-green)' },
          { label: 'Longest Streak', val: '28 Days', desc: 'Personal Best', color: 'var(--accent-purple)' },
          { label: 'Topics Mastered', val: '14/32', desc: '43% Completion', color: 'var(--accent-blue)' }
        ].map((kpi, i) => (
          <div key={i} style={{ background: 'var(--bg-card)', border: '1px solid var(--border-light)', borderRadius: 'var(--radius-md)', padding: '1.25rem' }}>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>{kpi.label}</div>
            <div style={{ fontSize: '1.75rem', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '0.25rem' }}>{kpi.val}</div>
            <div style={{ fontSize: '0.75rem', color: kpi.color }}>{kpi.desc}</div>
          </div>
        ))}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '1.5rem', marginBottom: '2rem' }}>
        {/* ── Study Time Bar Chart (CSS mock) ── */}
        <div style={{ background: 'var(--bg-card)', border: '1px solid var(--border-light)', borderRadius: 'var(--radius-lg)', padding: '1.5rem' }}>
          <h3 style={{ fontSize: '1.1rem', margin: '0 0 1.5rem 0', color: 'var(--text-primary)' }}>Weekly Study Hours</h3>
          <div style={{ display: 'flex', height: '200px', alignItems: 'flex-end', gap: '1rem', borderBottom: '1px solid var(--border-strong)', paddingBottom: '0.5rem' }}>
            {[45, 60, 30, 80, 50, 90, 75].map((h, i) => (
              <div key={i} style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0.5rem' }}>
                <div style={{ width: '100%', background: i === 5 ? 'var(--accent-indigo)' : 'rgba(99, 102, 241, 0.2)', height: `${h}%`, borderRadius: '4px 4px 0 0', transition: 'height 0.5s ease' }} />
                <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{['Mon','Tue','Wed','Thu','Fri','Sat','Sun'][i]}</span>
              </div>
            ))}
          </div>
        </div>

        {/* ── Topic Mastery ── */}
        <div style={{ background: 'var(--bg-card)', border: '1px solid var(--border-light)', borderRadius: 'var(--radius-lg)', padding: '1.5rem' }}>
          <h3 style={{ fontSize: '1.1rem', margin: '0 0 1.5rem 0', color: 'var(--text-primary)' }}>Topic Mastery</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {[
              { topic: 'Arrays', pct: 95 },
              { topic: 'Two Pointers', pct: 82 },
              { topic: 'Sliding Window', pct: 60 },
              { topic: 'Binary Search', pct: 45 },
            ].map((t, i) => (
              <div key={i}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', marginBottom: '0.25rem' }}>
                  <span style={{ color: 'var(--text-secondary)' }}>{t.topic}</span>
                  <span style={{ color: 'var(--text-primary)', fontWeight: 600 }}>{t.pct}%</span>
                </div>
                <div style={{ width: '100%', background: 'var(--bg-dark)', height: '8px', borderRadius: '4px', overflow: 'hidden' }}>
                  <div style={{ width: `${t.pct}%`, background: t.pct > 80 ? 'var(--accent-green)' : t.pct > 50 ? 'var(--accent-blue)' : 'var(--accent-purple)', height: '100%' }} />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* ── Consistency Heatmap (Mock) ── */}
      <div style={{ background: 'var(--bg-card)', border: '1px solid var(--border-light)', borderRadius: 'var(--radius-lg)', padding: '1.5rem' }}>
        <h3 style={{ fontSize: '1.1rem', margin: '0 0 1.5rem 0', color: 'var(--text-primary)' }}>Consistency Heatmap</h3>
        <div style={{ display: 'flex', gap: '4px', flexWrap: 'wrap' }}>
          {Array.from({ length: 90 }).map((_, i) => {
            const intensity = Math.random();
            let color = 'var(--bg-dark)';
            if (intensity > 0.8) color = 'var(--accent-indigo)';
            else if (intensity > 0.5) color = 'rgba(99, 102, 241, 0.6)';
            else if (intensity > 0.2) color = 'rgba(99, 102, 241, 0.3)';
            
            return (
              <div key={i} style={{ width: '14px', height: '14px', borderRadius: '3px', background: color }} title={`Day ${i}`} />
            );
          })}
        </div>
        <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center', marginTop: '1rem', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
          <span>Less</span>
          <div style={{ display: 'flex', gap: '4px' }}>
            <div style={{ width: '12px', height: '12px', borderRadius: '2px', background: 'var(--bg-dark)' }} />
            <div style={{ width: '12px', height: '12px', borderRadius: '2px', background: 'rgba(99, 102, 241, 0.3)' }} />
            <div style={{ width: '12px', height: '12px', borderRadius: '2px', background: 'rgba(99, 102, 241, 0.6)' }} />
            <div style={{ width: '12px', height: '12px', borderRadius: '2px', background: 'var(--accent-indigo)' }} />
          </div>
          <span>More</span>
        </div>
      </div>
    </div>
  );
}
