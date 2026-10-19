"""
Fetches stock data directly from Yahoo Finance's v7 quote API.

Yahoo Finance's v10/quoteSummary endpoint requires a crumb cookie that is
aggressively rate-limited. The v7/quote endpoint returns the same core
market data without crumb authentication and is far more reliable.
"""
import json
import time
import random
import threading
import requests
from agents import function_tool

_call_lock = threading.Lock()
_last_call: float = 0.0
_MIN_INTERVAL = 1.5  # seconds between calls

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://finance.yahoo.com/",
}


def _rate_limit() -> None:
    global _last_call
    with _call_lock:
        gap = time.time() - _last_call
        if gap < _MIN_INTERVAL:
            time.sleep(_MIN_INTERVAL - gap)
        _last_call = time.time()


def _v7_quote(ticker: str) -> dict:
    """Fetch quote data from Yahoo Finance v7 API (no crumb required)."""
    _rate_limit()
    session = requests.Session()
    session.headers.update(_HEADERS)

    url = "https://query1.finance.yahoo.com/v7/finance/quote"
    resp = session.get(url, params={"symbols": ticker.upper()}, timeout=15)
    resp.raise_for_status()

    results = resp.json().get("quoteResponse", {}).get("result", [])
    if not results:
        raise ValueError(f"No quote data returned for {ticker}")
    return results[0]


def _v8_fundamentals(ticker: str, session: requests.Session) -> dict:
    """
    Fetch income/valuation data from Yahoo Finance v8 chart endpoint.
    Returns a subset of financial fundamentals embedded in the chart response.
    """
    _rate_limit()
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker.upper()}"
    params = {
        "interval": "1d",
        "range": "1d",
        "includePrePost": "false",
        "modules": "summaryDetail,defaultKeyStatistics,financialData,assetProfile",
    }
    resp = session.get(url, params=params, timeout=15)
    resp.raise_for_status()
    meta = resp.json().get("chart", {}).get("result", [{}])[0].get("meta", {})
    return meta


def _fetch_stock_data(ticker: str, max_attempts: int = 3) -> dict:
    last_err = None
    for attempt in range(max_attempts):
        try:
            quote = _v7_quote(ticker)
            return quote
        except Exception as e:
            last_err = e
            is_rate_limit = "429" in str(e) or "Too Many" in str(e)
            if attempt < max_attempts - 1:
                wait = (8 * (attempt + 1) + random.uniform(0, 2)) if is_rate_limit else 2.0
                time.sleep(wait)

    raise RuntimeError(f"All attempts failed for {ticker}: {last_err}")


@function_tool
def get_stock_financials(ticker: str) -> str:
    """Fetch current financial data for a stock ticker from Yahoo Finance."""
    try:
        q = _fetch_stock_data(ticker.upper())

        def sf(key, fallback=None):
            val = q.get(key)
            if val is None:
                return fallback
            try:
                return float(val)
            except (TypeError, ValueError):
                return fallback

        data = {
            "ticker": q.get("symbol", ticker.upper()),
            "company_name": q.get("longName") or q.get("shortName", ticker.upper()),
            "sector": q.get("sector", "Unknown"),
            "industry": q.get("industry", "Unknown"),
            "current_price": sf("regularMarketPrice"),
            "market_cap": sf("marketCap"),
            "pe_ratio": sf("trailingPE"),
            "forward_pe": sf("forwardPE"),
            "revenue": sf("totalRevenue"),
            "ebitda": sf("ebitda"),
            "eps": sf("epsTrailingTwelveMonths"),
            "week_52_high": sf("fiftyTwoWeekHigh"),
            "week_52_low": sf("fiftyTwoWeekLow"),
            "beta": sf("beta"),
            "dividend_yield": sf("dividendYield"),
            "price_to_book": sf("priceToBook"),
            "debt_to_equity": sf("debtToEquity"),
            "return_on_equity": sf("returnOnEquity"),
            "profit_margin": sf("profitMargins"),
            "analyst_target_price": sf("targetMeanPrice"),
            "enterprise_value": sf("enterpriseValue"),
            "ev_ebitda": sf("enterpriseToEbitda"),
            "ev_revenue": sf("enterpriseToRevenue"),
            "free_cashflow": sf("freeCashflow"),
            "operating_cashflow": sf("operatingCashflow"),
            "gross_margins": sf("grossMargins"),
            "operating_margins": sf("operatingMargins"),
            "shares_outstanding": sf("sharesOutstanding"),
            "analyst_recommendation": q.get("recommendationKey", "N/A"),
            "number_of_analysts": q.get("numberOfAnalystOpinions"),
            # v7-specific fields that map to our model
            "book_value": sf("bookValue"),
            "regular_market_volume": sf("regularMarketVolume"),
            "average_volume": sf("averageVolume"),
            "fifty_day_average": sf("fiftyDayAverage"),
            "two_hundred_day_average": sf("twoHundredDayAverage"),
        }

        return json.dumps(data, default=str)

    except Exception as e:
        return json.dumps({
            "error": f"Failed to fetch data for {ticker}: {str(e)}",
            "ticker": ticker.upper(),
        })
