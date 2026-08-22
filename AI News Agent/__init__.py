"""AI News Multi-Agent System Package."""

from .agents import (
    NewsAgentState,
    FeedParserAgent,
    ContentFetcherAgent,
    SummarizationAgent,
    DiscordPosterAgent,
    create_pipeline,
    run_pipeline,
)

from .orchestrator import (
    AINewsOrchestrator,
    FeedsManager,
)

from .llm_utils import (
    LLMClient,
    SUMMARY_TEMPLATES,
)

__version__ = "1.0.0"
__all__ = [
    "NewsAgentState",
    "FeedParserAgent",
    "ContentFetcherAgent",
    "SummarizationAgent",
    "DiscordPosterAgent",
    "create_pipeline",
    "run_pipeline",
    "AINewsOrchestrator",
    "FeedsManager",
    "LLMClient",
    "SUMMARY_TEMPLATES",
]