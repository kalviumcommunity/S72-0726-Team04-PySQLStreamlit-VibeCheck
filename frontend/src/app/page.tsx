"use client";

import { useEffect, useState } from "react";
import { fetchKPIs, fetchCharts, fetchEmployees, KPIPayload, ChartsPayload, EmployeeFriction } from "@/lib/api";
import AnimatedCard from "@/components/AnimatedCard";
import FrictionScatter from "@/components/charts/FrictionScatter";
import ToolAdoptionLine from "@/components/charts/ToolAdoptionLine";
import BlockersBarChart from "@/components/charts/BlockersBarChart";
import BuddyImpactChart from "@/components/charts/BuddyImpactChart";
import EmployeeCardGrid from "@/components/EmployeeCardGrid";
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
  // Get top 6 high friction employees to display in the grid
  const topHighRiskEmployees = employees.slice(0, 6);

  if (!kpis || !charts) return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center">
      <div className="animate-pulse flex flex-col items-center">
        <div className="w-12 h-12 border-4 border-slate-300 border-t-slate-900 rounded-full animate-spin"></div>
        <p className="mt-4 text-slate-500 font-medium">Loading insights...</p>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-slate-50 relative overflow-hidden p-8 text-slate-900 font-sans space-y-6 z-0">
      
      {/* Top Filter Bar */}
      <div className="flex items-center justify-between bg-white backdrop-blur-md border border-slate-200 p-5 rounded-2xl shadow-sm mb-8 transition-all hover:shadow-md">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-slate-900">Onboarding Operations</h1>
          <p className="text-slate-500 mt-1">Real-time friction and productivity analytics</p>
        </div>
        <div className="flex gap-3">
          <select className="bg-background/60 backdrop-blur-md border border-border rounded-xl px-4 py-2.5 text-sm focus:ring-2 focus:ring-primary outline-none transition-all hover:border-primary/50 cursor-pointer"><option>All Departments</option></select>
          <select className="bg-background/60 backdrop-blur-md border border-border rounded-xl px-4 py-2.5 text-sm focus:ring-2 focus:ring-primary outline-none transition-all hover:border-primary/50 cursor-pointer"><option>Last 30 Days</option></select>
        </div>
      </div>

      {/* Dynamic Alert Banner */}
      {highRiskCount > 0 && (
        <div className="bg-red-50 border border-red-200 p-4 rounded-xl flex items-center gap-3 shadow-sm mb-6 backdrop-blur-sm animate-in fade-in slide-in-from-top-4 duration-500">
          <AlertCircle className="w-5 h-5 text-red-600 animate-pulse" />
          <span className="font-medium text-red-900">Action Required: <span className="font-bold">{highRiskCount} new hires</span> have a friction score over 70.</span>
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
          <AnimatedCard delay={0.1}>
            <CardHeader className="pb-2 border-b border-slate-100">
              <CardTitle className="text-base font-semibold text-slate-800">Tickets by Training Cohort</CardTitle>
            </CardHeader>
            <CardContent className="pt-4">
              <FrictionScatter data={charts?.scatter || []} />
            </CardContent>
          </AnimatedCard>
        
        <AnimatedCard delay={0.5}>
          <CardHeader><CardTitle>Tool Adoption Over Time</CardTitle></CardHeader>
          <CardContent><ToolAdoptionLine data={charts.tool_adoption} /></CardContent>
        </AnimatedCard>
        
        <AnimatedCard delay={0.6}>
          <CardHeader><CardTitle>Top IT Bottlenecks</CardTitle></CardHeader>
          <CardContent><BlockersBarChart data={charts.blockers} /></CardContent>
        </AnimatedCard>

        <AnimatedCard delay={0.7}>
          <CardHeader><CardTitle>Buddy Impact on Training %</CardTitle></CardHeader>
          <CardContent><BuddyImpactChart data={charts.buddy_impact} /></CardContent>
        </AnimatedCard>
      </div>

      {/* High Friction Employee Cards */}
      <AnimatedCard delay={0.8}>
        <CardHeader>
          <CardTitle>High-Friction Employees</CardTitle>
          <p className="text-sm text-slate-500">Top 6 employees requiring immediate intervention</p>
        </CardHeader>
        <CardContent>
          <EmployeeCardGrid employees={topHighRiskEmployees} onRowClick={setSelectedEmployee} />
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
