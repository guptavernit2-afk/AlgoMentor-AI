import React from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export default function AccuracyChart({ data }) {
  if (!data || data.length === 0) return null;

  return (
    <div className="accuracy-chart-container" style={{ width: '100%', height: '200px' }}>
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
          <defs>
            <linearGradient id="colorAccuracy" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.8}/>
              <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0}/>
            </linearGradient>
          </defs>
          <XAxis 
            dataKey="date" 
            tick={{ fontSize: 10, fill: 'var(--text-muted)' }} 
            tickLine={false} 
            axisLine={false}
            minTickGap={20}
          />
          <YAxis 
            tick={{ fontSize: 10, fill: 'var(--text-muted)' }} 
            tickLine={false} 
            axisLine={false}
            tickFormatter={(val) => `${val}%`}
          />
          <Tooltip 
            contentStyle={{ backgroundColor: '#1e293b', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px' }}
            itemStyle={{ color: '#8b5cf6' }}
            formatter={(value) => [`${value}%`, 'Accuracy']}
          />
          <Area 
            type="monotone" 
            dataKey="accuracy" 
            stroke="#8b5cf6" 
            strokeWidth={3} 
            fillOpacity={1}
            fill="url(#colorAccuracy)"
            activeDot={{ r: 6, fill: '#fff', stroke: '#8b5cf6', strokeWidth: 3 }}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
