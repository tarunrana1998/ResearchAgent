"""CLI entry point for ResearchMind.

Usage:
    python main.py                       # prompt for a topic
    python main.py "quantum computing"   # run directly
"""

import sys

import config
from pipeline import run_research_pipeline


def main() -> None:
    missing = config.missing_keys()
    if missing:
        print("Missing required environment variable(s):", ", ".join(missing))
        print("Set them in a .env file or your shell environment before running.")
        sys.exit(1)

    topic = " ".join(sys.argv[1:]).strip() or input("\nEnter a research topic: ").strip()
    if not topic:
        print("No topic provided.")
        sys.exit(1)

    run_research_pipeline(topic)


if __name__ == "__main__":
    main()
