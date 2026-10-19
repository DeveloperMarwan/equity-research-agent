# Equity Research Agent

An autonomous multi-agent system that turns a stock ticker into a structured equity research report. Enter a ticker such as `AAPL` and, in roughly one to two minutes, five specialised AI agents gather financial data, find peer companies, pull risk factors from SEC filings, form a BUY / HOLD / SELL view, and write the report. Progress streams to the browser live as each agent finishes.

> **Disclaimer.** Reports are **AI-generated**, produced **for educational purposes only**, and are **not financial advice**. Figures come from web search results interpreted by a language model and may be wrong, incomplete or out of date. Do not make investment decisions based on this output.

This application was built with [Claude Code](https://claude.com/claude-code) during the **Agentic AI Engineering Bootcamp**.

## Architecture

Five agents run **sequentially**; each one's typed (Pydantic) output feeds the next. The backend streams progress to the browser over Server-Sent Events (SSE).

```
 Browser (Next.js UI)
      │  GET /api/research/stream/{ticker}      (Next.js route handler passes the stream through)
      ▼
 FastAPI backend ── SSE: agent_start / agent_complete / pipeline_complete / error
      │
      ▼
 ┌──────────────────────────┐
 │ 1. Financial Data Agent  │  Tavily web search ──► FinancialData
 └────────────┬─────────────┘
              ▼
 ┌──────────────────────────┐
 │ 2. Comparable Companies  │  Tavily web search ──► CompsData (3 peers + multiples)
 │    Agent                 │
 └────────────┬─────────────┘
              ▼
 ┌──────────────────────────┐
 │ 3. Risk Analysis Agent   │  SEC EDGAR 10-K (edgartools), Tavily fallback
 └────────────┬─────────────┘  ──► RiskData (5-8 risk factors)
              ▼
 ┌──────────────────────────┐
 │ 4. Analyst Agent         │  no tools; synthesises 1-3 ──► AnalystOutput
 └────────────┬─────────────┘  (BUY / HOLD / SELL + reasoning)
              ▼
 ┌──────────────────────────┐
 │ 5. Research Writer Agent │  no tools; ──► FinalReport (sectioned prose)
 └────────────┬─────────────┘
              ▼
   `pipeline_complete` event ──► UI renders the full report
```

| # | Agent | Model | Tools / data source | Output |
|---|-------|-------|---------------------|--------|
| 1 | Financial Data | `gpt-4.1-mini` | Tavily search (4 targeted queries) | Price, market cap, P/E, revenue, EBITDA, margins, ... |
| 2 | Comparable Companies | `gpt-4.1-mini` | Tavily search | 3 peers with market cap, P/E, EV/EBITDA, revenue, margin, P/B |
| 3 | Risk Analysis | `gpt-4.1-mini` | `edgartools` (10-K Item 1A), Tavily fallback | 5-8 risk statements, filing year |
| 4 | Analyst | `gpt-4.1` | none | Signal, valuation summary, relative valuation, strengths, risks |
| 5 | Research Writer | `gpt-4.1-mini` | none | Overview, financials, comps, risk, recommendation, executive summary |

Built with: Python, FastAPI, [OpenAI Agents SDK](https://github.com/openai/openai-agents-python), Pydantic, Tavily, edgartools · Next.js 16, React 19, TypeScript, Tailwind CSS 4.

```
backend/
  main.py          FastAPI app, CORS, /health and the SSE endpoint
  pipeline.py      Orchestrates the 5 agents and emits SSE events
  models.py        Pydantic schemas for every agent's input/output
  agents/          One file per agent
  tools/           Tavily and EDGAR tools (plus an unused Yahoo Finance tool)
frontend/
  app/             Next.js App Router; app/api/research/stream/[ticker] proxies the SSE stream
  components/      TickerInput, ProgressFeed, ResearchReport, CompsTable, ...
  lib/             Shared TypeScript types and formatters
docs/
  Capstone_Report.md       Project report
  decision-log.md          Architecture decisions
```

## Prerequisites

- **Python 3.9 or newer** (developed and tested on 3.9.10)
- **Node.js 20.9 or newer** and npm (tested on Node 24)
- An **OpenAI API key** and a **Tavily API key** (see below)

## Environment variables

Configured in `backend/.env` (copy from `backend/.env.example`). This file is git-ignored; never commit it.

| Variable | Required | Used for |
|----------|----------|----------|
| `OPENAI_API_KEY` | Yes | All five agents. The API returns HTTP 500 if it is missing. |
| `TAVILY_API_KEY` | Yes | Web search in the Financial Data, Comparable Companies and Risk agents. |
| `EDGAR_IDENTITY` | Recommended | Contact identity the SEC requires on EDGAR requests, e.g. `Your Name you@example.com`. If unset, the Risk Analysis Agent skips SEC filings and uses web search only. |

The frontend has one optional variable, `BACKEND_URL` (default `http://localhost:8000`), read by the Next.js route handler. Set it in `frontend/.env.local` only if the backend runs elsewhere.

## Setup and run

You need two terminals. Run all commands from the repository root unless stated otherwise.

### 1. Backend

```bash
python3 -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r backend/requirements.txt

cp backend/.env.example backend/.env # then edit backend/.env and add your real keys

uvicorn backend.main:app --reload --port 8000
```

Check it is up: `curl http://localhost:8000/health` should return `{"status":"ok","service":"equity-research-agent"}`.

> Run `uvicorn` from the repository root (not from inside `backend/`), because the app uses package imports (`backend.main`).

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open <http://localhost:3000>, enter a ticker (try `AAPL`, `NVDA`, `JPM`, `COST` or `TSLA`) and wait for the report. A full run typically takes 60-120 seconds.

For a production build: `npm run build && npm run start`.

## Example output

The backend streams named SSE events. A successful run looks like this (messages shortened; `...` marks elided content):

```
event: agent_start
data: {"agent": "financial_data", "message": "Researching financial data for AAPL..."}

event: agent_complete
data: {"agent": "financial_data", "message": "Financial data retrieved for <Company Name>", "data": {...}}

... same start/complete pairs for "comps", "risk" and "analyst" ...

event: agent_start
data: {"agent": "writer", "message": "Writing final research report..."}

: keepalive                      <- comment lines every 12s while the writer works

event: pipeline_complete
data: {"report": {...}, "financials": {...}, "comps": {...}, "risks": {...}, "analysis": {...}}
```

The `report` object in `pipeline_complete` has this shape (values are descriptions, not real data):

```json
{
  "ticker": "<TICKER>",
  "company_name": "<legal name>",
  "executive_summary": "<3-5 sentences: signal, core reason, top risk>",
  "company_overview": "<2-3 paragraphs>",
  "financials_summary": "<2-3 paragraphs>",
  "comps_analysis": "<2-3 paragraphs>",
  "risk_summary": "<1-2 paragraphs>",
  "recommendation": "<2-3 paragraphs>",
  "signal": "BUY | HOLD | SELL",
  "signal_reasoning": "<2-3 sentences grounded in the data>",
  "key_strengths": ["..."],
  "key_risks": ["..."]
}
```

If something fails, the stream emits `event: error` with a `message`, for example an invalid OpenAI key or a rate limit.

## Known limitations

- **Data quality depends on web search.** Financials and peer multiples are extracted by an LLM from Tavily search snippets, not from a market-data feed. Values can be stale, mis-parsed (units, fiscal periods) or `null` for thinly covered companies. Nothing is cross-checked.
- **No real-time prices.** Search results can be hours or days old.
- **SEC risk factors are heuristic.** The 10-K tool takes up to ten reasonably sized lines from Item 1A rather than parsing individual risk headings. Foreign filers and companies without a 10-K fall back to web search.
- **The signal is qualitative.** It is an LLM's reasoning over peer multiples, not a DCF or a backtested model.
- **One ticker at a time, sequential, slow.** Roughly 60-120 seconds per run, and each run makes paid OpenAI and Tavily calls. Cost is not capped.
- **Not production-hardened.** No authentication, rate limiting, caching, or automated tests. CORS only allows `localhost:3000`. The SSE endpoint is public if you expose the backend.
- **Failures stop the run.** If any agent fails, the pipeline ends with an error event and does not retry or skip the agent.
- **SEC filings need your own identity.** The SEC asks API users to identify themselves. Set `EDGAR_IDENTITY` to your own name and email; without it, risk factors come from web search only, which is less authoritative.
- **Dependencies are pinned for a reason.** `openai-agents==0.0.19` breaks with newer `openai` releases, so `openai` is pinned in `backend/requirements.txt`. Upgrade both together.
- **Unused code.** `backend/tools/yfinance_tool.py` (a direct Yahoo Finance client) and the `yfinance` dependency are not used by any agent; Yahoo's endpoints rate-limit automated access, which is why Tavily is the data source.

## Further reading

- [`docs/Capstone_Report.md`](docs/Capstone_Report.md) - design rationale, prompts, results and future improvements
- [`docs/decision-log.md`](docs/decision-log.md) - architecture decisions

## About this project

Capstone project for the **Agentic AI Engineering Bootcamp**, built with **Claude Code**. Author: Marwan Aziz.

Released under the [MIT License](LICENSE).

Reports are AI-generated, for educational purposes only, and are not financial advice.
