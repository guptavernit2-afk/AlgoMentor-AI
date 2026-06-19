import React from 'react';

export default function FocusAreasWidget({ areas }) {
  if (!areas) return null;

  return (
    <div className="focus-areas-list" style={{ marginTop: '1rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
      {areas.map((area, i) => {
        // Use a purple hue for the background circle
        return (
          <div key={i} style={{ display: 'flex', alignItems: 'center', gap: '1rem', cursor: 'pointer', padding: '0.5rem', borderRadius: '12px', transition: 'background 0.2s' }} className="focus-area-item">
            <div style={{ width: '36px', height: '36px', borderRadius: '50%', backgroundColor: 'rgba(139, 92, 246, 0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <div style={{ width: '12px', height: '12px', borderRadius: '50%', border: '2px solid var(--accent-purple)', position: 'relative' }}>
                <div style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)', width: '4px', height: '4px', backgroundColor: 'var(--accent-purple)', borderRadius: '50%' }} />
              </div>
            </div>
            <div style={{ flex: 1 }}>
              <div style={{ color: 'var(--text-primary)', fontSize: '0.9rem', fontWeight: 500 }}>{area.topic}</div>
              <div style={{ color: 'var(--text-muted)', fontSize: '0.75rem' }}>{area.reason}</div>
            </div>
            <div style={{ color: 'var(--text-muted)' }}>&gt;</div>
          </div>
        );
      })}
    </div>
  );
}
