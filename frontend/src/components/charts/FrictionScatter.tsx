"use client";

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from "recharts";

interface FrictionCohortChartProps {
  data: { employee_id: number; training_completion_percent: number; ticket_count: number }[];
}

export default function FrictionScatter({ data }: FrictionCohortChartProps) {
  if (!data || data.length === 0) return null;

  let lowCount = 0, lowTickets = 0;
  let medCount = 0, medTickets = 0;
  let highCount = 0, highTickets = 0;

  data.forEach(d => {
    if (d.training_completion_percent < 50) {
      lowCount++;
      lowTickets += d.ticket_count;
    } else if (d.training_completion_percent <= 80) {
      medCount++;
      medTickets += d.ticket_count;
    } else {
      highCount++;
      highTickets += d.ticket_count;
    }
  });

  const cohortData = [
    { name: 'Low (<50%)', avg_tickets: lowCount ? Number((lowTickets / lowCount).toFixed(1)) : 0 },
    { name: 'Medium (50-80%)', avg_tickets: medCount ? Number((medTickets / medCount).toFixed(1)) : 0 },
    { name: 'High (>80%)', avg_tickets: highCount ? Number((highTickets / highCount).toFixed(1)) : 0 }
  ];

  const colors = ['#ef4444', '#f59e0b', '#10b981'];

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={cohortData} margin={{ top: 20, right: 20, bottom: 5, left: -20 }}>
        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
        <XAxis dataKey="name" tickLine={false} axisLine={false} tick={{fill: '#64748b'}} />
        <YAxis dataKey="avg_tickets" type="number" name="Avg Tickets" tickLine={false} axisLine={false} tick={{fill: '#64748b'}} />
        <Tooltip cursor={{ fill: '#f1f5f9' }} contentStyle={{ borderRadius: '8px', border: '1px solid #e2e8f0', color: '#0f172a' }} />
        <Bar dataKey="avg_tickets" radius={[4, 4, 0, 0]} maxBarSize={60}>
          {cohortData.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
