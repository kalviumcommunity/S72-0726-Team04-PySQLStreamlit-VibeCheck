"use client";

import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

interface FrictionScatterProps {
  data: { employee_id: number; training_completion_percent: number; ticket_count: number }[];
}

export default function FrictionScatter({ data }: FrictionScatterProps) {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: -20 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
        <XAxis dataKey="training_completion_percent" type="number" name="Training %" unit="%" tickLine={false} axisLine={false} />
        <YAxis dataKey="ticket_count" type="number" name="Tickets" tickLine={false} axisLine={false} />
        <Tooltip cursor={{ strokeDasharray: '3 3' }} contentStyle={{ borderRadius: '8px' }} />
        <Scatter name="Employees" data={data} fill="#ef4444" opacity={0.6} />
      </ScatterChart>
    </ResponsiveContainer>
  );
}
