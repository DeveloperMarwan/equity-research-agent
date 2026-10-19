"use client";

import { useState, useCallback, useRef } from "react";
import { TickerInput } from "@/components/TickerInput";
import { ProgressFeed } from "@/components/ProgressFeed";
import { ResearchReport } from "@/components/ResearchReport";
import { AgentEvent, AgentName, PipelineResult } from "@/lib/types";

type AppState = "idle" | "loading" | "complete" | "error";

export default function Home() {
  const [appState, setAppState] = useState<AppState>("idle");
  const [events, setEvents] = useState<AgentEvent[]>([]);
  const [result, setResult] = useState<PipelineResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const esRef = useRef<EventSource | null>(null);

  const handleResearch = useCallback((ticker: string) => {
    if (esRef.current) {
      esRef.current.close();
    }

    setAppState("loading");
    setEvents([]);
    setResult(null);
    setError(null);

    const es = new EventSource(`/api/research/stream/${ticker}`);
    esRef.current = es;

    es.addEventListener("agent_start", (e) => {
      const data = JSON.parse((e as MessageEvent).data);
      setEvents((prev) => {
        const without = prev.filter((ev) => !(ev.agent === data.agent && ev.status === "running"));
        return [
          ...without,
          {
            agent: data.agent as AgentName,
            message: data.message,
            status: "running" as const,
            timestamp: Date.now(),
          },
        ];
      });
    });

    es.addEventListener("agent_complete", (e) => {
      const data = JSON.parse((e as MessageEvent).data);
      setEvents((prev) =>
        prev.map((ev) =>
          ev.agent === data.agent && ev.status === "running"
            ? { ...ev, message: data.message, status: "complete" as const, data: data.data }
            : ev
        )
      );
    });

    es.addEventListener("pipeline_complete", (e) => {
      const data = JSON.parse((e as MessageEvent).data) as PipelineResult;
      setResult(data);
      setAppState("complete");
      es.close();
    });

    es.addEventListener("error", (e) => {
      try {
        const data = JSON.parse((e as MessageEvent).data);
        setError(data.message);
      } catch {
        setError("An unexpected error occurred. Please try again.");
      }
      setAppState("error");
      es.close();
    });

    es.onerror = () => {
      setError(
        "Could not connect to the research backend. Make sure the backend server is running on port 8000."
      );
      setAppState("error");
      es.close();
    };
  }, []);

  return (
    <main className="min-h-screen bg-slate-950 text-white">
      <div className="max-w-5xl mx-auto px-4 py-12">
        <div className="text-center mb-10">
          <h1 className="text-4xl font-black tracking-tight mb-2">
            Equity Research Agent
          </h1>
          <p className="text-slate-400 text-lg max-w-xl mx-auto">
            AI-powered research in seconds — financials, peer comps, SEC risk factors, and a buy/hold/sell signal.
          </p>
        </div>

        <TickerInput onSubmit={handleResearch} isLoading={appState === "loading"} />

        {(appState === "loading" || appState === "complete") && events.length > 0 && (
          <ProgressFeed events={events} />
        )}

        {appState === "error" && (
          <div className="mt-6 max-w-2xl mx-auto bg-red-950 border border-red-800 rounded-xl p-5">
            <h3 className="font-semibold text-red-300 mb-1">Research Failed</h3>
            <p className="text-red-400 text-sm">{error}</p>
            <button
              onClick={() => setAppState("idle")}
              className="mt-3 text-sm text-red-300 hover:text-white transition-colors underline"
            >
              Try again
            </button>
          </div>
        )}

        {appState === "complete" && result && <ResearchReport result={result} />}

        {appState === "idle" && (
          <div className="mt-16 text-center text-slate-600 text-sm">
            <p>Enter a stock ticker above to generate a full equity research report.</p>
            <p className="mt-1">Powered by OpenAI · Yahoo Finance · SEC EDGAR · Tavily</p>
          </div>
        )}
      </div>
    </main>
  );
}
