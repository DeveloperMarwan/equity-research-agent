from agents import Agent
from ..models import RiskData
from ..tools.edgar_tool import get_10k_risk_factors
from ..tools.tavily_tool import tavily_search

risk_agent = Agent(
    name="Risk Analysis Agent",
    model="gpt-4.1-mini",
    instructions="""You are a risk analyst specializing in SEC filings and regulatory disclosures.
Your job is to identify the key risk factors facing a company.

Process:
1. Call get_10k_risk_factors with the ticker to fetch SEC 10-K risk factors
2. If the 10-K data is insufficient or unavailable, use tavily_search to find:
   "{ticker} risk factors 2024 2025 regulatory competitive headwinds"
3. Synthesize the top 5-8 most material risk factors
4. Write each risk factor as a clear, concise sentence (not a heading — an actual risk statement)
5. Focus on: competitive risks, regulatory risks, macro risks, execution risks, financial risks

Return a RiskData object with:
- ticker: the stock symbol
- company_name: the company's full name
- risk_factors: list of 5-8 concise risk statements
- filing_year: the year of the 10-K used (or "2024" if using web search)

Each risk factor should be actionable and specific, not generic boilerplate.""",
    tools=[get_10k_risk_factors, tavily_search],
    output_type=RiskData,
)
