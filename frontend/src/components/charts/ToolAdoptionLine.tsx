"use client";

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from "recharts";

interface ToolAdoptionLineProps {
  data: Record<string, unknown>[];
}

export default function ToolAdoptionLine({ data }: ToolAdoptionLineProps) {
  if (!data || data.length === 0) return null;
  const toolKeys = Object.keys(data[0]).filter(k => k !== 'date');
  const colors = ['#d946ef', '#3b82f6', '#10b981', '#f97316', '#fb7185'];

  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
        <XAxis dataKey="date" tickLine={false} axisLine={false} dy={10} />
        <YAxis tickLine={false} axisLine={false} />
        <Tooltip contentStyle={{ borderRadius: '8px' }} />
        <Legend iconType="circle" />
        {toolKeys.map((key, idx) => (
          <Line key={key} type="monotone" dataKey={key} stroke={colors[idx % colors.length]} strokeWidth={3} dot={false} />
        ))}
      </LineChart>
    </ResponsiveContainer>
  );
}
