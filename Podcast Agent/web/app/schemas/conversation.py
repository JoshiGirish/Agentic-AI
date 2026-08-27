"""Pydantic models for the Podcast Conversation API."""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
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


class StartConversationRequest(BaseModel):
    """Request to start a new conversation."""
    topic: str = Field(..., min_length=1, max_length=500)
    role_mode: RoleMode = Field(default=RoleMode.HOST_GUEST)
    max_turns: int = Field(default=20, ge=1, le=100)


class StartConversationResponse(BaseModel):
    """Response after starting a conversation."""
    conversation_id: str
    status: str
    message: str


class Message(BaseModel):
    """A single message in the conversation."""
    agent: str
    content: str
    timestamp: str


class ConversationStatus(BaseModel):
    """Conversation status information."""
    conversation_id: str
    topic: str
    role_mode: str
    turn_count: int
    max_turns: int
    is_complete: bool
    current_speaker: Optional[str] = None
    messages: List[Message] = Field(default_factory=list)


class StopConversationResponse(BaseModel):
    """Response after stopping a conversation."""
    conversation_id: str
    status: str
    message: str


class StreamingMessage(BaseModel):
    """Message for SSE streaming."""
    agent: str
    content: str
    token_index: int
    conversation_id: str = ""


class StreamingComplete(BaseModel):
    """Complete message for SSE streaming."""
    conversation_id: str
    turn_count: int
    is_complete: bool
