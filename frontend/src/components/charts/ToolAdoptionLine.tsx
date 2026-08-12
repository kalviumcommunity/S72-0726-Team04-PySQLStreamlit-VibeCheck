"use client";

import { useState } from "react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from "recharts";

interface ToolAdoptionLineProps {
  data: Record<string, any>[];
}

export default function ToolAdoptionLine({ data }: ToolAdoptionLineProps) {
  const [activeLine, setActiveLine] = useState<string | null>(null);

  if (!data || data.length === 0) return null;
  const toolKeys = Object.keys(data[0]).filter(k => k !== 'date');
  const colors = ['#0f172a', '#3b82f6', '#10b981', '#f59e0b', '#8b5cf6', '#ef4444', '#06b6d4', '#ec4899'];

  const handleLegendClick = (e: any) => {
    if (activeLine === e.dataKey) {
      setActiveLine(null);
    } else {
      setActiveLine(e.dataKey);
    }
  };

  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
        <XAxis dataKey="date" tickLine={false} axisLine={false} tick={{fill: '#64748b'}} />
        <YAxis tickLine={false} axisLine={false} tick={{fill: '#64748b'}} />
        <Tooltip contentStyle={{ borderRadius: '8px', border: '1px solid #e2e8f0', color: '#0f172a' }} />
        <Legend 
          onClick={handleLegendClick}
          wrapperStyle={{ paddingTop: '20px' }} 
          cursor="pointer"
        />
        {toolKeys.map((key, index) => (
          <Line 
            key={key} 
            type="monotone" 
            dataKey={key} 
            stroke={colors[index % colors.length]} 
            strokeWidth={activeLine === null || activeLine === key ? 3 : 1}
            opacity={activeLine === null || activeLine === key ? 1 : 0.15}
            dot={false}
          />
        ))}
      </LineChart>
    </ResponsiveContainer>
  );
}
