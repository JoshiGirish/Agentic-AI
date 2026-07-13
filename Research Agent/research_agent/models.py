"""Pydantic models for the Research Agent."""

from pydantic import BaseModel, Field

class ResearchAgentState(BaseModel):
    """State model for the research agent graph."""
    topic: str = Field(
        description="Topic from the user"
    )
    queries: list = Field(
        default_factory=list,
        description="list of semantically similar search queries for the topic"
    )
    scrapedData: list[str] = Field(
        default_factory=list,
        description="list of content scraped from web for each query"
    )
    summary: str = Field(
        default="",
        description="final summary of the research"
    )
    nTotalArticlesProcessed: int = Field(
        default=0,
        description="Total number of web articles processed for research"
    )