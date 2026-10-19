"use client";

import { FinancialData } from "@/lib/types";
import { fmtMarketCap, fmtNumber, fmtPercent, fmtPrice, fmtMultiple } from "@/lib/format";

export function FinancialsTable({ data }: { data: FinancialData }) {
  const metrics = [
    { label: "Current Price", value: fmtPrice(data.current_price), highlight: true },
    { label: "Market Cap", value: fmtMarketCap(data.market_cap) },
    { label: "P/E Ratio (TTM)", value: fmtMultiple(data.pe_ratio) },
    { label: "Forward P/E", value: fmtMultiple(data.forward_pe) },
    { label: "Price / Book", value: fmtMultiple(data.price_to_book) },
    { label: "Revenue (TTM)", value: fmtMarketCap(data.revenue) },
    { label: "EBITDA", value: fmtMarketCap(data.ebitda) },
    { label: "EPS (TTM)", value: fmtPrice(data.eps) },
    { label: "Profit Margin", value: fmtPercent(data.profit_margin) },
    { label: "Return on Equity", value: fmtPercent(data.return_on_equity) },
    { label: "Debt / Equity", value: fmtNumber(data.debt_to_equity) },
    { label: "Beta", value: fmtNumber(data.beta) },
    { label: "Dividend Yield", value: data.dividend_yield ? fmtPercent(data.dividend_yield) : "None" },
    { label: "52W High", value: fmtPrice(data.week_52_high) },
    { label: "52W Low", value: fmtPrice(data.week_52_low) },
    { label: "Analyst Target", value: fmtPrice(data.analyst_target_price) },
  ];

  return (
    <div>
      <h3 className="text-lg font-semibold text-white mb-3">Key Financials</h3>
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {metrics.map(({ label, value, highlight }) => (
          <div
            key={label}
            className={`rounded-lg p-3 border ${
              highlight
                ? "bg-blue-950 border-blue-700"
                : "bg-slate-800 border-slate-700"
            }`}
          >
            <p className="text-xs text-slate-400 mb-1">{label}</p>
            <p className={`text-base font-semibold ${highlight ? "text-blue-300" : "text-white"}`}>
              {value}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}
