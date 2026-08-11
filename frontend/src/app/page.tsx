"use client";

import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import {
  fetchKPIs,
  fetchFrictionCorrelation,
  fetchBlockers,
  fetchToolAdoption,
  fetchHighFrictionEmployees
} from '@/lib/api';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import {
  ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  BarChart, Bar,
  LineChart, Line, Legend
} from 'recharts';
import { Activity, Clock, Ticket, Users } from 'lucide-react';

export default function Dashboard() {
  const [kpis, setKpis] = useState<any>(null);
  const [frictionData, setFrictionData] = useState<any[]>([]);
  const [blockers, setBlockers] = useState<any[]>([]);
  const [toolData, setToolData] = useState<any[]>([]);
  const [employees, setEmployees] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const [k, f, b, t, e] = await Promise.all([
          fetchKPIs(),
          fetchFrictionCorrelation(),
          fetchBlockers(),
          fetchToolAdoption(),
          fetchHighFrictionEmployees()
        ]);
        setKpis(k);
        setFrictionData(f);
        setBlockers(b);
        setToolData(t);
        setEmployees(e);
      } catch (error) {
        console.error("Error loading dashboard data:", error);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const containerVariants = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: { staggerChildren: 0.1 }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    show: { opacity: 1, y: 0, transition: { type: "spring", stiffness: 300, damping: 24 } }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <div className="animate-pulse flex flex-col items-center">
          <div className="w-12 h-12 border-4 border-slate-300 border-t-slate-900 rounded-full animate-spin"></div>
          <p className="mt-4 text-slate-500 font-medium">Loading insights...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 p-8 font-sans">
      <motion.div
        className="max-w-7xl mx-auto space-y-8"
        variants={containerVariants}
        initial="hidden"
        animate="show"
      >
        <motion.div variants={itemVariants}>
          <h1 className="text-4xl font-bold tracking-tight">Onboarding & Friction Dashboard</h1>
          <p className="text-slate-500 mt-2">Correlating new hire progress with IT support and tool adoption.</p>
        </motion.div>

        {/* Executive KPIs */}
        <motion.div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4" variants={itemVariants}>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-slate-500">Total Employees</CardTitle>
              <Users className="w-4 h-4 text-slate-400" />
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">{kpis?.totalEmployees}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-slate-500">Avg Training Completion</CardTitle>
              <Activity className="w-4 h-4 text-slate-400" />
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">{kpis?.onboardingCompletion}%</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-slate-500">Tickets per New Hire</CardTitle>
              <Ticket className="w-4 h-4 text-slate-400" />
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">{kpis?.avgTickets}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-slate-500">Avg Tool Active Mins</CardTitle>
              <Clock className="w-4 h-4 text-slate-400" />
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">{kpis?.avgToolMinutes}</div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Charts Row */}
        <motion.div className="grid grid-cols-1 lg:grid-cols-3 gap-6" variants={itemVariants}>
          
          <Card className="col-span-1 lg:col-span-1">
            <CardHeader>
              <CardTitle>Top Onboarding Blockers</CardTitle>
            </CardHeader>
            <CardContent className="h-[300px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={blockers} layout="vertical" margin={{ left: 40 }}>
                  <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#e2e8f0" />
                  <XAxis type="number" hide />
                  <YAxis dataKey="issue_type" type="category" axisLine={false} tickLine={false} tick={{fill: '#64748b', fontSize: 12}} />
                  <Tooltip cursor={{fill: '#f1f5f9'}} contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }} />
                  <Bar dataKey="count" fill="#0f172a" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          <Card className="col-span-1 lg:col-span-2">
            <CardHeader>
              <CardTitle>Tool Adoption Curve</CardTitle>
            </CardHeader>
            <CardContent className="h-[300px]">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={toolData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                  <XAxis dataKey="date" axisLine={false} tickLine={false} tick={{fill: '#64748b', fontSize: 12}} dy={10} />
                  <YAxis axisLine={false} tickLine={false} tick={{fill: '#64748b', fontSize: 12}} />
                  <Tooltip contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }} />
                  <Legend iconType="circle" wrapperStyle={{ fontSize: '12px', paddingTop: '10px' }} />
                  {toolData.length > 0 && Object.keys(toolData[0]).filter(k => k !== 'date').map((key, index) => {
                    const colors = ['#0f172a', '#3b82f6', '#10b981', '#f59e0b', '#8b5cf6'];
                    return <Line key={key} type="monotone" dataKey={key} stroke={colors[index % colors.length]} strokeWidth={3} dot={false} activeDot={{r: 6}} />
                  })}
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

        </motion.div>

        <motion.div className="grid grid-cols-1 gap-6" variants={itemVariants}>
          <Card>
            <CardHeader>
              <CardTitle>Friction Correlation (Training % vs Tickets)</CardTitle>
            </CardHeader>
            <CardContent className="h-[300px]">
              <ResponsiveContainer width="100%" height="100%">
                <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: -20 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                  <XAxis dataKey="training_completion_percent" type="number" name="Training %" unit="%" axisLine={false} tickLine={false} tick={{fill: '#64748b', fontSize: 12}} />
                  <YAxis dataKey="ticket_count" type="number" name="Tickets" axisLine={false} tickLine={false} tick={{fill: '#64748b', fontSize: 12}} />
                  <Tooltip cursor={{strokeDasharray: '3 3'}} contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }} />
                  <Scatter name="Employees" data={frictionData} fill="#ef4444" opacity={0.6} />
                </ScatterChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </motion.div>

        {/* High Friction Employees Table */}
        <motion.div variants={itemVariants}>
          <Card>
            <CardHeader>
              <CardTitle>High-Friction Employees</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="rounded-md border">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Employee ID</TableHead>
                      <TableHead>Role</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead className="text-right">Ticket Count</TableHead>
                      <TableHead className="text-right">Avg Resolution (hrs)</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {employees.map((emp) => (
                      <TableRow key={emp.employee_id} className={emp.ticket_count > 3 ? "bg-red-50/50 hover:bg-red-50" : ""}>
                        <TableCell className="font-medium">{emp.employee_id}</TableCell>
                        <TableCell>{emp.JobRole}</TableCell>
                        <TableCell>
                          <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${emp.onboarding_status === 'Completed' ? 'bg-green-100 text-green-800' : 'bg-amber-100 text-amber-800'}`}>
                            {emp.onboarding_status}
                          </span>
                        </TableCell>
                        <TableCell className="text-right font-medium text-slate-900">{emp.ticket_count}</TableCell>
                        <TableCell className="text-right">{emp.avg_resolution > 0 ? emp.avg_resolution.toFixed(1) : '-'}</TableCell>
                      </TableRow>
                    ))}
                    {employees.length === 0 && (
                      <TableRow>
                        <TableCell colSpan={5} className="text-center py-6 text-slate-500">No data found</TableCell>
                      </TableRow>
                    )}
                  </TableBody>
                </Table>
              </div>
            </CardContent>
          </Card>
        </motion.div>

      </motion.div>
    </div>
  );
}
