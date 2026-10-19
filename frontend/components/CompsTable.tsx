"use client";

import { CompsData } from "@/lib/types";
import { fmtMarketCap, fmtMultiple, fmtPercent } from "@/lib/format";

export function CompsTable({ data, subjectTicker }: { data: CompsData; subjectTicker: string }) {
  return (
    <div>
      <h3 className="text-lg font-semibold text-white mb-1">Comparable Companies</h3>
      <p className="text-sm text-slate-400 mb-3">{data.search_rationale}</p>
      <div className="overflow-x-auto rounded-xl border border-slate-700">
        <table className="w-full text-sm">
          <thead className="bg-slate-800 text-slate-400 uppercase text-xs">
            <tr>
              <th className="px-4 py-3 text-left">Company</th>
              <th className="px-4 py-3 text-right">Market Cap</th>
              <th className="px-4 py-3 text-right">P/E</th>
              <th className="px-4 py-3 text-right">EV/EBITDA</th>
              <th className="px-4 py-3 text-right">Revenue</th>
              <th className="px-4 py-3 text-right">Margin</th>
              <th className="px-4 py-3 text-right">P/B</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-700/60">
            {data.comparable_companies.map((co) => (
              <tr
                key={co.ticker}
                className={`transition-colors ${
                  co.ticker === subjectTicker
                    ? "bg-blue-950 font-semibold"
                    : "bg-slate-900 hover:bg-slate-800"
                }`}
              >
                <td className="px-4 py-3 text-left">
                  <span className="font-mono text-blue-400 mr-2">{co.ticker}</span>
                  <span className="text-slate-300 text-xs">{co.name}</span>
                </td>
                <td className="px-4 py-3 text-right text-slate-200">{fmtMarketCap(co.market_cap)}</td>
                <td className="px-4 py-3 text-right text-slate-200">{fmtMultiple(co.pe_ratio)}</td>
                <td className="px-4 py-3 text-right text-slate-200">{fmtMultiple(co.ev_ebitda)}</td>
                <td className="px-4 py-3 text-right text-slate-200">{fmtMarketCap(co.revenue)}</td>
                <td className="px-4 py-3 text-right text-slate-200">{fmtPercent(co.profit_margin)}</td>
                <td className="px-4 py-3 text-right text-slate-200">{fmtMultiple(co.price_to_book)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
