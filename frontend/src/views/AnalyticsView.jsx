import React from 'react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer,
  LineChart, Line, AreaChart, Area
} from 'recharts';

const weeklyData = [
  { name: 'Mon', hours: 2.5 },
  { name: 'Tue', hours: 3.8 },
  { name: 'Wed', hours: 1.5 },
  { name: 'Thu', hours: 4.2 },
  { name: 'Fri', hours: 2.0 },
  { name: 'Sat', hours: 5.5 },
  { name: 'Sun', hours: 4.8 },
];

const progressData = [
  { day: 'Day 1', score: 40 },
  { day: 'Day 5', score: 45 },
  { day: 'Day 10', score: 55 },
  { day: 'Day 15', score: 65 },
  { day: 'Day 20', score: 75 },
  { day: 'Day 25', score: 85 },
  { day: 'Day 30', score: 89 },
];

const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div style={{ background: 'rgba(15, 23, 42, 0.9)', border: '1px solid rgba(148, 163, 184, 0.2)', padding: '10px', borderRadius: '8px', boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.5)' }}>
        <p style={{ margin: 0, color: 'var(--text-primary)', fontWeight: 600 }}>{label}</p>
        <p style={{ margin: 0, color: payload[0].color, fontSize: '0.9rem' }}>
          {payload[0].name}: {payload[0].value}
        </p>
      </div>
    );
  }
  return null;
};

export default function AnalyticsView() {
  return (
    <div className="layout-view layout-view-padded">
      <div className="section-head" style={{ marginBottom: '2rem' }}>
        <div>
          <p className="eyebrow" style={{ color: 'var(--accent-blue)', fontSize: '0.85rem', fontWeight: 600, textTransform: 'uppercase', marginBottom: '0.5rem' }}>Performance Metrics</p>
          <h2 style={{ fontSize: '1.75rem', margin: '0 0 0.5rem 0', color: 'var(--text-primary)' }}>Analytics Dashboard</h2>
          <p style={{ color: 'var(--text-secondary)' }}>Track your spaced repetition efficiency and problem solving trends.</p>
        </div>
      </div>

      {/* ── Top KPIs ── */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1.5rem', marginBottom: '2rem' }}>
        {[
          { label: 'Total Study Time', val: '142h', desc: '+12h this month', color: 'var(--accent-indigo)' },
          { label: 'Avg Accuracy', val: '89%', desc: 'SM-2 Recall Score', color: 'var(--accent-green)' },
          { label: 'Longest Streak', val: '28 Days', desc: 'Personal Best', color: 'var(--accent-purple)' },
          { label: 'Topics Mastered', val: '14/32', desc: '43% Completion', color: 'var(--accent-blue)' }
        ].map((kpi, i) => (
          <div key={i} style={{ background: 'var(--bg-card)', border: '1px solid var(--border-light)', borderRadius: 'var(--radius-md)', padding: '1.25rem', transition: 'transform 0.2s', cursor: 'pointer' }}
               onMouseOver={(e) => e.currentTarget.style.transform = 'translateY(-2px)'}
               onMouseOut={(e) => e.currentTarget.style.transform = 'none'}>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>{kpi.label}</div>
            <div style={{ fontSize: '1.75rem', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '0.25rem' }}>{kpi.val}</div>
            <div style={{ fontSize: '0.75rem', color: kpi.color }}>{kpi.desc}</div>
          </div>
        ))}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '1.5rem', marginBottom: '2rem' }}>
        {/* ── Study Time Bar Chart ── */}
        <div style={{ background: 'var(--bg-card)', border: '1px solid var(--border-light)', borderRadius: 'var(--radius-lg)', padding: '1.5rem' }}>
          <h3 style={{ fontSize: '1.1rem', margin: '0 0 1.5rem 0', color: 'var(--text-primary)' }}>Weekly Study Hours</h3>
          <div style={{ height: 250 }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={weeklyData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(148, 163, 184, 0.1)" vertical={false} />
                <XAxis dataKey="name" stroke="var(--text-muted)" fontSize={12} tickLine={false} axisLine={false} />
                <YAxis stroke="var(--text-muted)" fontSize={12} tickLine={false} axisLine={false} />
                <RechartsTooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(255,255,255,0.05)' }} />
                <Bar dataKey="hours" name="Hours" fill="var(--accent-indigo)" radius={[4, 4, 0, 0]} barSize={30} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* ── Problem Solving Trends Area Chart ── */}
        <div style={{ background: 'var(--bg-card)', border: '1px solid var(--border-light)', borderRadius: 'var(--radius-lg)', padding: '1.5rem' }}>
          <h3 style={{ fontSize: '1.1rem', margin: '0 0 1.5rem 0', color: 'var(--text-primary)' }}>Accuracy Trend (30 Days)</h3>
          <div style={{ height: 250 }}>
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={progressData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorScore" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="var(--accent-green)" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="var(--accent-green)" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(148, 163, 184, 0.1)" vertical={false} />
                <XAxis dataKey="day" stroke="var(--text-muted)" fontSize={12} tickLine={false} axisLine={false} />
                <YAxis stroke="var(--text-muted)" fontSize={12} tickLine={false} axisLine={false} domain={[0, 100]} />
                <RechartsTooltip content={<CustomTooltip />} />
                <Area type="monotone" dataKey="score" name="Accuracy %" stroke="var(--accent-green)" fillOpacity={1} fill="url(#colorScore)" strokeWidth={2} />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* ── Topic Mastery ── */}
      <div style={{ background: 'var(--bg-card)', border: '1px solid var(--border-light)', borderRadius: 'var(--radius-lg)', padding: '1.5rem', marginBottom: '2rem' }}>
        <h3 style={{ fontSize: '1.1rem', margin: '0 0 1.5rem 0', color: 'var(--text-primary)' }}>Topic Mastery</h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.5rem' }}>
          {[
            { topic: 'Arrays', pct: 95 },
            { topic: 'Two Pointers', pct: 82 },
            { topic: 'Sliding Window', pct: 60 },
            { topic: 'Binary Search', pct: 45 },
            { topic: 'Dynamic Programming', pct: 30 },
            { topic: 'Graphs', pct: 15 },
          ].map((t, i) => (
            <div key={i}>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', marginBottom: '0.4rem' }}>
                <span style={{ color: 'var(--text-secondary)' }}>{t.topic}</span>
                <span style={{ color: 'var(--text-primary)', fontWeight: 600 }}>{t.pct}%</span>
              </div>
              <div style={{ width: '100%', background: 'var(--bg-dark)', height: '8px', borderRadius: '4px', overflow: 'hidden' }}>
                <div style={{ width: `${t.pct}%`, background: t.pct > 80 ? 'var(--accent-green)' : t.pct > 50 ? 'var(--accent-blue)' : 'var(--accent-purple)', height: '100%', borderRadius: '4px' }} />
              </div>
            </div>
          ))}
        </div>
      </div>

    </div>
  );
}
