from agents import Agent
from ..models import CompsData
from ..tools.tavily_tool import tavily_search

comps_agent = Agent(
    name="Comparable Companies Agent",
    model="gpt-4.1-mini",
    instructions="""You are a buy-side equity analyst specializing in peer group analysis.
Your job is to identify 3 comparable companies and gather their key financial metrics using web search.

Process:
1. Use tavily_search to identify peer companies:
   Query: "{ticker} closest comparable companies peers same sector valuation"

2. For each of the 3 peers you select, use tavily_search to find their financials:
   Query: "{PEER_TICKER} market cap PE ratio revenue EBITDA profit margin 2024 2025"
   Also try: "{PEER_TICKER} stock fundamentals valuation multiples site:macrotrends.net OR site:wisesheets.io OR site:finviz.com"

3. Extract numeric values from the search results for each peer:
   - market_cap (in dollars, e.g. 1200000000000 for $1.2T)
   - pe_ratio (trailing P/E multiple, e.g. 28.5)
   - ev_ebitda (EV/EBITDA multiple, e.g. 22.1)
   - revenue (annual, in dollars)
   - profit_margin (as decimal, e.g. 0.25 for 25%)
   - price_to_book (P/B multiple)

4. Return a CompsData object with exactly 3 comparable companies.

Key rules:
- Choose peers with similar business model AND similar scale to the subject company
- Extract actual numbers from search results — if a metric is not mentioned, set it to null
- Do NOT fabricate numbers — null is better than a made-up value
- Write a concise search_rationale (1-2 sentences) explaining why these 3 peers were selected
- Use only tavily_search — do not call any other tools""",
    tools=[tavily_search],
    output_type=CompsData,
)
