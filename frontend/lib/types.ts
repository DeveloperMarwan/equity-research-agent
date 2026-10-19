export type Signal = "BUY" | "HOLD" | "SELL";

export interface FinancialData {
  ticker: string;
  company_name: string;
  sector: string;
  industry: string;
  current_price: number;
  market_cap: number | null;
  pe_ratio: number | null;
  forward_pe: number | null;
  revenue: number | null;
  ebitda: number | null;
  eps: number | null;
  week_52_high: number;
  week_52_low: number;
  beta: number | null;
  dividend_yield: number | null;
  price_to_book: number | null;
  debt_to_equity: number | null;
  return_on_equity: number | null;
  profit_margin: number | null;
  analyst_target_price: number | null;
}

export interface CompanyMetric {
  ticker: string;
  name: string;
  market_cap: number | null;
  pe_ratio: number | null;
  ev_ebitda: number | null;
  revenue: number | null;
  profit_margin: number | null;
  price_to_book: number | null;
}

export interface CompsData {
  subject_ticker: string;
  comparable_companies: CompanyMetric[];
  search_rationale: string;
}

export interface RiskData {
  ticker: string;
  company_name: string;
  risk_factors: string[];
  filing_year: string;
}

export interface AnalystOutput {
  signal: Signal;
  signal_reasoning: string;
  valuation_summary: string;
  relative_valuation: string;
  key_strengths: string[];
  key_risks: string[];
  price_target_rationale: string;
}

export interface FinalReport {
  ticker: string;
  company_name: string;
  company_overview: string;
  financials_summary: string;
  comps_analysis: string;
  risk_summary: string;
  recommendation: string;
  signal: Signal;
  signal_reasoning: string;
  key_strengths: string[];
  key_risks: string[];
  executive_summary: string;
}

export type AgentName = "financial_data" | "comps" | "risk" | "analyst" | "writer";

export interface AgentEvent {
  agent: AgentName;
  message: string;
  status: "running" | "complete" | "error";
  data?: FinancialData | CompsData | RiskData | AnalystOutput | null;
  timestamp: number;
}

export interface PipelineResult {
  report: FinalReport;
  financials: FinancialData;
  comps: CompsData;
  risks: RiskData;
  analysis: AnalystOutput;
}
