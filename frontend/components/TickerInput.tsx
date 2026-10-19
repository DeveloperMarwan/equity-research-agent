"use client";

import { useState, FormEvent } from "react";

interface Props {
  onSubmit: (ticker: string) => void;
  isLoading: boolean;
}

const POPULAR = ["AAPL", "NVDA", "JPM", "COST", "TSLA", "MSFT", "GOOGL", "AMZN"];

export function TickerInput({ onSubmit, isLoading }: Props) {
  const [value, setValue] = useState("");

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    const ticker = value.trim().toUpperCase();
    if (ticker) onSubmit(ticker);
  }

  return (
    <div className="w-full max-w-2xl mx-auto">
      <form onSubmit={handleSubmit} className="flex gap-3">
        <input
          type="text"
          value={value}
          onChange={(e) => setValue(e.target.value.toUpperCase())}
          placeholder="Enter a stock ticker (e.g. AAPL)"
          disabled={isLoading}
          maxLength={10}
          className="flex-1 px-4 py-3 rounded-xl border border-slate-700 bg-slate-800 text-white placeholder-slate-500 text-lg font-mono focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
          autoFocus
        />
        <button
          type="submit"
          disabled={isLoading}
          className={`px-6 py-3 text-white font-semibold rounded-xl transition-colors text-lg ${
            isLoading || !value.trim()
              ? "bg-slate-600 cursor-not-allowed opacity-60"
              : "bg-blue-600 hover:bg-blue-500"
          }`}
        >
          {isLoading ? "Researching…" : "Research"}
        </button>
      </form>

      <div className="mt-3 flex flex-wrap gap-2">
        <span className="text-slate-500 text-sm self-center">Try:</span>
        {POPULAR.map((t) => (
          <button
            key={t}
            onClick={() => {
              setValue(t);
              onSubmit(t);
            }}
            disabled={isLoading}
            className="px-3 py-1 text-sm font-mono bg-slate-800 hover:bg-slate-700 disabled:opacity-40 text-slate-300 rounded-lg border border-slate-700 transition-colors"
          >
            {t}
          </button>
        ))}
      </div>
    </div>
  );
}
