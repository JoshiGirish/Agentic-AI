"""SSE Streaming service for real-time conversation updates."""

import asyncio
import json
import time
from typing import Dict, Any, Optional, AsyncGenerator
from fastapi import Request

from app.schemas.conversation import StreamingMessage, StreamingComplete


class SSEManager:
    """Manages Server-Sent Events streaming for conversations."""
    
    def __init__(self):
        self.conversation_queues: Dict[str, asyncio.Queue] = {}
        self.conversation_states: Dict[str, Dict[str, Any]] = {}
    
    async def create_queue(self, conversation_id: str) -> asyncio.Queue:
        """Create a new message queue for a conversation."""
        queue = asyncio.Queue()
        self.conversation_queues[conversation_id] = queue
        return queue
    
    async def get_queue(self, conversation_id: str) -> Optional[asyncio.Queue]:
        """Get the message queue for a conversation."""
        return self.conversation_queues.get(conversation_id)
    
    async def put_message(self, conversation_id: str, message: StreamingMessage) -> bool:
        """Put a message into the conversation's queue."""
        queue = await self.get_queue(conversation_id)
        if queue:
            await queue.put(message)
            return True
        return False
    
    async def put_complete(self, conversation_id: str, complete: StreamingComplete) -> bool:
        """Put a completion message into the conversation's queue."""
        queue = await self.get_queue(conversation_id)
        if queue:
            await queue.put(complete)
            return True
        return False
    
    async def stream_events(
        self,
        conversation_id: str,
        request: Request
    ) -> AsyncGenerator[str, None]:
        """Stream events to connected clients."""
        queue = await self.create_queue(conversation_id)
        
        try:
            while True:
                if await request.is_disconnected():
                    break
                
                try:
                    message = await asyncio.wait_for(queue.get(), timeout=1.0)
                    
                    if isinstance(message, StreamingMessage):
                        data = {
                            "agent": message.agent,
                            "content": message.content,
                            "token_index": message.token_index,
                            "conversation_id": conversation_id
                        }
                        yield f"event: message\ndata: {json.dumps(data)}\n\n"
                    elif isinstance(message, StreamingComplete):
                        data = {
                            "conversation_id": message.conversation_id,
                            "turn_count": message.turn_count,
                            "is_complete": message.is_complete
                        }
                        yield f"event: complete\ndata: {json.dumps(data)}\n\n"
                        
                except asyncio.TimeoutError:
                    yield ": heartbeat\n\n"
                    
        except asyncio.CancelledError:
            pass
        finally:
            if conversation_id in self.conversation_queues:
                del self.conversation_queues[conversation_id]
    
    def set_conversation_state(self, conversation_id: str, state: Dict[str, Any]):
        """Set the current state of a conversation."""
        self.conversation_states[conversation_id] = state
    
    def get_conversation_state(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Get the current state of a conversation."""
        return self.conversation_states.get(conversation_id)
