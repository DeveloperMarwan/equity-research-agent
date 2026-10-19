"use client";

import { useState } from "react";
import { PipelineResult } from "@/lib/types";
import { SignalBadge } from "./SignalBadge";
import { FinancialsTable } from "./FinancialsTable";
import { CompsTable } from "./CompsTable";
import { fmtPrice } from "@/lib/format";

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="bg-slate-900 rounded-xl border border-slate-700 p-6">
      <h3 className="text-base font-semibold text-slate-300 uppercase tracking-wider mb-4 pb-3 border-b border-slate-700">
        {title}
      </h3>
      {children}
    </div>
  );
}

function RiskAccordion({ risks }: { risks: string[] }) {
  const [open, setOpen] = useState(false);
  const visible = open ? risks : risks.slice(0, 3);

  return (
    <div>
      <ul className="space-y-2">
        {visible.map((risk, i) => (
          <li key={i} className="flex gap-3 text-sm text-slate-300">
            <span className="text-amber-400 shrink-0 mt-0.5">⚠</span>
            <span>{risk}</span>
          </li>
        ))}
      </ul>
      {risks.length > 3 && (
        <button
          onClick={() => setOpen(!open)}
          className="mt-3 text-sm text-blue-400 hover:text-blue-300 transition-colors"
        >
          {open ? "Show less" : `Show ${risks.length - 3} more risks`}
        </button>
      )}
    </div>
  );
}

export function ResearchReport({ result }: { result: PipelineResult }) {
  const { report, financials, comps, risks } = result;

  const priceChange =
    financials.analyst_target_price && financials.current_price
      ? ((financials.analyst_target_price - financials.current_price) / financials.current_price) * 100
      : null;

  return (
    <div className="w-full space-y-5 mt-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-slate-900 to-slate-800 rounded-xl border border-slate-700 p-6">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <div className="flex items-center gap-3 mb-1">
              <span className="text-3xl font-black font-mono text-white">{report.ticker}</span>
              <SignalBadge signal={report.signal} size="lg" />
            </div>
            <p className="text-slate-400 text-lg">{report.company_name}</p>
            <p className="text-slate-500 text-sm mt-1">
              {financials.sector} · {financials.industry}
            </p>
          </div>
          <div className="text-right">
            <p className="text-3xl font-bold text-white">{fmtPrice(financials.current_price)}</p>
            {financials.analyst_target_price && (
              <p className="text-sm text-slate-400 mt-1">
                Analyst target:{" "}
                <span className="text-white font-medium">
                  {fmtPrice(financials.analyst_target_price)}
                </span>
                {priceChange !== null && (
                  <span
                    className={`ml-2 font-semibold ${
                      priceChange >= 0 ? "text-emerald-400" : "text-red-400"
                    }`}
                  >
                    {priceChange >= 0 ? "+" : ""}
                    {priceChange.toFixed(1)}%
                  </span>
                )}
              </p>
            )}
          </div>
        </div>

        {/* Executive summary */}
        <div className="mt-5 pt-5 border-t border-slate-700">
          <p className="text-slate-300 leading-relaxed">{report.executive_summary}</p>
        </div>
      </div>

      {/* Signal card */}
      <Section title="Investment Recommendation">
        <div className="flex items-start gap-4">
          <SignalBadge signal={report.signal} size="lg" />
          <p className="text-slate-300 leading-relaxed flex-1">{report.signal_reasoning}</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-5">
          <div>
            <h4 className="text-sm font-semibold text-emerald-400 uppercase tracking-wide mb-2">
              Key Strengths
            </h4>
            <ul className="space-y-2">
              {report.key_strengths.map((s, i) => (
                <li key={i} className="flex gap-2 text-sm text-slate-300">
                  <span className="text-emerald-400 shrink-0">✓</span>
                  {s}
                </li>
              ))}
            </ul>
          </div>
          <div>
            <h4 className="text-sm font-semibold text-red-400 uppercase tracking-wide mb-2">
              Key Risks
            </h4>
            <ul className="space-y-2">
              {report.key_risks.map((r, i) => (
                <li key={i} className="flex gap-2 text-sm text-slate-300">
                  <span className="text-red-400 shrink-0">✗</span>
                  {r}
                </li>
              ))}
            </ul>
          </div>
        </div>
      </Section>

      {/* Financials */}
      <Section title="Financial Overview">
        <FinancialsTable data={financials} />
        <div className="mt-5 pt-5 border-t border-slate-700">
          <p className="text-slate-300 text-sm leading-relaxed">{report.financials_summary}</p>
        </div>
      </Section>

      {/* Comps */}
      <Section title="Peer Comparison">
        <CompsTable data={comps} subjectTicker={report.ticker} />
        <div className="mt-5 pt-5 border-t border-slate-700">
          <p className="text-slate-300 text-sm leading-relaxed">{report.comps_analysis}</p>
        </div>
      </Section>

      {/* Company overview */}
      <Section title="Company Overview">
        <p className="text-slate-300 text-sm leading-relaxed whitespace-pre-line">
          {report.company_overview}
        </p>
      </Section>

      {/* Risk factors */}
      <Section title={`Risk Factors · SEC 10-K ${risks.filing_year}`}>
        <RiskAccordion risks={risks.risk_factors} />
        <div className="mt-5 pt-5 border-t border-slate-700">
          <p className="text-slate-300 text-sm leading-relaxed">{report.risk_summary}</p>
        </div>
      </Section>

      {/* Recommendation detail */}
      <Section title="Full Recommendation">
        <p className="text-slate-300 text-sm leading-relaxed whitespace-pre-line">
          {report.recommendation}
        </p>
      </Section>

      <p className="text-xs text-slate-600 text-center pb-4">
        This report is AI-generated for educational purposes only and does not constitute financial advice.
        Always consult a licensed financial advisor before making investment decisions.
      </p>
    </div>
  );
}
