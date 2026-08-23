"""AI News Multi-Agent System - Root package.

This package provides a modular, extensible multi-agent system for processing
news feeds and publishing to Discord.

Public API:
    - FeedParserAgent: Parses RSS/Atom feeds
    - ContentFetcherAgent: Fetches article content
    - SummarizationAgent: Generates article summaries
    - DiscordPosterAgent: Publishes to Discord via MCP

Usage:
    from agents import FeedParserAgent, create_pipeline, run_pipeline

    # Use the pipeline
    result = await run_pipeline("https://techcrunch.com/feed/")
"""

from agents import (
    FeedParserAgent,
    ContentFetcherAgent,
    SummarizationAgent,
    DiscordPosterAgent,
    create_pipeline,
    run_pipeline,
)

__all__ = [
    "FeedParserAgent",
    "ContentFetcherAgent",
    "SummarizationAgent",
    "DiscordPosterAgent",
    "create_pipeline",
    "run_pipeline",
]

__version__ = "1.0.0"