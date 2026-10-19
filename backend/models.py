from typing import List, Literal, Optional
from pydantic import BaseModel


class FinancialData(BaseModel):
    ticker: str
    company_name: str
    sector: str
    industry: str
    current_price: Optional[float]
    market_cap: Optional[float]
    pe_ratio: Optional[float]
    forward_pe: Optional[float]
    revenue: Optional[float]
    ebitda: Optional[float]
    eps: Optional[float]
    week_52_high: Optional[float]
    week_52_low: Optional[float]
    beta: Optional[float]
    dividend_yield: Optional[float]
    price_to_book: Optional[float]
    debt_to_equity: Optional[float]
    return_on_equity: Optional[float]
    profit_margin: Optional[float]
    analyst_target_price: Optional[float]


class CompanyMetric(BaseModel):
    ticker: str
    name: str
    market_cap: Optional[float]
    pe_ratio: Optional[float]
    ev_ebitda: Optional[float]
    revenue: Optional[float]
    profit_margin: Optional[float]
    price_to_book: Optional[float]


class CompsData(BaseModel):
    subject_ticker: str
    comparable_companies: List[CompanyMetric]
    search_rationale: str


class RiskData(BaseModel):
    ticker: str
    company_name: str
    risk_factors: List[str]
    filing_year: str


class AnalystOutput(BaseModel):
    signal: Literal["BUY", "HOLD", "SELL"]
    signal_reasoning: str
    valuation_summary: str
    relative_valuation: str
    key_strengths: List[str]
    key_risks: List[str]
    price_target_rationale: str


class FinalReport(BaseModel):
    ticker: str
    company_name: str
    company_overview: str
    financials_summary: str
    comps_analysis: str
    risk_summary: str
    recommendation: str
    signal: Literal["BUY", "HOLD", "SELL"]
    signal_reasoning: str
    key_strengths: List[str]
    key_risks: List[str]
    executive_summary: str
