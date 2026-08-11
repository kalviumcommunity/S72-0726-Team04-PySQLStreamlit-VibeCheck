"use client";

import { Sheet, SheetContent, SheetDescription, SheetHeader, SheetTitle } from "@/components/ui/sheet";

interface EmployeeDrawerProps {
  employeeId: number | null;
  isOpen: boolean;
  onClose: () => void;
}

export default function EmployeeDrawer({ employeeId, isOpen, onClose }: EmployeeDrawerProps) {
  return (
    <Sheet open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <SheetContent className="sm:max-w-md bg-white border-l border-slate-200 shadow-xl">
        <SheetHeader>
          <SheetTitle className="text-2xl font-bold text-slate-900">Employee Deep-Dive</SheetTitle>
          <SheetDescription className="text-slate-500 text-base">
            Detailed friction timeline for Employee #{employeeId}.
          </SheetDescription>
        </SheetHeader>
        <div className="py-8">
          <div className="p-6 rounded-2xl bg-slate-50 border border-slate-200 text-center">
            <p className="text-sm text-slate-500">
              (Timeline and tool usage breakdown for employee {employeeId} would be rendered here.)
            </p>
          </div>
        </div>
      </SheetContent>
    </Sheet>
  );
}
