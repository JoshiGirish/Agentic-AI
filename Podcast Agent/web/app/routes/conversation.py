"""API routes for the Podcast Conversation API."""

from fastapi import APIRouter, HTTPException, Request, Response
from fastapi.responses import StreamingResponse
from typing import Dict, Any, AsyncGenerator
import asyncio
import json

from app.schemas.conversation import (
    StartConversationRequest,
    StartConversationResponse,
    StopConversationResponse,
    StreamingMessage,
    StreamingComplete
)

router = APIRouter(prefix="/api/v1", tags=["conversation"])

conversations: Dict[str, Any] = {}


@router.post("/conversation", response_model=StartConversationResponse)
async def start_conversation(request: StartConversationRequest):
    """Start a new podcast conversation."""
    from app.services.agent_orchestrator import AgentOrchestrator
    
    orchestrator = AgentOrchestrator()
    conversation_id = await orchestrator.create_conversation(
        topic=request.topic,
        role_mode=request.role_mode.value,
        max_turns=request.max_turns
    )
    
    return StartConversationResponse(
        conversation_id=conversation_id,
        status="started",
        message="Conversation initialized"
    )


@router.get("/stream/{conversation_id}")
async def stream_conversation(
    conversation_id: str,
    request: Request
) -> StreamingResponse:
    """Stream conversation events via Server-Sent Events (SSE)."""
    from app.services.streaming import SSEManager
    
    sse_manager = SSEManager()
    
    async def event_generator() -> AsyncGenerator[str, None]:
        """Generate SSE events for the conversation."""
        async for event in sse_manager.stream_events(conversation_id, request):
            yield event
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*"
        }
    )


@router.get("/conversation/{conversation_id}")
async def get_conversation(conversation_id: str):
    """Get conversation status and history."""
    from app.services.agent_orchestrator import AgentOrchestrator
    
    orchestrator = AgentOrchestrator()
    status = await orchestrator.get_conversation_status(conversation_id)
    
    if status is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return status


@router.delete("/conversation/{conversation_id}", response_model=StopConversationResponse)
async def stop_conversation(conversation_id: str):
    """Stop an ongoing conversation."""
    from app.services.agent_orchestrator import AgentOrchestrator
    
    orchestrator = AgentOrchestrator()
    result = await orchestrator.stop_conversation(conversation_id)
    
    if not result:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return StopConversationResponse(
        conversation_id=conversation_id,
        status="stopped",
        message="Conversation stopped successfully"
    )
