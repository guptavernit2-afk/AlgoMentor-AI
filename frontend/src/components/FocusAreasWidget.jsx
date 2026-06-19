import React from 'react';

export default function FocusAreasWidget({ areas }) {
  if (!areas) return null;

  return (
    <div className="focus-areas-list" style={{ marginTop: '1rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
      {areas.map((area, i) => (
        <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <div style={{ width: '32px', height: '32px', borderRadius: '50%', backgroundColor: 'rgba(255,255,255,0.05)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <span style={{ color: 'var(--accent-purple)', fontSize: '1rem' }}>🎯</span>
          </div>
          <div style={{ flex: 1 }}>
            <div style={{ color: 'var(--text-primary)', fontSize: '0.9rem', fontWeight: 500 }}>{area.topic}</div>
            <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>{area.reason}</div>
          </div>
          <div style={{ color: 'var(--text-muted)' }}>&gt;</div>
        </div>
      ))}
    </div>
  );
}
