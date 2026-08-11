"use client";

import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

interface FrictionScatterProps {
  data: { employee_id: number; training_completion_percent: number; ticket_count: number }[];
}

export default function FrictionScatter({ data }: FrictionScatterProps) {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: -20 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#475569" strokeOpacity={0.3} />
        <XAxis dataKey="training_completion_percent" type="number" name="Training %" unit="%" tickLine={false} axisLine={false} tick={{fill: '#94a3b8'}} />
        <YAxis dataKey="ticket_count" type="number" name="Tickets" tickLine={false} axisLine={false} tick={{fill: '#94a3b8'}} />
        <Tooltip cursor={{ strokeDasharray: '3 3', stroke: '#cbd5e1' }} contentStyle={{ borderRadius: '12px', backgroundColor: 'rgba(15, 23, 42, 0.8)', backdropFilter: 'blur(10px)', border: '1px solid rgba(255,255,255,0.1)', color: '#f8fafc' }} />
        <Scatter name="Employees" data={data} fill="#ef4444" opacity={0.8} />
      </ScatterChart>
    </ResponsiveContainer>
  );
}
