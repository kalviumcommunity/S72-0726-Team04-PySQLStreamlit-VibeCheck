"use client";

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from "recharts";

interface BlockersBarChartProps {
  data: { issue_type: string; count: number }[];
}

export default function BlockersBarChart({ data }: BlockersBarChartProps) {
  if (!data || data.length === 0) return null;

  const colors = ['#f59e0b', '#3b82f6', '#10b981', '#8b5cf6', '#ef4444'];

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={data} layout="vertical" margin={{ top: 20, right: 30, left: 40, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#e2e8f0" />
        <XAxis type="number" tickLine={false} axisLine={false} tick={{fill: '#64748b'}} />
        <YAxis dataKey="issue_type" type="category" tickLine={false} axisLine={false} tick={{fill: '#64748b'}} />
        <Tooltip cursor={{ fill: '#f1f5f9' }} contentStyle={{ borderRadius: '8px', border: '1px solid #e2e8f0', color: '#0f172a' }} />
        <Bar dataKey="count" radius={[0, 4, 4, 0]}>
          {data.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
