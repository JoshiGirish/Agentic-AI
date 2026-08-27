"""Agent Execution service for running individual agent turns."""

import asyncio
import os
import httpx
from typing import Dict, Any, Optional
from datetime import datetime

from app.schemas.conversation import RoleMode


class AgentExecutor:
    """Executes individual agent turns."""
    
    def __init__(self):
        self.agents_url = os.getenv("AGENTS_URL", "http://agents:8000")
    
    async def execute_turn(
        self,
        conversation_id: str,
        speaker: str,
        topic: str,
        role_mode: str,
        turn_count: int
    ) -> str:
        """Execute a single agent turn."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.agents_url}/api/v1/agent/turn",
                json={
                    "conversation_id": conversation_id,
                    "speaker": speaker,
                    "topic": topic,
                    "role_mode": role_mode,
                    "turn_count": turn_count
                },
                timeout=60.0
            )
            response.raise_for_status()
            return response.json()["content"]


async def execute_agent_turn(
    conversation_id: str,
    speaker: str,
    topic: str,
    role_mode: str,
    turn_count: int
) -> str:
    """Execute an agent turn and return the response."""
    executor = AgentExecutor()
    return await executor.execute_turn(
        conversation_id=conversation_id,
        speaker=speaker,
        topic=topic,
        role_mode=role_mode,
        turn_count=turn_count
    )
