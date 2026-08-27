"""Agent execution service for podcast conversations."""

import asyncio
import os
from typing import Dict, Any, Optional

from models import PodcastState, RoleMode
from _agents import PodcastAgent, HostAgent, GuestAgent, SkepticAgent, EnthusiastAgent


class AgentExecutor:
    """Executes individual agent turns."""
    
    def __init__(self):
        self.agents = {}
        self.base_url = os.getenv("LLM_URL", "http://localhost:8080/v1")
    
    def get_agent(self, role: str) -> Any:
        """Get or create an agent for the given role."""
        if role not in self.agents:
            if role == "host":
                self.agents[role] = HostAgent()
            elif role == "guest":
                self.agents[role] = GuestAgent()
            elif role == "skeptic":
                self.agents[role] = SkepticAgent()
            elif role == "enthusiast":
                self.agents[role] = EnthusiastAgent()
            else:
                raise ValueError(f"Unknown agent role: {role}")
        return self.agents[role]
    
    async def execute_turn(
        self,
        conversation_id: str,
        speaker: str,
        topic: str,
        role_mode: str,
        turn_count: int,
        messages: list = None
    ) -> str:
        """Execute a single agent turn and return the response."""
        agent = self.get_agent(speaker)
        
        conversation_history = messages or []
        
        response = await agent.generate_response(
            topic=topic,
            conversation_history=conversation_history,
            max_tokens=500
        )
        
        return response


async def execute_agent_turn(
    conversation_id: str,
    speaker: str,
    topic: str,
    role_mode: str,
    turn_count: int,
    messages: list = None
) -> str:
    """Execute an agent turn and return the response."""
    executor = AgentExecutor()
    return await executor.execute_turn(
        conversation_id=conversation_id,
        speaker=speaker,
        topic=topic,
        role_mode=role_mode,
        turn_count=turn_count,
        messages=messages
    )
