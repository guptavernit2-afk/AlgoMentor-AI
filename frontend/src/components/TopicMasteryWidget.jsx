import React from 'react';

export default function TopicMasteryWidget({ topics }) {
  if (!topics) return null;

  return (
    <div className="topic-mastery-grid" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginTop: '1rem' }}>
      {topics.map((t, i) => (
        <div key={i} className="topic-bar-container" style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem' }}>
            <span style={{ color: 'var(--text-primary)' }}>{t.topic}</span>
            <span style={{ color: 'var(--text-primary)', fontWeight: 'bold' }}>{t.percentage}%</span>
          </div>
          <div style={{ height: '6px', width: '100%', backgroundColor: 'rgba(255,255,255,0.05)', borderRadius: '3px', overflow: 'hidden' }}>
            <div style={{ height: '100%', width: `${t.percentage}%`, backgroundColor: getGradientColor(t.percentage), borderRadius: '3px' }} />
          </div>
        </div>
      ))}
    </div>
  );
}

function getGradientColor(percentage) {
  if (percentage > 80) return 'var(--accent-green)';
  if (percentage > 50) return 'var(--accent-indigo)';
  if (percentage > 20) return 'var(--accent-purple)';
  return 'var(--accent-red)';
}
