"use client";

import { EmployeeFriction } from "@/lib/api";
import { motion } from "framer-motion";

interface EmployeeCardGridProps {
  employees: EmployeeFriction[];
  onRowClick: (id: number) => void;
}

export default function EmployeeCardGrid({ employees, onRowClick }: EmployeeCardGridProps) {
  const getScoreColor = (score: number) => {
    if (score > 70) return "text-red-700 border-red-200 bg-red-50";
    if (score >= 40) return "text-yellow-700 bg-yellow-50 border-yellow-200";
    return "text-green-700 bg-green-50 border-green-200";
  };

  const container = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  };

  const item = {
    hidden: { opacity: 0, y: 20 },
    show: { opacity: 1, y: 0, transition: { type: "spring", stiffness: 100 } }
  };

  return (
    <motion.div 
      variants={container} 
      initial="hidden" 
      animate="show" 
      className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4"
    >
      {employees.map((emp) => (
        <motion.div 
          key={emp.employee_id}
          variants={item}
          whileHover={{ y: -5, scale: 1.02 }}
          onClick={() => onRowClick(emp.employee_id)}
          className="border border-slate-200 rounded-2xl p-5 bg-white backdrop-blur-md shadow-sm hover:shadow-md cursor-pointer transition-all duration-300 flex flex-col justify-between h-full group"
        >
          <div>
            <div className="flex justify-between items-start mb-3">
              <span className="text-sm font-medium text-slate-500 bg-slate-50 px-2 py-1 rounded-md border border-slate-100">#{emp.employee_id}</span>
              <div className="flex flex-col items-end gap-1">
                <span className={`inline-flex px-3 py-1 rounded-full text-xs font-semibold border backdrop-blur-sm ${getScoreColor(emp.friction_score)}`}>
                  Score: {emp.friction_score.toFixed(1)}
                </span>
                {emp.predicted_risk !== undefined && (
                  <span className={`inline-flex px-3 py-1 rounded-full text-xs font-semibold border backdrop-blur-sm ${getScoreColor(emp.predicted_risk)}`}>
                    ML Risk: {emp.predicted_risk.toFixed(1)}%
                  </span>
                )}
              </div>
            </div>
            <h3 className="font-bold text-slate-900 text-lg truncate group-hover:text-slate-700 transition-colors" title={emp.JobRole}>{emp.JobRole}</h3>
            <p className="text-sm text-slate-500 mt-1">{emp.Department}</p>
          </div>
          <div className="mt-5 pt-4 border-t border-slate-100 text-sm flex justify-between items-center">
            <span className="text-slate-500">Status</span>
            <span className="font-medium bg-slate-100 text-slate-800 px-3 py-1 rounded-lg">{emp.onboarding_status}</span>
          </div>
        </motion.div>
      ))}
    </motion.div>
  );
}
