import re

with open("frontend/src/App.jsx", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Extract the blocks from the current App.jsx
# We will use regex to find the start and end of each section

def extract_section(content, start_marker, end_marker):
    start_idx = content.find(start_marker)
    if start_idx == -1: return ""
    end_idx = content.find(end_marker, start_idx)
    if end_idx == -1: return ""
    return content[start_idx:end_idx]

hero_panel = extract_section(content, '{/* ── Hero Panel ── */}', '{/* ── Smart Schedule Setup ── */}')
if not hero_panel:
    hero_panel = extract_section(content, '{/* ── Hero Panel ── */}', '</div>\n      )}\n\n      {activeView === \'schedule\'')

schedule_panel = extract_section(content, '{/* ── Smart Schedule Setup ── */}', '{/* ── Daily Override ── */}')
daily_override = extract_section(content, '{/* ── Daily Override ── */}', '</div>\n      )}\n\n      {activeView === \'dashboard\'')

smart_daily_plan = extract_section(content, '{/* ── Smart Daily Plan ── */}', '{/* ── Stats Grid ── */}')
stats_grid = extract_section(content, '{/* ── Stats Grid ── */}', '{/* ── Memory Map + Mentor ── */}')
memory_map = extract_section(content, '{/* ── Memory Map + Mentor ── */}', '{/* ── Plan + Queue ── */}')
plan_queue = extract_section(content, '{/* ── Plan + Queue ── */}', '{/* ── Revision Reminder System ── */}')
reminder_system = extract_section(content, '{/* ── Revision Reminder System ── */}', '{/* ── Recommended Problem Bank ── */}')
recommend_panel = extract_section(content, '{/* ── Recommended Problem Bank ── */}', '{/* ── Practice Workspace ── */}')
workspace_panel = extract_section(content, '{/* ── Practice Workspace ── */}', '</div>\n      )}\n\n      {activeView === \'revision\'')

# 2. Build the new views

dashboard_view = f"""
      {{activeView === 'dashboard' && (
        <div className="layout-view view-dashboard">
{hero_panel}
{stats_grid}
          <div className="dashboard-row" style={{{{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem', marginTop: '2rem' }}}}>
            {plan_queue.replace('bottom-grid', 'bottom-grid-dashboard')}
            {reminder_system}
          </div>
        </div>
      )}}
"""

schedule_view = f"""
      {{activeView === 'schedule' && (
        <div className="layout-view view-schedule" style={{{{ maxWidth: '1000px', margin: '0 auto', width: '100%' }}}}>
{schedule_panel}
{daily_override}
        </div>
      )}}
"""

revision_view = f"""
      {{activeView === 'revision' && (
        <div className="layout-view view-revision">
{smart_daily_plan}
{memory_map}
{recommend_panel}
{workspace_panel}
        </div>
      )}}
"""

analytics_view = """
      {activeView === 'analytics' && (
        <div className="layout-view view-analytics">
          <div className="section-head">
            <div>
              <p className="eyebrow">Performance Metrics</p>
              <h2>Analytics & Progress</h2>
            </div>
          </div>
          <div className="analytics-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1.5rem', marginTop: '2rem' }}>
            <div className="stat-card">
              <span className="stat-label">Total Study Time</span>
              <strong>142 hrs</strong>
              <p>+12 hrs this week</p>
            </div>
            <div className="stat-card">
              <span className="stat-label">Revision Accuracy</span>
              <strong>89%</strong>
              <p>Based on SM-2 recall scores</p>
            </div>
            <div className="stat-card success">
              <span className="stat-label">Current Streak</span>
              <strong>14 Days</strong>
              <p>Keep it up!</p>
            </div>
            <div className="stat-card danger">
              <span className="stat-label">Needs Attention</span>
              <strong>Dynamic Programming</strong>
              <p>4 problems overdue</p>
            </div>
          </div>
        </div>
      )}
"""

settings_view = """
      {activeView === 'settings' && (
        <div className="layout-view view-settings" style={{ maxWidth: '800px', margin: '0 auto', width: '100%' }}>
          <div className="section-head">
            <div>
              <p className="eyebrow">Account Preferences</p>
              <h2>Settings</h2>
            </div>
          </div>
          <div className="settings-card" style={{ background: '#1e293b', padding: '2rem', borderRadius: '12px', border: '1px solid rgba(148, 163, 184, 0.1)', marginTop: '2rem' }}>
            <h3 style={{ marginBottom: '1.5rem', color: '#f8fafc' }}>Profile Information</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', color: '#94a3b8', marginBottom: '0.5rem' }}>Display Name</label>
                <input type="text" value="Demo User" disabled style={{ width: '100%', padding: '0.75rem', background: '#0f172a', border: '1px solid rgba(148, 163, 184, 0.2)', borderRadius: '6px', color: '#f8fafc' }} />
              </div>
              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', color: '#94a3b8', marginBottom: '0.5rem' }}>Email Address</label>
                <input type="email" value="demo@algomentor.ai" disabled style={{ width: '100%', padding: '0.75rem', background: '#0f172a', border: '1px solid rgba(148, 163, 184, 0.2)', borderRadius: '6px', color: '#f8fafc' }} />
              </div>
              <button className="primary-btn" style={{ alignSelf: 'flex-start', marginTop: '1rem' }}>Save Changes</button>
            </div>
          </div>
        </div>
      )}
"""

# 3. Replace everything inside <AppShell> with the new views
start_idx = content.find("<AppShell activeView={activeView} setActiveView={setActiveView}>")
end_idx = content.find("</AppShell>")

if start_idx != -1 and end_idx != -1:
    new_content = content[:start_idx + len("<AppShell activeView={activeView} setActiveView={setActiveView}>")]
    new_content += dashboard_view + schedule_view + revision_view + analytics_view + settings_view
    new_content += "\n    " + content[end_idx:]
    
    with open("frontend/src/App.jsx", "w", encoding="utf-8") as f:
        f.write(new_content)
    print("App.jsx rewritten successfully.")
else:
    print("Could not find AppShell markers.")

