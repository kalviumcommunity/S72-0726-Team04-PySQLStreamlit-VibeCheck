"use client";

import { motion } from "framer-motion";
import { ReactNode } from "react";
import { Card } from "@/components/ui/card";

export default function AnimatedCard({ children, delay = 0 }: { children: ReactNode; delay?: number }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay, ease: "easeOut" }}
      className="h-full"
    >
      <Card className="h-full w-full">{children}</Card>
    </motion.div>
  );
}
