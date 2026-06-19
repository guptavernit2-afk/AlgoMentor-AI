import { useState } from 'react';

export default function ScheduleView() {
  const [collegeSchedule, setCollegeSchedule] = useState('9 AM – 4 PM');
  const [availableTime, setAvailableTime] = useState('1.5 hours');
  const [workload, setWorkload] = useState('Medium');

  return (
    <div className="layout-view layout-view-padded">
      <div className="section-head" style={{ marginBottom: '2rem' }}>
        <div>
          <p className="eyebrow" style={{ color: 'var(--accent-purple)', fontSize: '0.85rem', fontWeight: 600, textTransform: 'uppercase', marginBottom: '0.5rem' }}>Planning Workspace</p>
          <h2 style={{ fontSize: '1.75rem', margin: '0 0 0.5rem 0', color: 'var(--text-primary)' }}>Schedule & Workload</h2>
          <p style={{ color: 'var(--text-secondary)' }}>Manage your weekly availability and apply daily overrides.</p>
        </div>
      </div>

      {/* ── Weekly Schedule Setup (Mock) ── */}
      <section style={{ background: 'var(--bg-card)', border: '1px solid var(--border-light)', borderRadius: 'var(--radius-lg)', padding: '2rem', marginBottom: '2rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
          <h3 style={{ margin: 0, fontSize: '1.2rem', color: 'var(--text-primary)' }}>Weekly Base Schedule</h3>
          <span style={{ fontSize: '0.75rem', background: 'rgba(59, 130, 246, 0.1)', color: 'var(--accent-blue)', padding: '0.25rem 0.75rem', borderRadius: '12px', fontWeight: 600 }}>Active</span>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1.5rem' }}>
          <div className="setup-field">
            <label style={{ display: 'block', fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>College Schedule</label>
            <input 
              value={collegeSchedule} 
              onChange={e => setCollegeSchedule(e.target.value)}
              style={{ width: '100%', padding: '0.75rem', background: 'var(--bg-dark)', border: '1px solid var(--border-strong)', borderRadius: 'var(--radius-sm)', color: 'var(--text-primary)' }}
            />
          </div>
          <div className="setup-field">
            <label style={{ display: 'block', fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>Base Target Time</label>
            <select 
              value={availableTime} 
              onChange={e => setAvailableTime(e.target.value)}
              style={{ width: '100%', padding: '0.75rem', background: 'var(--bg-dark)', border: '1px solid var(--border-strong)', borderRadius: 'var(--radius-sm)', color: 'var(--text-primary)' }}
            >
              <option>30 minutes</option>
              <option>1 hour</option>
              <option>1.5 hours</option>
              <option>2+ hours</option>
            </select>
          </div>
          <div className="setup-field">
            <label style={{ display: 'block', fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>Base Workload</label>
            <select 
              value={workload} 
              onChange={e => setWorkload(e.target.value)}
              style={{ width: '100%', padding: '0.75rem', background: 'var(--bg-dark)', border: '1px solid var(--border-strong)', borderRadius: 'var(--radius-sm)', color: 'var(--text-primary)' }}
            >
              <option>Low</option>
              <option>Medium</option>
              <option>High</option>
            </select>
          </div>
        </div>
        <div style={{ marginTop: '1.5rem', paddingTop: '1.5rem', borderTop: '1px solid var(--border-light)', display: 'flex', justifyContent: 'flex-end' }}>
          <button style={{ background: 'var(--accent-indigo)', color: 'white', border: 'none', padding: '0.75rem 1.5rem', borderRadius: 'var(--radius-sm)', fontWeight: 600, cursor: 'pointer' }}>
            Save Base Schedule
          </button>
        </div>
      </section>

    </div>
  );
}
