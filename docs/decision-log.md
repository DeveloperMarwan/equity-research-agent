# Decision Log

## Architecture Decisions

### FastAPI + SSE for backend streaming
**Decision**: Use FastAPI with Server-Sent Events (SSE) instead of WebSockets or polling.
**Why**: SSE is unidirectional (server → client) which matches the pipeline pattern exactly. Simpler than WebSockets, no handshake overhead, and native browser support via `EventSource`.

### OpenAI Agents SDK for orchestration
**Decision**: Use OpenAI Agents SDK (`openai-agents`) with GPT-4.1-mini for most agents, GPT-4.1 for the Analyst Agent.
**Why**: Matches the Week 2 bootcamp pattern. The SDK handles tool calling, retry logic, and structured output parsing via Pydantic. GPT-4.1 is used for the Analyst Agent because the buy/hold/sell reasoning requires stronger multi-step reasoning.

### Sequential pipeline over parallel agents
**Decision**: Run the 5 agents sequentially, not in parallel.
**Why**: Each agent depends on the previous agent's output (Comps Agent needs the sector from Financial Data Agent, Analyst Agent needs all three data sources). Sequential streaming also gives the user clearer progress feedback.

### edgartools for SEC filings with Tavily fallback
**Decision**: Primary risk factor source is edgartools (Item 1A from 10-K). Tavily is the fallback.
**Why**: edgartools gives structured access to actual SEC filings. However, some companies (e.g., foreign-listed ADRs) don't file 10-Ks with the SEC, so Tavily web search provides a graceful fallback.

### Next.js route handler proxy to avoid CORS
**Decision**: Proxy the SSE endpoint through a Next.js App Router route handler (`app/api/research/stream/[ticker]/route.ts`) that forwards to `BACKEND_URL` (default `localhost:8000`).
**Why**: Avoids CORS complexity in development: the browser only talks to the Next.js server. An initial attempt used `rewrites` in `next.config.ts`, but that buffered the stream and delivered every event at once when it closed; the route handler passes the upstream `ReadableStream` through unbuffered.

### Pydantic structured outputs per agent
**Decision**: Every agent has a typed `output_type` using Pydantic `BaseModel`.
**Why**: Guarantees the pipeline can safely access fields like `fin.pe_ratio` without string parsing. The SDK enforces the schema at the LLM output level.

### Dark slate UI theme
**Decision**: Dark theme (slate-950 background) with blue accents.
**Why**: Matches the aesthetic of professional financial terminals (Bloomberg, etc.). Easier to read dense numerical data against dark backgrounds.
