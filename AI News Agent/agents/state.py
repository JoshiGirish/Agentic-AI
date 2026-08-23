"""Agent state definitions for the AI News Multi-Agent System."""

from typing import Optional, TypedDict


class NewsAgentState(TypedDict, total=False):
    """State shared across all agents in the pipeline."""

    feed_url: Optional[str]
    feed_data: dict
    article_url: Optional[str]
    article_content: str
    summary: str
    image_url: Optional[str]
    category: str
    discord_result: str