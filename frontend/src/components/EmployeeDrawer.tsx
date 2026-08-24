"use client";

import { useEffect, useState } from "react";
import { Sheet, SheetContent, SheetDescription, SheetHeader, SheetTitle } from "@/components/ui/sheet";
import { fetchEmployeeDetail, EmployeeDetail } from "@/lib/api";
import { User, AlertTriangle, ShieldCheck, Ticket, Wrench, Calendar, CheckCircle2, Clock } from "lucide-react";

interface EmployeeDrawerProps {
  employeeId: number | null;
  isOpen: boolean;
  onClose: () => void;
}

export default function EmployeeDrawer({ employeeId, isOpen, onClose }: EmployeeDrawerProps) {
  const [detail, setDetail] = useState<EmployeeDetail | null>(null);
  const [loading, setLoading] = useState<boolean>(false);

  useEffect(() => {
    if (isOpen && employeeId !== null) {
      setLoading(true);
      fetchEmployeeDetail(employeeId)
        .then((data) => {
          setDetail(data);
          setLoading(false);
        })
        .catch(() => {
          setDetail(null);
          setLoading(false);
        });
    } else {
      setDetail(null);
    }
  }, [isOpen, employeeId]);

  const getScoreBadge = (score: number) => {
    if (score > 70) {
      return "bg-rose-50 border-rose-200 text-rose-700 font-semibold";
    }
    if (score > 40) {
      return "bg-amber-50 border-amber-200 text-amber-700 font-semibold";
    }
    return "bg-emerald-50 border-emerald-200 text-emerald-700 font-semibold";
  };

  return (
    <Sheet open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <SheetContent className="w-full sm:max-w-xl overflow-y-auto bg-slate-900 border-l border-slate-800 text-slate-100 shadow-2xl p-6">
        <SheetHeader className="pb-4 border-b border-slate-800">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-3.5 rounded-xl bg-indigo-500/10 border border-indigo-500/20 text-indigo-400">
                <User className="w-6 h-6" />
              </div>
              <div>
                <SheetTitle className="text-xl font-bold text-slate-50">
                  {detail ? `Employee #${detail.employee_id}` : `Employee #${employeeId}`}
                </SheetTitle>
                <SheetDescription className="text-slate-400 text-xs mt-0.5">
                  {detail ? `${detail.JobRole} • ${detail.Department}` : "Fetching details..."}
                </SheetDescription>
              </div>
            </div>

            {detail && (
              <span className={`px-3 py-1 text-xs rounded-full border ${getScoreBadge(detail.friction_score)}`}>
                Friction Score: {detail.friction_score}
              </span>
            )}
          </div>
        </SheetHeader>

        {loading ? (
          <div className="py-20 flex flex-col items-center justify-center space-y-3">
            <div className="w-8 h-8 border-3 border-indigo-500 border-t-transparent rounded-full animate-spin"></div>
            <p className="text-slate-400 text-xs animate-pulse">Loading employee profile & telemetry...</p>
          </div>
        ) : detail ? (
          <div className="py-6 space-y-6">
            {/* Risk & Friction Overview Cards */}
            <div className="grid grid-cols-2 gap-3">
              <div className="p-4 rounded-xl bg-slate-800/60 border border-slate-700/60">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-medium text-slate-400">Friction Score</span>
                  <AlertTriangle className={`w-4 h-4 ${detail.friction_score > 70 ? "text-rose-400" : "text-amber-400"}`} />
                </div>
                <div className="mt-2 text-2xl font-bold text-slate-100">{detail.friction_score} / 100</div>
                <p className="text-[11px] text-slate-400 mt-1">Calculated from tickets & onboarding completion</p>
              </div>

              <div className="p-4 rounded-xl bg-slate-800/60 border border-slate-700/60">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-medium text-slate-400">ML Risk Score</span>
                  <ShieldCheck className="w-4 h-4 text-indigo-400" />
                </div>
                <div className="mt-2 text-2xl font-bold text-indigo-300">
                  {detail.predicted_risk !== undefined ? `${detail.predicted_risk}%` : "N/A"}
                </div>
                <p className="text-[11px] text-slate-400 mt-1">XGBoost ML predictive model</p>
              </div>
            </div>

            {/* Profile & Onboarding Metadata */}
            <div className="p-4 rounded-xl bg-slate-800/40 border border-slate-700/40 space-y-3">
              <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-400">Onboarding Details</h4>
              
              <div className="grid grid-cols-2 gap-4 text-xs">
                <div>
                  <span className="text-slate-500 block">Status</span>
                  <span className="font-semibold text-slate-200 capitalize">{detail.onboarding_status}</span>
                </div>
                <div>
                  <span className="text-slate-500 block">Onboarding Duration</span>
                  <span className="font-semibold text-slate-200">{detail.onboarding_days} Days</span>
                </div>
                <div>
                  <span className="text-slate-500 block">Buddy Assigned</span>
                  <span className="font-semibold text-slate-200">{detail.buddy_assigned}</span>
                </div>
                <div>
                  <span className="text-slate-500 block">Manager Assigned</span>
                  <span className="font-semibold text-slate-200">{detail.manager_assigned}</span>
                </div>
              </div>

              {/* Progress Bar */}
              <div className="pt-2">
                <div className="flex justify-between text-xs mb-1">
                  <span className="text-slate-400 font-medium">Training Progress</span>
                  <span className="text-indigo-400 font-bold">{detail.training_completion_percent}%</span>
                </div>
                <div className="w-full bg-slate-700 h-2 rounded-full overflow-hidden">
                  <div
                    className="bg-gradient-to-r from-indigo-500 to-purple-500 h-full rounded-full transition-all duration-500"
                    style={{ width: `${Math.min(100, Math.max(0, detail.training_completion_percent))}%` }}
                  />
                </div>
              </div>
            </div>

            {/* Support Tickets Section */}
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Ticket className="w-4 h-4 text-amber-400" />
                  <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-300">
                    Support Tickets ({detail.tickets?.length || 0})
                  </h4>
                </div>
              </div>

              {detail.tickets && detail.tickets.length > 0 ? (
                <div className="space-y-2 max-h-48 overflow-y-auto pr-1">
                  {detail.tickets.map((t) => (
                    <div key={t.ticket_id} className="p-3 rounded-lg bg-slate-800/80 border border-slate-700/60 flex items-center justify-between text-xs">
                      <div>
                        <div className="font-medium text-slate-200">Ticket #{t.ticket_id} - {t.issue_type}</div>
                        <div className="text-slate-400 flex items-center gap-1 mt-0.5">
                          <Clock className="w-3 h-3 text-slate-500" />
                          Resolution: {t.resolution_hours} hrs
                        </div>
                      </div>
                      <span className="px-2 py-0.5 rounded bg-amber-500/10 text-amber-300 text-[10px] font-medium border border-amber-500/20">
                        Logged
                      </span>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="p-4 text-center rounded-lg bg-slate-800/30 border border-slate-700/30 text-xs text-slate-500">
                  No support tickets reported.
                </div>
              )}
            </div>

            {/* Tool Usage Breakdown */}
            <div className="space-y-3">
              <div className="flex items-center gap-2">
                <Wrench className="w-4 h-4 text-indigo-400" />
                <h4 className="text-xs font-semibold uppercase tracking-wider text-slate-300">
                  Tool Usage Telemetry
                </h4>
              </div>

              {detail.tool_usage && detail.tool_usage.length > 0 ? (
                <div className="grid grid-cols-2 gap-2 max-h-48 overflow-y-auto pr-1">
                  {detail.tool_usage.map((tu, idx) => (
                    <div key={idx} className="p-2.5 rounded-lg bg-slate-800/60 border border-slate-700/40 text-xs flex items-center justify-between">
                      <span className="text-slate-300 font-medium truncate max-w-[120px]">{tu.tool_name}</span>
                      <span className="text-indigo-400 font-mono font-semibold">{tu.active_minutes}m</span>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="p-4 text-center rounded-lg bg-slate-800/30 border border-slate-700/30 text-xs text-slate-500">
                  No tool usage telemetry logged.
                </div>
              )}
            </div>
          </div>
        ) : (
          <div className="py-12 text-center text-slate-500 text-sm">
            Failed to load details for Employee #{employeeId}.
          </div>
        )}
      </SheetContent>
    </Sheet>
  );
}
