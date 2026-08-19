"use client";

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from "recharts";

interface BuddyImpactChartProps {
  data: { buddy_assigned: boolean; training_completion_percent: number }[];
}

export default function BuddyImpactChart({ data }: BuddyImpactChartProps) {
  if (!data || data.length === 0) return null;

  const formattedData = data.map(d => {
    const val = String(d.buddy_assigned).toLowerCase();
    const isBuddy = d.buddy_assigned === true || val === 'true' || val === 'yes' || val === 'y' || d.buddy_assigned === 1;
    return {
      name: isBuddy ? 'With Buddy' : 'Without Buddy',
      percent: Math.round(d.training_completion_percent)
    };
  });

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={formattedData} margin={{ top: 20, right: 20, left: -20, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
        <XAxis dataKey="name" tickLine={false} axisLine={false} tick={{ fill: '#64748b' }} />
        <YAxis type="number" tickLine={false} axisLine={false} unit="%" domain={[0, 100]} tick={{ fill: '#64748b' }} />
        <Tooltip cursor={{ fill: '#f1f5f9' }} contentStyle={{ borderRadius: '8px', border: '1px solid #e2e8f0', color: '#0f172a' }} />
        <Bar dataKey="percent" radius={[4, 4, 0, 0]} maxBarSize={60}>
          {formattedData.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={entry.name === 'With Buddy' ? '#10b981' : '#ef4444'} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
