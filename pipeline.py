"""The 4-stage research pipeline: search → read → write → critique.

Exposes a single ``stream_research_pipeline`` generator so both the CLI and the
Streamlit UI share one implementation instead of duplicating the orchestration.
"""

from __future__ import annotations

from collections.abc import Iterator

import config
from agents import build_reader_agent, build_search_agent, critic_chain, writer_chain

# Ordered metadata for each pipeline stage, reused by every front-end.
STEPS = [
    {"key": "search", "num": "01", "title": "Search Agent", "desc": "Gathers recent web information"},
    {"key": "reader", "num": "02", "title": "Reader Agent", "desc": "Scrapes & extracts deep content"},
    {"key": "writer", "num": "03", "title": "Writer Chain", "desc": "Drafts the full research report"},
    {"key": "critic", "num": "04", "title": "Critic Chain", "desc": "Reviews & scores the report"},
]


def _last_message(result: dict) -> str:
    """Extract the final message content from an agent invocation result."""
    return result["messages"][-1].content


def stream_research_pipeline(topic: str) -> Iterator[tuple[str, str]]:
    """Run the pipeline, yielding ``(step_key, content)`` after each stage.

    Consumers can render progress live. Raises if required API keys are missing.
    """
    config.require_keys()

    topic = topic.strip()
    state: dict[str, str] = {}

    # ── Step 1: Search ──
    search_agent = build_search_agent()
    search_result = search_agent.invoke(
        {"messages": [("user", f"Find recent, reliable and detailed information about: {topic}")]}
    )
    state["search"] = _last_message(search_result)
    yield "search", state["search"]

    # ── Step 2: Reader ──
    reader_agent = build_reader_agent()
    reader_result = reader_agent.invoke(
        {
            "messages": [
                (
                    "user",
                    f"Based on the following search results about '{topic}', "
                    f"pick the most relevant URL and scrape it for deeper content.\n\n"
                    f"Search Results:\n{state['search'][:800]}",
                )
            ]
        }
    )
    state["reader"] = _last_message(reader_result)
    yield "reader", state["reader"]

    # ── Step 3: Writer ──
    research_combined = (
        f"SEARCH RESULTS:\n{state['search']}\n\n"
        f"DETAILED SCRAPED CONTENT:\n{state['reader']}"
    )
    state["writer"] = writer_chain.invoke({"topic": topic, "research": research_combined})
    yield "writer", state["writer"]

    # ── Step 4: Critic ──
    state["critic"] = critic_chain.invoke({"report": state["writer"]})
    yield "critic", state["critic"]


def run_research_pipeline(topic: str) -> dict:
    """Run the full pipeline and return the collected state (CLI-friendly)."""
    state: dict[str, str] = {}
    titles = {s["key"]: s["title"] for s in STEPS}
    for key, content in stream_research_pipeline(topic):
        print("\n" + "=" * 60)
        print(f"[bold cyan]{titles[key]}[/bold cyan]")
        print("=" * 60)
        print(content)
        state[key] = content
    return state


if __name__ == "__main__":
    topic = input("\nEnter a research topic: ")
    run_research_pipeline(topic)
