import { useState, useEffect } from 'react';
import './AppShell.css';
import { notificationsData } from '../data/notifications.js';

export default function AppShell({ children, activeView, setActiveView }) {
  const [showNotifications, setShowNotifications] = useState(false);
  const [notifications, setNotifications] = useState(notificationsData);

  const unreadCount = notifications.filter(n => !n.isRead).length;

  const markAllRead = () => {
    setNotifications(notifications.map(n => ({ ...n, isRead: true })));
  };

  const markRead = (id) => {
    setNotifications(notifications.map(n => n.id === id ? { ...n, isRead: true } : n));
  };

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (showNotifications && !e.target.closest('.notif-wrapper')) {
        setShowNotifications(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [showNotifications]);

  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: '🏠' },
    { id: 'revision', label: 'Study Plan', icon: '📅' },
    { id: 'problems', label: 'Problems', icon: '🧩' },
    { id: 'achievements', label: 'Achievements', icon: '🏆' },
    { id: 'settings', label: 'Settings', icon: '⚙️' },
  ];

  return (
    <div className="app-layout">
      
      {/* ── LEFT SIDEBAR ── */}
      <aside className="app-sidebar">
        <div className="app-sidebar-logo">
          <span style={{ color: 'var(--accent-indigo)', fontSize: '1.5rem' }}>⬡</span>
          AlgoMentor <span style={{ color: 'var(--accent-purple)', fontWeight: '300' }}>AI</span>
        </div>
        
        <nav className="app-nav">
          {navItems.map(item => (
            <button
              key={item.id}
              className={`app-nav-item ${activeView === item.id ? 'active' : ''}`}
              onClick={() => setActiveView(item.id)}
            >
              <span>{item.icon}</span> {item.label}
            </button>
          ))}
        </nav>
        <div className="sidebar-bottom-profile" style={{
          marginTop: 'auto',
          padding: '1rem',
          display: 'flex',
          alignItems: 'center',
          gap: '0.75rem',
          borderTop: '1px solid rgba(255,255,255,0.05)',
          cursor: 'pointer'
        }}>
          <div style={{ position: 'relative' }}>
            <img src="https://i.pravatar.cc/150?u=vernit" alt="Profile" style={{ width: '40px', height: '40px', borderRadius: '50%', border: '2px solid var(--bg-dark)' }} />
            <div style={{ position: 'absolute', bottom: 0, right: 0, background: 'var(--accent-green)', width: '10px', height: '10px', borderRadius: '50%', border: '2px solid var(--bg-card)' }}></div>
          </div>
          <div style={{ flex: 1, overflow: 'hidden' }}>
            <div style={{ fontSize: '0.9rem', fontWeight: 600, color: 'var(--text-primary)', whiteSpace: 'nowrap', textOverflow: 'ellipsis', overflow: 'hidden' }}>Vernit Gupta</div>
            <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', whiteSpace: 'nowrap', textOverflow: 'ellipsis', overflow: 'hidden' }}>Top 5% · Master Rank</div>
          </div>
          <div style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>▼</div>
        </div>
      </aside>

      {/* ── CENTER WORKSPACE ── */}
      <main className="app-center">
        
        {/* Topbar */}
        <header className="app-topbar">
          <div className="app-topbar-left">
            <button className="hamburger-btn">≡</button>
            <div className="app-topbar-title-group">
              <h1 className="app-topbar-title">
                {activeView.charAt(0).toUpperCase() + activeView.slice(1)}
              </h1>
              {activeView === 'dashboard' && (
                <span className="app-topbar-subtitle">Welcome back, Vernit! 👋</span>
              )}
            </div>
          </div>

          <div className="app-topbar-center">
            <div className="search-container">
              <span className="search-icon">🔍</span>
              <input type="text" className="search-input" placeholder="Search anything..." />
              <span className="search-shortcut">Ctrl K</span>
            </div>
          </div>

          <div className="app-topbar-actions">
            
            <div className="notif-wrapper">
              <button className="notif-bell" onClick={() => setShowNotifications(!showNotifications)}>
                🔔
                {unreadCount > 0 && <span className="notif-badge">{unreadCount}</span>}
              </button>

              {/* Floating Notifications Dropdown */}
              {showNotifications && (
                <div className="notif-dropdown">
                  <div className="notif-dropdown-header">
                    <span className="notif-dropdown-title">Notifications</span>
                    <button className="notif-mark-read" onClick={markAllRead}>Mark all as read</button>
                  </div>
                  <div className="notif-list">
                    {notifications.map(notif => (
                      <div key={notif.id} className={`notif-card ${!notif.isRead ? 'unread' : ''}`} onClick={() => markRead(notif.id)}>
                        <div className="notif-icon">{notif.icon}</div>
                        <div className="notif-content">
                          <div className="notif-title" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            {notif.title}
                            <span className="notif-time">{notif.timeAgo} {!notif.isRead && <span className="notif-unread-dot" />}</span>
                          </div>
                          <div className="notif-desc">{notif.description}</div>
                        </div>
                      </div>
                    ))}
                  </div>
                  <div className="notif-dropdown-footer">
                    <a className="notif-view-all">View all notifications &gt;</a>
                  </div>
                </div>
              )}
            </div>

          </div>
        </header>

        {/* Scrollable Content */}
        <div className="app-content">
          {children}
        </div>
      </main>

    </div>
  );
}
