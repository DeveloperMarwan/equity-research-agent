import json
import os
from agents import function_tool


@function_tool
def get_10k_risk_factors(ticker: str) -> str:
    """Fetch risk factors from the latest 10-K SEC filing using edgartools."""
    identity = os.getenv("EDGAR_IDENTITY")
    if not identity:
        return json.dumps({
            "ticker": ticker.upper(),
            "error": "EDGAR_IDENTITY is not set (the SEC requires a contact identity). Use web search instead.",
            "risk_factors": [],
            "filing_year": "N/A"
        })

    try:
        import edgar
        edgar.set_identity(identity)

        company = edgar.Company(ticker.upper())
        filings = company.get_filings(form="10-K")

        if not filings or len(filings) == 0:
            return json.dumps({
                "ticker": ticker.upper(),
                "error": "No 10-K filings found. Company may not file with SEC (e.g., foreign-listed).",
                "risk_factors": [],
                "filing_year": "N/A"
            })

        latest_10k = filings[0]
        filing_year = str(latest_10k.filing_date)[:4] if hasattr(latest_10k, "filing_date") else "Unknown"

        try:
            doc = latest_10k.obj()
            risk_text = ""

            if hasattr(doc, "risk_factors") and doc.risk_factors:
                risk_text = str(doc.risk_factors)
            elif hasattr(doc, "item_1a") and doc.item_1a:
                risk_text = str(doc.item_1a)

            if not risk_text:
                return json.dumps({
                    "ticker": ticker.upper(),
                    "risk_factors": ["Risk factors text could not be extracted from this filing."],
                    "filing_year": filing_year,
                    "note": "Manual review recommended."
                })

            # Extract individual risk factor headings/sentences
            lines = [line.strip() for line in risk_text.split("\n") if line.strip()]
            # Filter to meaningful lines (skip very short or very long boilerplate)
            risk_items = [l for l in lines if 20 < len(l) < 500][:10]

            return json.dumps({
                "ticker": ticker.upper(),
                "filing_year": filing_year,
                "risk_factors": risk_items if risk_items else [risk_text[:2000]],
            })

        except Exception as parse_err:
            return json.dumps({
                "ticker": ticker.upper(),
                "filing_year": filing_year,
                "risk_factors": [f"Could not parse 10-K document: {str(parse_err)}"],
            })

    except ImportError:
        return json.dumps({
            "ticker": ticker.upper(),
            "error": "edgartools not installed.",
            "risk_factors": [],
            "filing_year": "N/A"
        })
    except Exception as e:
        return json.dumps({
            "ticker": ticker.upper(),
            "error": f"Edgar lookup failed: {str(e)}",
            "risk_factors": [
                "Unable to retrieve SEC filings at this time.",
                "Common risks include: market competition, regulatory changes, macroeconomic conditions.",
            ],
            "filing_year": "N/A"
        })
