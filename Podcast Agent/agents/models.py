"""Pydantic models for the Podcast Agent."""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from enum import Enum


class RoleMode(str, Enum):
    """Conversation role modes."""
    HOST_GUEST = "host_guest"
    SKEPTIC_ENTHUSIAST = "skeptic_enthusiast"


class AgentRole(str, Enum):
    """Individual agent roles."""
    HOST = "host"
    GUEST = "guest"
    SKEPTIC = "skeptic"
    ENTHUSIAST = "enthusiast"


class PodcastState(BaseModel):
    """State for the podcast conversation."""
    topic: str = Field(..., description="The conversation topic")
    role_mode: str = Field(..., description="Role mode: host_guest or skeptic_enthusiast")
    messages: List[Dict[str, str]] = Field(default_factory=list, description="Conversation history")
    turn_count: int = Field(default=0, description="Number of turns completed")
    max_turns: int = Field(default=20, description="Maximum turns allowed")
    current_speaker: str = Field(default="host", description="Current speaker")
    is_complete: bool = Field(default=False, description="Whether conversation is complete")
    conversation_id: str = Field(default="", description="Unique conversation identifier")
