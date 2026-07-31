"""Centralized configuration for ResearchMind.

Loads environment variables once and exposes typed settings, so the rest of
the codebase never has to reach into ``os.environ`` directly.
"""

from __future__ import annotations

import os
from dotenv import load_dotenv

load_dotenv()

# ── Model ─────────────────────────────────────────────────────────────────────
# Google Generative AI (Gemini). Override via the LLM_MODEL env var.
LLM_MODEL: str = os.getenv("LLM_MODEL", "gemini-2.5-flash-lite")
LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0"))

# ── API keys ──────────────────────────────────────────────────────────────────
# langchain-google-genai reads GOOGLE_API_KEY; fall back to GEMINI_API_KEY.
GOOGLE_API_KEY: str | None = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
TAVILY_API_KEY: str | None = os.getenv("TAVILY_API_KEY")

# ── Search / scraping ─────────────────────────────────────────────────────────
SEARCH_MAX_RESULTS: int = int(os.getenv("SEARCH_MAX_RESULTS", "5"))
SEARCH_COUNTRY: str = os.getenv("SEARCH_COUNTRY", "india")
SCRAPE_TIMEOUT: int = int(os.getenv("SCRAPE_TIMEOUT", "15"))
SCRAPE_MAX_LINES: int = int(os.getenv("SCRAPE_MAX_LINES", "100"))

# Directory where per-query search results are cached.
CACHE_DIR: str = os.getenv("CACHE_DIR", ".cache")


def missing_keys() -> list[str]:
    """Return the names of required API keys that are not set."""
    missing = []
    if not GOOGLE_API_KEY:
        missing.append("GOOGLE_API_KEY (or GEMINI_API_KEY)")
    if not TAVILY_API_KEY:
        missing.append("TAVILY_API_KEY")
    return missing


def require_keys() -> None:
    """Raise a clear error if any required API key is missing."""
    missing = missing_keys()
    if missing:
        raise RuntimeError(
            "Missing required environment variable(s): "
            + ", ".join(missing)
            + ".\nSet them in a .env file or your shell environment."
        )
