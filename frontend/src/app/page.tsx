"use client";

import { useEffect, useState } from "react";
import { fetchKPIs, fetchCharts, fetchEmployees, KPIPayload, ChartsPayload, EmployeeFriction } from "@/lib/api";
import AnimatedCard from "@/components/AnimatedCard";
import FrictionScatter from "@/components/charts/FrictionScatter";
import ToolAdoptionLine from "@/components/charts/ToolAdoptionLine";
import EmployeeTable from "@/components/EmployeeTable";
import EmployeeDrawer from "@/components/EmployeeDrawer";
import { CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { AlertCircle } from "lucide-react";

export default function Dashboard() {
  const [kpis, setKpis] = useState<KPIPayload | null>(null);
  const [charts, setCharts] = useState<ChartsPayload | null>(null);
  const [employees, setEmployees] = useState<EmployeeFriction[]>([]);
  const [selectedEmployee, setSelectedEmployee] = useState<number | null>(null);

  useEffect(() => {
    Promise.all([fetchKPIs(), fetchCharts(), fetchEmployees()]).then(([k, c, e]) => {
      setKpis(k);
      setCharts(c);
      setEmployees(e);
    });
  }, []);

  const highRiskCount = employees.filter(e => e.friction_score > 70).length;

  if (!kpis || !charts) return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center">
      <div className="animate-pulse flex flex-col items-center">
        <div className="w-12 h-12 border-4 border-slate-300 border-t-slate-900 rounded-full animate-spin"></div>
        <p className="mt-4 text-slate-500 font-medium">Loading insights...</p>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-slate-50 p-8 text-slate-900 font-sans space-y-6">
      
      {/* Top Filter Bar (Mocked UI) */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Onboarding Operations</h1>
          <p className="text-slate-500">Real-time friction and productivity analytics</p>
        </div>
        <div className="flex gap-2">
          <select className="border rounded-md px-3 py-1.5 text-sm bg-white"><option>All Departments</option></select>
          <select className="border rounded-md px-3 py-1.5 text-sm bg-white"><option>Last 30 Days</option></select>
        </div>
      </div>

      {/* Dynamic Alert Banner */}
      {highRiskCount > 0 && (
        <div className="bg-red-50 text-red-800 border border-red-200 p-4 rounded-md flex items-center gap-3">
          <AlertCircle className="w-5 h-5 text-red-600" />
          <span className="font-medium">Action Required: {highRiskCount} new hires have a friction score over 70.</span>
        </div>
      )}

      {/* KPIs */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <AnimatedCard delay={0.1}>
          <CardHeader className="pb-2"><CardTitle className="text-sm text-slate-500">Avg Onboarding Days</CardTitle></CardHeader>
          <CardContent><div className="text-3xl font-bold">{kpis.avg_onboarding_days}</div></CardContent>
        </AnimatedCard>
        <AnimatedCard delay={0.2}>
          <CardHeader className="pb-2"><CardTitle className="text-sm text-slate-500">Time-to-Value (Days)</CardTitle></CardHeader>
          <CardContent><div className="text-3xl font-bold">{kpis.time_to_value}</div></CardContent>
        </AnimatedCard>
        <AnimatedCard delay={0.3}>
          <CardHeader className="pb-2"><CardTitle className="text-sm text-slate-500">Avg Tickets per Hire</CardTitle></CardHeader>
          <CardContent><div className="text-3xl font-bold">{kpis.avg_tickets}</div></CardContent>
        </AnimatedCard>
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <AnimatedCard delay={0.4}>
          <CardHeader><CardTitle>Friction Correlation</CardTitle></CardHeader>
          <CardContent><FrictionScatter data={charts.scatter} /></CardContent>
        </AnimatedCard>
        
        <AnimatedCard delay={0.5}>
          <CardHeader><CardTitle>Tool Adoption Over Time</CardTitle></CardHeader>
          <CardContent><ToolAdoptionLine data={charts.tool_adoption} /></CardContent>
        </AnimatedCard>
      </div>

      {/* Employee Table */}
      <AnimatedCard delay={0.6}>
        <CardHeader><CardTitle>High-Friction Employees</CardTitle></CardHeader>
        <CardContent>
          <EmployeeTable employees={employees} onRowClick={setSelectedEmployee} />
        </CardContent>
      </AnimatedCard>

      <EmployeeDrawer 
        employeeId={selectedEmployee} 
        isOpen={selectedEmployee !== null} 
        onClose={() => setSelectedEmployee(null)} 
      />
    </div>
  );
}
