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
      <SheetContent className="sm:max-w-md bg-background/70 backdrop-blur-3xl border-l border-border/50 shadow-[-10px_0_30px_rgba(0,0,0,0.5)]">
        <SheetHeader>
          <SheetTitle className="text-2xl font-bold bg-gradient-to-r from-primary to-fuchsia-400 bg-clip-text text-transparent">Employee Deep-Dive</SheetTitle>
          <SheetDescription className="text-muted-foreground text-base">
            Detailed friction timeline for Employee #{employeeId}.
          </SheetDescription>
        </SheetHeader>
        <div className="py-8">
          <div className="p-6 rounded-2xl bg-card/40 border border-border/30 backdrop-blur-md shadow-inner text-center">
            <p className="text-sm text-muted-foreground">
              (Timeline and tool usage breakdown for employee {employeeId} would be rendered here.)
            </p>
          </div>
        </div>
      </SheetContent>
    </Sheet>
  );
}
