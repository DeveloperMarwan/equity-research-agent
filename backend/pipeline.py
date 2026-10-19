from __future__ import annotations
import json
import asyncio
from typing import AsyncGenerator, Optional
from agents import Runner

from .agents.financial_data import financial_data_agent
from .agents.comps import comps_agent
from .agents.risk import risk_agent
from .agents.analyst import analyst_agent
from .agents.writer import writer_agent
from .models import FinancialData, CompsData, RiskData, AnalystOutput

_KEEPALIVE_INTERVAL = 12.0  # seconds between SSE keepalive pings


def _sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data)}\n\n"


def _keepalive() -> str:
    """SSE comment line — browsers ignore it, but it keeps the connection alive."""
    return ": keepalive\n\n"



def _fmt_market_cap(val: Optional[float]) -> str:
    if val is None:
        return "N/A"
    if val >= 1e12:
        return f"${val/1e12:.2f}T"
    if val >= 1e9:
        return f"${val/1e9:.2f}B"
    if val >= 1e6:
        return f"${val/1e6:.2f}M"
    return f"${val:,.0f}"


def _build_comps_prompt(ticker: str, fin: FinancialData) -> str:
    return (
        f"Find 3 comparable companies for {ticker} ({fin.company_name}).\n"
        f"Sector: {fin.sector}, Industry: {fin.industry}\n"
        f"Market cap: {_fmt_market_cap(fin.market_cap)}\n"
        f"Current P/E: {fin.pe_ratio}, Revenue: {_fmt_market_cap(fin.revenue)}\n"
        f"Look for direct business model peers with similar scale and sector exposure."
    )


def _build_analyst_prompt(fin: FinancialData, comps: CompsData, risk: RiskData) -> str:
    comps_table = "\n".join([
        f"  - {c.name} ({c.ticker}): P/E={c.pe_ratio}, EV/EBITDA={c.ev_ebitda}, "
        f"Revenue={_fmt_market_cap(c.revenue)}, Margin={c.profit_margin}"
        for c in comps.comparable_companies
    ])

    return (
        f"Analyze {fin.ticker} ({fin.company_name}) and produce a BUY/HOLD/SELL signal.\n\n"
        f"=== FINANCIAL DATA ===\n"
        f"Price: ${fin.current_price}, Market Cap: {_fmt_market_cap(fin.market_cap)}\n"
        f"P/E: {fin.pe_ratio}, Forward P/E: {fin.forward_pe}\n"
        f"Revenue: {_fmt_market_cap(fin.revenue)}, EBITDA: {_fmt_market_cap(fin.ebitda)}\n"
        f"Profit Margin: {fin.profit_margin}, ROE: {fin.return_on_equity}\n"
        f"Debt/Equity: {fin.debt_to_equity}, Beta: {fin.beta}\n"
        f"52W High: ${fin.week_52_high}, 52W Low: ${fin.week_52_low}\n"
        f"Analyst Target: ${fin.analyst_target_price}\n\n"
        f"=== PEER COMPARABLES ===\n{comps_table}\n"
        f"Comps rationale: {comps.search_rationale}\n\n"
        f"=== RISK FACTORS ===\n"
        + "\n".join([f"- {r}" for r in risk.risk_factors])
    )


def _build_writer_prompt(
    fin: FinancialData,
    comps: CompsData,
    risk: RiskData,
    analysis: AnalystOutput,
) -> str:
    comps_str = "\n".join([
        f"  {c.name} ({c.ticker}): P/E={c.pe_ratio}, EV/EBITDA={c.ev_ebitda}, "
        f"Revenue={_fmt_market_cap(c.revenue)}, P/B={c.price_to_book}"
        for c in comps.comparable_companies
    ])

    return (
        f"Write a professional equity research report for {fin.ticker} ({fin.company_name}).\n\n"
        f"Ticker: {fin.ticker}\nCompany Name: {fin.company_name}\n\n"
        f"=== FINANCIALS ===\n"
        f"Sector: {fin.sector} | Industry: {fin.industry}\n"
        f"Price: ${fin.current_price} | Market Cap: {_fmt_market_cap(fin.market_cap)}\n"
        f"P/E: {fin.pe_ratio} | Fwd P/E: {fin.forward_pe} | P/B: {fin.price_to_book}\n"
        f"Revenue: {_fmt_market_cap(fin.revenue)} | EBITDA: {_fmt_market_cap(fin.ebitda)}\n"
        f"Profit Margin: {fin.profit_margin} | ROE: {fin.return_on_equity}\n"
        f"D/E: {fin.debt_to_equity} | Beta: {fin.beta} | Div Yield: {fin.dividend_yield}\n"
        f"EPS: {fin.eps} | 52W: ${fin.week_52_low} – ${fin.week_52_high}\n"
        f"Analyst Target: ${fin.analyst_target_price}\n\n"
        f"=== PEER COMPS ===\n{comps_str}\n"
        f"Rationale: {comps.search_rationale}\n\n"
        f"=== RISK FACTORS ===\n"
        + "\n".join([f"- {r}" for r in risk.risk_factors])
        + f"\n\n=== ANALYST OUTPUT ===\n"
        f"Signal: {analysis.signal}\n"
        f"Reasoning: {analysis.signal_reasoning}\n"
        f"Valuation: {analysis.valuation_summary}\n"
        f"Relative Val: {analysis.relative_valuation}\n"
        f"Strengths: {', '.join(analysis.key_strengths)}\n"
        f"Risks: {', '.join(analysis.key_risks)}\n"
        f"Price Target: {analysis.price_target_rationale}"
    )


