"use client";

import { EmployeeFriction } from "@/lib/api";

interface EmployeeCardGridProps {
  employees: EmployeeFriction[];
  onRowClick: (id: number) => void;
}

export default function EmployeeCardGrid({ employees, onRowClick }: EmployeeCardGridProps) {
  const getScoreColor = (score: number) => {
    if (score > 70) return "text-red-600 bg-red-100 border-red-200";
    if (score >= 40) return "text-yellow-600 bg-yellow-100 border-yellow-200";
    return "text-green-600 bg-green-100 border-green-200";
  };

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
      {employees.map((emp) => (
        <div 
          key={emp.employee_id} 
          onClick={() => onRowClick(emp.employee_id)}
          className="border rounded-xl p-4 bg-white shadow-sm hover:shadow-md cursor-pointer transition-all flex flex-col justify-between h-full"
        >
          <div>
            <div className="flex justify-between items-start mb-2">
              <span className="text-sm font-medium text-slate-500">#{emp.employee_id}</span>
              <span className={`inline-flex px-2 py-1 rounded-full text-xs font-semibold border ${getScoreColor(emp.friction_score)}`}>
                Score: {emp.friction_score.toFixed(1)}
              </span>
            </div>
            <h3 className="font-bold text-slate-900 truncate" title={emp.JobRole}>{emp.JobRole}</h3>
            <p className="text-sm text-slate-500">{emp.Department}</p>
          </div>
          <div className="mt-4 pt-3 border-t text-sm flex justify-between">
            <span className="text-slate-500">Status</span>
            <span className="font-medium">{emp.onboarding_status}</span>
          </div>
        </div>
      ))}
    </div>
  );
}
