"use client";

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from "recharts";

interface BlockersBarChartProps {
  data: { issue_type: string; count: number }[];
}

export default function BlockersBarChart({ data }: BlockersBarChartProps) {
  if (!data || data.length === 0) return null;

  const colors = ['#d946ef', '#3b82f6', '#10b981', '#f97316', '#fb7185'];

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={data} layout="vertical" margin={{ top: 20, right: 30, left: 40, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#475569" strokeOpacity={0.3} />
        <XAxis type="number" tickLine={false} axisLine={false} tick={{fill: '#94a3b8'}} />
        <YAxis dataKey="issue_type" type="category" tickLine={false} axisLine={false} tick={{fill: '#94a3b8'}} />
        <Tooltip cursor={{ fill: 'rgba(255,255,255,0.05)' }} contentStyle={{ borderRadius: '12px', backgroundColor: 'rgba(15, 23, 42, 0.8)', backdropFilter: 'blur(10px)', border: '1px solid rgba(255,255,255,0.1)', color: '#f8fafc' }} />
        <Bar dataKey="count" radius={[0, 6, 6, 0]}>
          {data.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
