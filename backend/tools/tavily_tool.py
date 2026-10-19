import os
import json
import requests
from agents import function_tool


@function_tool
def tavily_search(query: str, max_results: int = 5) -> str:
    """Search the web for financial news, peer companies, and market context using Tavily."""
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        return "Error: TAVILY_API_KEY is not set."

    url = "https://api.tavily.com/search"
    headers = {"Content-Type": "application/json"}
    payload = {
        "api_key": api_key,
        "query": query,
        "max_results": max_results,
        "search_depth": "basic",
        "include_answer": True,
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        response.raise_for_status()
        data = response.json()

        results = data.get("results", [])
        answer = data.get("answer", "")

        output_parts = []
        if answer:
            output_parts.append(f"Summary: {answer}\n")

        for r in results:
            title = r.get("title", "Untitled")
            content = r.get("content", "")
            url_str = r.get("url", "")
            output_parts.append(f"- {title} ({url_str})\n  {content[:400]}")

        return "\n".join(output_parts) if output_parts else "No results found."

    except requests.exceptions.RequestException as e:
        return f"Tavily API error: {str(e)}"
