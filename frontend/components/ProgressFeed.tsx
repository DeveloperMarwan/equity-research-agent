"use client";

import { AgentEvent, AgentName } from "@/lib/types";

const AGENT_LABELS: Record<AgentName, string> = {
  financial_data: "Financial Data Agent",
  comps: "Comparable Companies Agent",
  risk: "Risk Analysis Agent",
  analyst: "Analyst Agent",
  writer: "Research Writer Agent",
};

const AGENT_ICONS: Record<AgentName, string> = {
  financial_data: "📊",
  comps: "🔍",
  risk: "⚠️",
  analyst: "🧠",
  writer: "✍️",
};

function Spinner() {
  return (
    <span className="inline-block w-4 h-4 border-2 border-blue-400 border-t-transparent rounded-full animate-spin" />
  );
}

export function ProgressFeed({ events }: { events: AgentEvent[] }) {
  if (events.length === 0) return null;

  return (
    <div className="w-full max-w-2xl mx-auto mt-6 bg-slate-800 rounded-xl border border-slate-700 overflow-hidden">
      <div className="px-4 py-3 border-b border-slate-700 bg-slate-900">
        <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider">
          Agent Pipeline
        </h3>
      </div>
      <ul className="divide-y divide-slate-700/50">
        {events.map((event, i) => (
          <li key={i} className="px-4 py-3 flex items-start gap-3">
            <span className="text-lg mt-0.5 shrink-0">{AGENT_ICONS[event.agent]}</span>
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2">
                <span className="text-sm font-medium text-slate-200">
                  {AGENT_LABELS[event.agent]}
                </span>
                {event.status === "running" && <Spinner />}
                {event.status === "complete" && (
                  <span className="text-emerald-400 text-sm">✓</span>
                )}
                {event.status === "error" && (
                  <span className="text-red-400 text-sm">✗</span>
                )}
              </div>
              <p className="text-sm text-slate-400 mt-0.5 truncate">{event.message}</p>
            </div>
            <span className="text-xs text-slate-600 shrink-0 mt-1">
              {new Date(event.timestamp).toLocaleTimeString()}
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}
