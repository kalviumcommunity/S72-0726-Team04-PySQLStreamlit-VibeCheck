"use client";

import { motion } from "framer-motion";
import { ReactNode } from "react";
import { Card } from "@/components/ui/card";

export default function AnimatedCard({ children, delay = 0 }: { children: ReactNode; delay?: number }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 30, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      whileHover={{ y: -5, scale: 1.02 }}
      transition={{ 
        duration: 0.5, 
        delay, 
        type: "spring", 
        stiffness: 100, 
        damping: 15 
      }}
      className="h-full"
    >
      <Card className="h-full w-full bg-white border border-slate-200 shadow-sm hover:shadow-md transition-all duration-300">
        {children}
      </Card>
    </motion.div>
  );
}
