import React from 'react';

export default function TopicMasteryWidget({ topics }) {
  if (!topics) return null;

  return (
    <div className="topic-mastery-grid" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem', marginTop: '1rem' }}>
      {topics.map((t, i) => {
        const color = getGradientColor(t.percentage);
        const iconData = getTopicIcon(t.topic);
        
        return (
          <div key={i} className="topic-bar-container" style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            {/* Icon Box */}
            <div style={{ 
              width: '40px', 
              height: '40px', 
              borderRadius: '10px', 
              backgroundColor: 'rgba(255,255,255,0.03)', 
              border: '1px solid rgba(255,255,255,0.05)',
              display: 'flex', 
              alignItems: 'center', 
              justifyContent: 'center',
              fontSize: '1.1rem',
              color: color,
              flexShrink: 0
            }}>
              {iconData}
            </div>
            
            {/* Progress Bar Container */}
            <div style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem' }}>
                <span style={{ color: 'var(--text-primary)', fontWeight: 500 }}>{t.topic}</span>
                <span style={{ color: 'var(--text-primary)', fontWeight: 'bold' }}>{t.percentage}%</span>
              </div>
              <div style={{ height: '6px', width: '100%', backgroundColor: 'rgba(255,255,255,0.05)', borderRadius: '3px', overflow: 'hidden' }}>
                <div style={{ height: '100%', width: `${t.percentage}%`, backgroundColor: color, borderRadius: '3px', boxShadow: `0 0 8px ${color}` }} />
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}

function getTopicIcon(topic) {
  const map = {
    'Arrays': '📊',
    'Two Pointers': '⤨',
    'Binary Search': '🔍',
    'Sliding Window': '◫',
    'Dynamic Programming': '🧠',
    'Graphs': '🕸️'
  };
  return map[topic] || '📝';
}

function getGradientColor(percentage) {
  if (percentage > 80) return 'var(--accent-green)';
  if (percentage > 50) return 'var(--accent-indigo)';
  if (percentage > 20) return 'var(--accent-purple)';
  return 'var(--accent-red)';
}
