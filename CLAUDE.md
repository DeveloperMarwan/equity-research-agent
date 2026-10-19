# Equity Research Agent — Capstone Project

## Project Overview
An autonomous multi-agent system that generates professional equity research reports. The user enters a stock ticker and within ~60 seconds receives a full report with financials, peer comparisons, SEC risk factors, and a buy/hold/sell signal — all streamed live.

## Architecture

```
backend/     Python FastAPI — agent pipeline, SSE streaming
frontend/    Next.js 16 + TypeScript + Tailwind CSS — UI
```

## Running the App

**Backend** (Python 3.9+, run from the repository root):
```bash
pip install -r backend/requirements.txt
cp backend/.env.example backend/.env   # then fill in API keys
uvicorn backend.main:app --reload --port 8000
```

**Frontend**:
```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3000.

## Environment Variables (backend/.env)
```
OPENAI_API_KEY=...
TAVILY_API_KEY=...
```

## Agent Pipeline

| # | Agent | Data Source | Output |
|---|-------|-------------|--------|
| 1 | Financial Data Agent | Tavily search | Price, market cap, P/E, revenue, EBITDA |
| 2 | Comparable Companies Agent | Tavily search | 3 peer companies with multiples |
| 3 | Risk Analysis Agent | edgartools (10-K) + Tavily | 5-8 material risk factors |
| 4 | Analyst Agent | All above | BUY/HOLD/SELL signal + reasoning |
| 5 | Research Writer Agent | All above | Full formatted research report |

## Key Files
- `backend/pipeline.py` — SSE event generator, orchestrates all 5 agents
- `backend/models.py` — Pydantic schemas for all agent inputs/outputs
- `backend/agents/` — One file per agent (financial_data, comps, risk, analyst, writer)
- `backend/tools/` — Tavily and edgartools function tools (`yfinance_tool.py` is unused)
- `frontend/components/` — TickerInput, ProgressFeed, ResearchReport, etc.
- `frontend/lib/types.ts` — Shared TypeScript interfaces

## Test Tickers
AAPL, NVDA, JPM, COST, TSLA