async def run_research_pipeline(ticker: str) -> AsyncGenerator[str, None]:
    ticker = ticker.upper().strip()

    # Agent 1: Financial Data
    yield _sse("agent_start", {
        "agent": "financial_data",
        "message": f"Researching financial data for {ticker}..."
    })
    try:
        fin_result = await _collect_agent_result(financial_data_agent, ticker)
        fin: FinancialData = fin_result.final_output
        yield _sse("agent_complete", {
            "agent": "financial_data",
            "message": f"Financial data retrieved for {fin.company_name}",
            "data": fin.model_dump()
        })
    except Exception as e:
        yield _sse("error", {"message": f"Financial data fetch failed: {str(e)}"})
        return

    # Agent 2: Comps
    yield _sse("agent_start", {
        "agent": "comps",
        "message": f"Identifying comparable companies for {ticker}..."
    })
    try:
        comps_prompt = _build_comps_prompt(ticker, fin)
        comps_result = await _collect_agent_result(comps_agent, comps_prompt)
        comps: CompsData = comps_result.final_output
        yield _sse("agent_complete", {
            "agent": "comps",
            "message": f"Found {len(comps.comparable_companies)} comparable companies",
            "data": comps.model_dump()
        })
    except Exception as e:
        yield _sse("error", {"message": f"Comps analysis failed: {str(e)}"})
        return

    # Agent 3: Risk
    yield _sse("agent_start", {
        "agent": "risk",
        "message": f"Fetching SEC 10-K risk factors for {ticker}..."
    })
    try:
        risk_result = await _collect_agent_result(risk_agent, ticker)
        risk: RiskData = risk_result.final_output
        yield _sse("agent_complete", {
            "agent": "risk",
            "message": f"Identified {len(risk.risk_factors)} risk factors",
            "data": risk.model_dump()
        })
    except Exception as e:
        yield _sse("error", {"message": f"Risk analysis failed: {str(e)}"})
        return

    # Agent 4: Analyst
    yield _sse("agent_start", {
        "agent": "analyst",
        "message": "Synthesizing data and generating buy/hold/sell signal..."
    })
    try:
        analyst_prompt = _build_analyst_prompt(fin, comps, risk)
        analyst_result = await _collect_agent_result(analyst_agent, analyst_prompt)
        analysis: AnalystOutput = analyst_result.final_output
        yield _sse("agent_complete", {
            "agent": "analyst",
            "message": f"Signal: {analysis.signal} — {analysis.signal_reasoning[:80]}...",
            "data": analysis.model_dump()
        })
    except Exception as e:
        yield _sse("error", {"message": f"Analyst synthesis failed: {str(e)}"})
        return

    # Agent 5: Writer — with keepalive to hold the SSE connection open
    yield _sse("agent_start", {
        "agent": "writer",
        "message": "Writing final research report..."
    })
    try:
        writer_prompt = _build_writer_prompt(fin, comps, risk, analysis)
        writer_task = asyncio.ensure_future(Runner.run(writer_agent, writer_prompt))

        while not writer_task.done():
            try:
                await asyncio.wait_for(asyncio.shield(writer_task), timeout=_KEEPALIVE_INTERVAL)
            except asyncio.TimeoutError:
                yield _keepalive()

        if writer_task.exception():
            raise writer_task.exception()

        report = writer_task.result().final_output

        # Mark the writer complete BEFORE sending pipeline_complete
        yield _sse("agent_complete", {
            "agent": "writer",
            "message": "Research report written.",
            "data": None
        })
        yield _sse("pipeline_complete", {
            "report": report.model_dump(),
            "financials": fin.model_dump(),
            "comps": comps.model_dump(),
            "risks": risk.model_dump(),
            "analysis": analysis.model_dump(),
        })
    except Exception as e:
        yield _sse("error", {"message": f"Report writing failed: {str(e)}"})


async def _collect_agent_result(agent, prompt: str):
    """Run an agent with keepalive-aware waiting. Returns the RunResult."""
    task = asyncio.ensure_future(Runner.run(agent, prompt))
    while not task.done():
        try:
            await asyncio.wait_for(asyncio.shield(task), timeout=_KEEPALIVE_INTERVAL)
        except asyncio.TimeoutError:
            pass  # keepalive not needed here — caller already yields its own events
    if task.exception():
        raise task.exception()
    return task.result()
