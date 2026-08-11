"use client";

import { EmployeeFriction } from "@/lib/api";
import { motion } from "framer-motion";

interface EmployeeCardGridProps {
  employees: EmployeeFriction[];
  onRowClick: (id: number) => void;
}

export default function EmployeeCardGrid({ employees, onRowClick }: EmployeeCardGridProps) {
  const getScoreColor = (score: number) => {
    if (score > 70) return "text-destructive border-destructive/50 shadow-[0_0_10px_rgba(220,38,38,0.2)] bg-destructive/10";
    if (score >= 40) return "text-orange-400 bg-orange-500/10 border-orange-500/30";
    return "text-emerald-400 bg-emerald-500/10 border-emerald-500/30";
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
          className="border border-border/50 rounded-2xl p-5 bg-background/40 backdrop-blur-md shadow-lg hover:shadow-[0_0_20px_rgba(124,58,237,0.15)] hover:border-primary/50 cursor-pointer transition-all duration-300 flex flex-col justify-between h-full group"
        >
          <div>
            <div className="flex justify-between items-start mb-3">
              <span className="text-sm font-medium text-muted-foreground bg-card/50 px-2 py-1 rounded-md border border-border/50">#{emp.employee_id}</span>
              <span className={`inline-flex px-3 py-1 rounded-full text-xs font-semibold border backdrop-blur-sm ${getScoreColor(emp.friction_score)}`}>
                Score: {emp.friction_score.toFixed(1)}
              </span>
            </div>
            <h3 className="font-bold text-foreground text-lg truncate group-hover:text-primary transition-colors" title={emp.JobRole}>{emp.JobRole}</h3>
            <p className="text-sm text-muted-foreground mt-1">{emp.Department}</p>
          </div>
          <div className="mt-5 pt-4 border-t border-border/30 text-sm flex justify-between items-center">
            <span className="text-muted-foreground">Status</span>
            <span className="font-medium bg-secondary text-secondary-foreground px-3 py-1 rounded-lg shadow-inner">{emp.onboarding_status}</span>
          </div>
        </motion.div>
      ))}
    </motion.div>
  );
}
