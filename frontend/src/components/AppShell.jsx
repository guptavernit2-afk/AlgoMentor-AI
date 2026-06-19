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
    { id: 'schedule', label: 'Schedule', icon: '📅' },
    { id: 'revision', label: 'Revision', icon: '🧠' },
    { id: 'analytics', label: 'Analytics', icon: '📊' },
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

        <div className="sidebar-bottom-widgets">
          <div className="sidebar-protip">
            <div className="protip-label">
              <span>💡</span> PRO TIP
            </div>
            <div className="protip-text">
              Consistency is the ultimate algorithm.<br/>
              <span style={{ color: 'var(--accent-indigo)', fontWeight: 600 }}>Keep showing up!</span>
            </div>
          </div>

          <div className="sidebar-streak-card">
            <div className="streak-header">
              <span className="streak-title">Study Streak</span>
            </div>
            <div className="streak-value">7 <span style={{ fontSize: '0.9rem', color: 'var(--text-secondary)' }}>days</span></div>
            <div style={{ display: 'flex', gap: '4px', marginTop: '0.75rem', height: '20px', alignItems: 'flex-end' }}>
              {[30, 50, 40, 70, 60, 90, 80].map((h, i) => (
                <div key={i} style={{ flex: 1, background: 'var(--accent-green)', height: `${h}%`, borderRadius: '2px' }} />
              ))}
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.65rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
              <span>M</span><span>T</span><span>W</span><span>T</span><span>F</span><span>S</span><span>S</span>
            </div>
          </div>
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

            <button className="user-profile-btn">
              <div className="app-avatar">DU</div>
              <span className="user-name">Demo User</span>
              <span className="user-dropdown-icon">▼</span>
            </button>
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
