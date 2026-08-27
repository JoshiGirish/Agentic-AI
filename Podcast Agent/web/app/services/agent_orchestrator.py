"""Agent Orchestrator service for managing podcast conversations."""

import asyncio
import uuid
from typing import Dict, Any, Optional
from datetime import datetime

from app.schemas.conversation import (
    StartConversationResponse,
    ConversationStatus,
    StopConversationResponse,
    StreamingMessage,
    StreamingComplete,
    RoleMode
)


class AgentOrchestrator:
    """Orchestrates podcast conversations between two agents."""
    
    def __init__(self):
        self.conversations: Dict[str, Dict[str, Any]] = {}
        self.running: Dict[str, asyncio.Task] = {}
    
    async def create_conversation(
        self,
        topic: str,
        role_mode: str,
        max_turns: int
    ) -> str:
        """Create a new conversation."""
        conversation_id = str(uuid.uuid4())[:8]
        
        self.conversations[conversation_id] = {
            "topic": topic,
            "role_mode": role_mode,
            "max_turns": max_turns,
            "turn_count": 0,
            "is_complete": False,
            "current_speaker": "host",
            "messages": [],
            "start_time": datetime.now().isoformat()
        }
        
        self.running[conversation_id] = asyncio.create_task(
            self._run_conversation(conversation_id)
        )
        
        return conversation_id
    
    async def get_conversation_status(self, conversation_id: str) -> Optional[ConversationStatus]:
        """Get the status of a conversation."""
        conv = self.conversations.get(conversation_id)
        if not conv:
            return None
        
        return ConversationStatus(
            conversation_id=conversation_id,
            topic=conv["topic"],
            role_mode=conv["role_mode"],
            turn_count=conv["turn_count"],
            max_turns=conv["max_turns"],
            is_complete=conv["is_complete"],
            current_speaker=conv.get("current_speaker"),
            messages=conv["messages"]
        )
    
    async def stop_conversation(self, conversation_id: str) -> bool:
        """Stop an ongoing conversation."""
        if conversation_id not in self.conversations:
            return False
        
        self.conversations[conversation_id]["is_complete"] = True
        
        if conversation_id in self.running:
            self.running[conversation_id].cancel()
            del self.running[conversation_id]
        
        return True
    
    async def _run_conversation(self, conversation_id: str):
        """Run the conversation between agents."""
        from app.services.agent_execution import execute_agent_turn
        
        conv = self.conversations[conversation_id]
        
        while not conv["is_complete"] and conv["turn_count"] < conv["max_turns"]:
            current_speaker = conv["current_speaker"]
            
            try:
                response = await execute_agent_turn(
                    conversation_id=conversation_id,
                    speaker=current_speaker,
                    topic=conv["topic"],
                    role_mode=conv["role_mode"],
                    turn_count=conv["turn_count"]
                )
                
                conv["messages"].append({
                    "agent": current_speaker,
                    "content": response,
                    "timestamp": datetime.now().isoformat()
                })
                
                conv["turn_count"] += 1
                
                if current_speaker == "host":
                    conv["current_speaker"] = "guest"
                else:
                    conv["current_speaker"] = "host"
                
                await asyncio.sleep(0.5)
                
            except Exception as e:
                print(f"Error in conversation {conversation_id}: {e}")
                conv["is_complete"] = True
                break
        
        conv["is_complete"] = True
