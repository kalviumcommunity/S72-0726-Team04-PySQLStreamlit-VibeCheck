"use client";

import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { EmployeeFriction } from "@/lib/api";

interface EmployeeTableProps {
  employees: EmployeeFriction[];
  onRowClick: (id: number) => void;
}

export default function EmployeeTable({ employees, onRowClick }: EmployeeTableProps) {
  
  const getScoreColor = (score: number) => {
    if (score > 70) return "text-red-600 bg-red-100";
    if (score >= 40) return "text-yellow-600 bg-yellow-100";
    return "text-green-600 bg-green-100";
  };

  return (
    <div className="rounded-md border">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>ID</TableHead>
            <TableHead>Role</TableHead>
            <TableHead>Department</TableHead>
            <TableHead>Status</TableHead>
            <TableHead className="text-right">Friction Score</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {employees.map((emp) => (
            <TableRow key={emp.employee_id} onClick={() => onRowClick(emp.employee_id)} className="cursor-pointer hover:bg-slate-50 transition-colors">
              <TableCell className="font-medium">{emp.employee_id}</TableCell>
              <TableCell>{emp.JobRole}</TableCell>
              <TableCell>{emp.Department}</TableCell>
              <TableCell>{emp.onboarding_status}</TableCell>
              <TableCell className="text-right">
                <span className={`inline-flex px-2 py-1 rounded-full text-xs font-semibold ${getScoreColor(emp.friction_score)}`}>
                  {emp.friction_score.toFixed(1)}
                </span>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
