"""Prompts package for AI News Agent."""

from .summarization import SUMMARIZATION_SYSTEM_PROMPT
from .discord_poster import DISCORD_POSTER_SYSTEM_PROMPT

__all__ = [
    "SUMMARIZATION_SYSTEM_PROMPT",
    "DISCORD_POSTER_SYSTEM_PROMPT",
]