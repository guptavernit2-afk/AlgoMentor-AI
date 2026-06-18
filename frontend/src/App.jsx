import { useState, useEffect } from "react";
import { checkBackendHealth, getProfile, DEMO_USER_ID } from "./services/api";
import "./App.css";

import AppShell from "./components/AppShell";
import OnboardingWizard from "./components/onboarding/OnboardingWizard";
import DashboardView from "./views/DashboardView";
import ScheduleView from "./views/ScheduleView";
import RevisionView from "./views/RevisionView";
import AnalyticsView from "./views/AnalyticsView";
import SettingsView from "./views/SettingsView";
import WorkspaceView from "./views/WorkspaceView";

function App() {
  const [activeView, setActiveView] = useState("dashboard");
  const [backendStatus, setBackendStatus] = useState("PROTOTYPE · CHECKING API");
  const [onboardingStatus, setOnboardingStatus] = useState('checking');

  useEffect(() => {
    checkBackendHealth().then((isHealthy) => {
      setBackendStatus(isHealthy ? "PROTOTYPE · API CONNECTED" : "PROTOTYPE · API OFFLINE");
    });
  }, []);

  useEffect(() => {
    let cancelled = false;
    getProfile(DEMO_USER_ID)
      .then(() => {
        if (!cancelled) setOnboardingStatus('complete');
      })
      .catch((err) => {
        if (cancelled) return;
        setOnboardingStatus('required');
      });
    return () => { cancelled = true; };
  }, []);

  if (onboardingStatus === 'checking') {
    return (
      <div className="app-root">
        <nav className="top-nav" style={{ padding: '1rem', borderBottom: '1px solid rgba(255,255,255,0.1)', background: '#0f172a', color: '#f8fafc', display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <span style={{ color: '#6366f1', fontSize: '1.5rem', fontWeight: 700 }}>⬡</span>
          <span style={{ fontSize: '1.2rem', fontWeight: 600 }}>AlgoMentor AI</span>
          <span style={{ marginLeft: 'auto', background: 'rgba(255,255,255,0.1)', padding: '0.2rem 0.5rem', borderRadius: '4px', fontSize: '0.75rem' }}>LOADING</span>
        </nav>
        <main style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '60vh', background: '#090e17' }}>
          <p style={{ color: 'rgba(148, 163, 184, 0.55)' }}>Checking your profile…</p>
        </main>
      </div>
    );
  }

  if (onboardingStatus === 'required') {
    return <OnboardingWizard onComplete={() => setOnboardingStatus('complete')} />;
  }

  if (activeView === 'workspace') {
    return <WorkspaceView setActiveView={setActiveView} />;
  }

  return (
    <AppShell activeView={activeView} setActiveView={setActiveView}>
      {activeView === 'dashboard' && <DashboardView setActiveView={setActiveView} />}
      {activeView === 'schedule' && <ScheduleView />}
      {activeView === 'revision' && <RevisionView />}
      {activeView === 'analytics' && <AnalyticsView />}
      {activeView === 'settings' && <SettingsView />}
    </AppShell>
  );
}

export default App;