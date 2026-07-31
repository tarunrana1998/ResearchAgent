"""Agent tools: web search (Tavily) and URL scraping (requests + BeautifulSoup)."""

from __future__ import annotations

import hashlib
import json
import os

import requests
from bs4 import BeautifulSoup
from langchain.tools import tool
from rich import print
from tavily import TavilyClient

import config

tavily_client = TavilyClient(config.TAVILY_API_KEY)


def _cache_path(query: str) -> str:
    """Return a per-query cache file path.

    The previous implementation cached every search to a single file, so the
    first query's results were served for *every* subsequent topic. Keying the
    cache by a hash of the query fixes that.
    """
    key = hashlib.sha256(query.strip().lower().encode("utf-8")).hexdigest()[:16]
    return os.path.join(config.CACHE_DIR, f"search_{key}.json")


@tool
def web_search(query: str) -> str:
    """Search the web with the Tavily API for recent, reliable information.

    Args:
        query: The search query.
    Returns:
        Formatted title / URL / content blocks for the top results.
    """
    cache_file = _cache_path(query)

    if os.path.exists(cache_file):
        print(f"[dim]Using cached web results for query hash → {cache_file}[/dim]")
        with open(cache_file, "r", encoding="utf-8") as f:
            web_results = json.load(f)
    else:
        print(f"[cyan]Searching Tavily for:[/cyan] {query}")
        web_results = tavily_client.search(
            query=query,
            max_results=config.SEARCH_MAX_RESULTS,
            # country=config.SEARCH_COUNTRY,
            include_images=True,
        )
        os.makedirs(config.CACHE_DIR, exist_ok=True)
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(web_results, f, indent=4, ensure_ascii=False)

    output = []
    for r in web_results.get("results", []):
        output.append(
            f"Title: {r.get('title', '')}\n"
            f"URL: {r.get('url', '')}\n"
            f"Content: {r.get('content', '')}\n"
        )
        output.append("-" * 50)

    return "\n".join(output) if output else "No results found."


@tool
def scrape_url(url: str) -> str:
    """Fetch a URL and return its cleaned main text content.

    Args:
        url: The URL to fetch.
    Returns:
        The extracted text (truncated), or an error message on failure.
    """
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
        )
    }
    try:
        response = requests.get(url, headers=headers, timeout=config.SCRAPE_TIMEOUT)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"Error fetching URL: {e}"

    soup = BeautifulSoup(response.text, "html.parser")

    # Remove non-content tags before extracting text.
    for unwanted in ("script", "style", "header", "footer", "nav", "form", "iframe"):
        for tag in soup.find_all(unwanted):
            tag.decompose()

    text = soup.get_text(separator="\n", strip=True)
    lines = [ln for ln in text.split("\n") if ln.strip()]
    return "\n".join(lines[: config.SCRAPE_MAX_LINES])
