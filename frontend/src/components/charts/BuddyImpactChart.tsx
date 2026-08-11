"use client";

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from "recharts";

interface BuddyImpactChartProps {
  data: { buddy_assigned: boolean; training_completion_percent: number }[];
}

export default function BuddyImpactChart({ data }: BuddyImpactChartProps) {
  if (!data || data.length === 0) return null;

  // Format data for display
  const formattedData = data.map(d => ({
    name: d.buddy_assigned ? 'With Buddy' : 'No Buddy',
    percent: Math.round(d.training_completion_percent)
  }));

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={formattedData} margin={{ top: 20, right: 20, left: -20, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#475569" strokeOpacity={0.3} />
        <XAxis dataKey="name" tickLine={false} axisLine={false} tick={{fill: '#94a3b8'}} />
        <YAxis type="number" tickLine={false} axisLine={false} unit="%" domain={[0, 100]} tick={{fill: '#94a3b8'}} />
        <Tooltip cursor={{ fill: 'rgba(255,255,255,0.05)' }} contentStyle={{ borderRadius: '12px', backgroundColor: 'rgba(15, 23, 42, 0.8)', backdropFilter: 'blur(10px)', border: '1px solid rgba(255,255,255,0.1)', color: '#f8fafc' }} />
        <Bar dataKey="percent" radius={[6, 6, 0, 0]} maxBarSize={60}>
          {formattedData.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={entry.name === 'With Buddy' ? '#10b981' : '#f43f5e'} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
