import React from 'react';

export default function SettingsView() {
  return (
    <div className="layout-view layout-view-padded">
      <div className="section-head" style={{ marginBottom: '2rem' }}>
        <div>
          <p className="eyebrow" style={{ color: 'var(--text-muted)', fontSize: '0.85rem', fontWeight: 600, textTransform: 'uppercase', marginBottom: '0.5rem' }}>Preferences</p>
          <h2 style={{ fontSize: '1.75rem', margin: '0 0 0.5rem 0', color: 'var(--text-primary)' }}>Account Settings</h2>
          <p style={{ color: 'var(--text-secondary)' }}>Manage your personal profile, learning goals, and notifications.</p>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '2rem', maxWidth: '800px' }}>
        
        {/* ── Profile Information ── */}
        <section style={{ background: 'var(--bg-card)', border: '1px solid var(--border-light)', borderRadius: 'var(--radius-lg)', padding: '2rem' }}>
          <h3 style={{ fontSize: '1.1rem', margin: '0 0 1.5rem 0', color: 'var(--text-primary)', borderBottom: '1px solid var(--border-light)', paddingBottom: '0.75rem' }}>Profile Information</h3>
          
          <div style={{ display: 'flex', gap: '2rem', alignItems: 'center', marginBottom: '2rem' }}>
            <div style={{ width: '80px', height: '80px', borderRadius: '50%', background: 'linear-gradient(135deg, var(--accent-indigo), var(--accent-purple))', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '2rem', fontWeight: 700, color: 'white' }}>
              DU
            </div>
            <div>
              <button style={{ background: 'var(--bg-dark)', color: 'var(--text-primary)', border: '1px solid var(--border-strong)', padding: '0.6rem 1rem', borderRadius: 'var(--radius-sm)', cursor: 'pointer', marginRight: '1rem' }}>Upload Avatar</button>
              <button style={{ background: 'transparent', color: 'var(--accent-red)', border: 'none', cursor: 'pointer' }}>Remove</button>
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem' }}>
            <div>
              <label style={{ display: 'block', fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>Full Name</label>
              <input type="text" defaultValue="Demo User" style={{ width: '100%', padding: '0.75rem', background: 'var(--bg-dark)', border: '1px solid var(--border-strong)', borderRadius: 'var(--radius-sm)', color: 'var(--text-primary)', boxSizing: 'border-box' }} />
            </div>
            <div>
              <label style={{ display: 'block', fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>Email Address</label>
              <input type="email" defaultValue="demo@algomentor.ai" style={{ width: '100%', padding: '0.75rem', background: 'var(--bg-dark)', border: '1px solid var(--border-strong)', borderRadius: 'var(--radius-sm)', color: 'var(--text-primary)', boxSizing: 'border-box' }} />
            </div>
          </div>
        </section>

        {/* ── Learning Goals ── */}
        <section style={{ background: 'var(--bg-card)', border: '1px solid var(--border-light)', borderRadius: 'var(--radius-lg)', padding: '2rem' }}>
          <h3 style={{ fontSize: '1.1rem', margin: '0 0 1.5rem 0', color: 'var(--text-primary)', borderBottom: '1px solid var(--border-light)', paddingBottom: '0.75rem' }}>Learning Goals</h3>
          
          <div>
            <label style={{ display: 'block', fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>Primary Goal</label>
            <select style={{ width: '100%', padding: '0.75rem', background: 'var(--bg-dark)', border: '1px solid var(--border-strong)', borderRadius: 'var(--radius-sm)', color: 'var(--text-primary)', boxSizing: 'border-box', marginBottom: '1.5rem' }}>
              <option>Placement Preparation</option>
              <option>Internship Preparation</option>
              <option>College Exams</option>
              <option>Competitive Programming</option>
            </select>
          </div>

          <div>
            <label style={{ display: 'block', fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>Difficulty Calibration</label>
            <div style={{ display: 'flex', gap: '1rem' }}>
              {['Easy', 'Medium', 'Hard'].map((diff, i) => (
                <button key={i} style={{ flex: 1, padding: '0.75rem', background: diff === 'Medium' ? 'rgba(99, 102, 241, 0.1)' : 'var(--bg-dark)', border: `1px solid ${diff === 'Medium' ? 'var(--accent-indigo)' : 'var(--border-strong)'}`, borderRadius: 'var(--radius-sm)', color: diff === 'Medium' ? 'var(--accent-indigo)' : 'var(--text-secondary)', fontWeight: 600, cursor: 'pointer' }}>
                  {diff}
                </button>
              ))}
            </div>
          </div>
        </section>

        {/* ── Notifications ── */}
        <section style={{ background: 'var(--bg-card)', border: '1px solid var(--border-light)', borderRadius: 'var(--radius-lg)', padding: '2rem' }}>
          <h3 style={{ fontSize: '1.1rem', margin: '0 0 1.5rem 0', color: 'var(--text-primary)', borderBottom: '1px solid var(--border-light)', paddingBottom: '0.75rem' }}>Notification Preferences</h3>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <div style={{ fontWeight: 500, color: 'var(--text-primary)', marginBottom: '0.2rem' }}>Daily Plan Reminders</div>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Get notified when your new daily plan is generated.</div>
              </div>
              <div style={{ width: '44px', height: '24px', background: 'var(--accent-indigo)', borderRadius: '12px', position: 'relative', cursor: 'pointer' }}>
                <div style={{ width: '20px', height: '20px', background: 'white', borderRadius: '50%', position: 'absolute', top: '2px', right: '2px' }} />
              </div>
            </div>
            
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <div style={{ fontWeight: 500, color: 'var(--text-primary)', marginBottom: '0.2rem' }}>Revision Overdue Alerts</div>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Immediate alerts when a concept memory decays past threshold.</div>
              </div>
              <div style={{ width: '44px', height: '24px', background: 'var(--accent-indigo)', borderRadius: '12px', position: 'relative', cursor: 'pointer' }}>
                <div style={{ width: '20px', height: '20px', background: 'white', borderRadius: '50%', position: 'absolute', top: '2px', right: '2px' }} />
              </div>
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <div style={{ fontWeight: 500, color: 'var(--text-primary)', marginBottom: '0.2rem' }}>Weekly Progress Report</div>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Receive a summary of your performance via email.</div>
              </div>
              <div style={{ width: '44px', height: '24px', background: 'var(--border-strong)', borderRadius: '12px', position: 'relative', cursor: 'pointer' }}>
                <div style={{ width: '20px', height: '20px', background: 'var(--text-muted)', borderRadius: '50%', position: 'absolute', top: '2px', left: '2px' }} />
              </div>
            </div>
          </div>
        </section>

      </div>
    </div>
  );
}
