"""Pipeline orchestration for the AI News Multi-Agent System."""

from agents.feed_parser import FeedParserAgent
from agents.content_fetcher import ContentFetcherAgent
from agents.summarization import SummarizationAgent
from agents.discord_poster import DiscordPosterAgent

from agents.state import NewsAgentState
from langgraph.graph import StateGraph, START, END


def create_pipeline() -> StateGraph:
    """Create the complete agent pipeline using LangGraph."""

    builder = StateGraph(NewsAgentState)

    feed_parser = FeedParserAgent()
    builder.add_node("feed_parser", feed_parser.process)

    content_fetcher = ContentFetcherAgent()
    builder.add_node("content_fetcher", content_fetcher.process)

    summarizer = SummarizationAgent()
    builder.add_node("summarizer", summarizer.process)

    poster = DiscordPosterAgent()
    builder.add_node("poster", poster.process)

    builder.add_edge(START, "feed_parser")
    builder.add_edge("feed_parser", "content_fetcher")
    builder.add_edge("content_fetcher", "summarizer")
    builder.add_edge("summarizer", "poster")
    builder.add_edge("poster", END)

    graph = builder.compile()

    return graph


async def run_pipeline(feed_url: str, category: str = "General") -> dict:
    """Run the complete pipeline for a single feed item."""
    graph = create_pipeline()

    state = NewsAgentState()
    state["feed_url"] = feed_url
    state["category"] = category

    result = await graph.ainvoke(state)

    return result


async def main():
    import json

    test_feed = "https://techcrunch.com/feed/"

    print("Running AI News Multi-Agent Pipeline...\n")
    print(f"Processing feed: {test_feed}\n")

    result = await run_pipeline(test_feed, category="Technology")

    print("\n" + "=" * 60)
    print("Pipeline Results:")
    print("=" * 60)

    if result.get("feed_data"):
        print(f"Title: {result['feed_data'].get('title', 'N/A')}")
        print(f"Link: {result['feed_data'].get('link', 'N/A')}")
        print(f"Category: {result['feed_data'].get('category', 'N/A')}")
        print(f"Image: {result['feed_data'].get('image', 'N/A')}")

    if result.get("summary"):
        print(f"\nSummary:\n{result['summary'][:500]}...")

    print("\n" + "=" * 60)