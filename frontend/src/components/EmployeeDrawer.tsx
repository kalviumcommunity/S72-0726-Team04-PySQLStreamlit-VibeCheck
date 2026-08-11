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
      <SheetContent className="sm:max-w-md">
        <SheetHeader>
          <SheetTitle>Employee Deep-Dive</SheetTitle>
          <SheetDescription>
            Detailed friction timeline for Employee #{employeeId}.
          </SheetDescription>
        </SheetHeader>
        <div className="py-6">
          <p className="text-sm text-slate-500">
            (Timeline and tool usage breakdown for employee {employeeId} would be rendered here.)
          </p>
        </div>
      </SheetContent>
    </Sheet>
  );
}
