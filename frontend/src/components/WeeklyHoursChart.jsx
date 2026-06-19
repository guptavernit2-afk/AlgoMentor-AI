import React from 'react';
import { BarChart, Bar, XAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';

export default function WeeklyHoursChart({ data }) {
  if (!data || data.length === 0) return null;

  return (
    <div className="weekly-hours-chart-container" style={{ width: '100%', height: '150px', marginTop: '1rem' }}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={data} margin={{ top: 0, right: 0, left: 0, bottom: 0 }}>
          <XAxis 
            dataKey="day" 
            tick={{ fontSize: 10, fill: 'var(--text-muted)' }} 
            tickLine={false} 
            axisLine={false}
          />
          <Tooltip 
            cursor={{ fill: 'rgba(255,255,255,0.05)' }}
            contentStyle={{ backgroundColor: '#1e293b', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px' }}
            formatter={(value) => [`${value}h`, 'Study Time']}
          />
          <Bar dataKey="hours" radius={[4, 4, 0, 0]}>
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.day === 'Sat' || entry.day === 'Sun' ? '#8b5cf6' : '#6366f1'} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
