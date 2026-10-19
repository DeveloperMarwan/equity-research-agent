"use client";

import { Signal } from "@/lib/types";

const config: Record<Signal, { bg: string; text: string; border: string; label: string }> = {
  BUY: {
    bg: "bg-emerald-500",
    text: "text-white",
    border: "border-emerald-600",
    label: "BUY",
  },
  HOLD: {
    bg: "bg-amber-400",
    text: "text-amber-900",
    border: "border-amber-500",
    label: "HOLD",
  },
  SELL: {
    bg: "bg-red-500",
    text: "text-white",
    border: "border-red-600",
    label: "SELL",
  },
};

export function SignalBadge({ signal, size = "md" }: { signal: Signal; size?: "sm" | "md" | "lg" }) {
  const c = config[signal];
  const sizeClass =
    size === "lg"
      ? "text-2xl font-black px-6 py-2 rounded-xl"
      : size === "sm"
      ? "text-xs font-bold px-2 py-0.5 rounded"
      : "text-sm font-bold px-3 py-1 rounded-lg";

  return (
    <span className={`inline-block ${c.bg} ${c.text} border ${c.border} ${sizeClass} tracking-widest`}>
      {c.label}
    </span>
  );
}
