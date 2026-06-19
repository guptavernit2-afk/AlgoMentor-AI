import React from 'react';

export default function AchievementsWidget() {
  const achievements = [
    { title: 'Streak Master', desc: '7 Day Streak', icon: '🔥', color: 'var(--accent-orange)' },
    { title: 'Problem Solver', desc: '500+ Solved', icon: '🧩', color: 'var(--accent-indigo)' },
    { title: 'Accuracy Pro', desc: '90%+ Accuracy', icon: '🎯', color: 'var(--accent-blue)' },
    { title: 'Dedication', desc: '100+ Hours', icon: '🏆', color: 'var(--accent-yellow)' },
  ];

  return (
    <div style={{ display: 'flex', gap: '1.5rem', marginTop: '1rem', overflowX: 'auto', paddingBottom: '0.5rem' }}>
      {achievements.map((ach, i) => (
        <div key={i} style={{ 
          minWidth: '120px', 
          display: 'flex', 
          flexDirection: 'column', 
          alignItems: 'center', 
          gap: '0.5rem',
          padding: '1rem',
          backgroundColor: 'rgba(255,255,255,0.02)',
          border: '1px solid rgba(255,255,255,0.05)',
          borderRadius: '12px'
        }}>
          {/* Hexagon shape roughly */}
          <div style={{ 
            width: '60px', 
            height: '60px', 
            backgroundColor: 'rgba(255,255,255,0.05)', 
            border: `2px solid ${ach.color}`, 
            borderRadius: '16px', // Rounded square looks similar to hex in small
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'center',
            fontSize: '1.5rem',
            transform: 'rotate(45deg)'
          }}>
            <div style={{ transform: 'rotate(-45deg)' }}>{ach.icon}</div>
          </div>
          
          <div style={{ textAlign: 'center', marginTop: '0.5rem' }}>
            <div style={{ color: ach.color, fontSize: '0.8rem', fontWeight: 600 }}>{ach.title}</div>
            <div style={{ color: 'var(--text-muted)', fontSize: '0.7rem' }}>{ach.desc}</div>
          </div>
        </div>
      ))}
    </div>
  );
}
