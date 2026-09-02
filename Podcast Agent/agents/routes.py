"""API routes for the Agent service."""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from typing import Dict, Any, AsyncGenerator
from uuid import uuid4
import json
import os
import re
import asyncio
from datetime import datetime

from langchain_openai import ChatOpenAI
from pydantic import SecretStr
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from models import PodcastState
from execution import execute_agent_turn

router = APIRouter(prefix="/api/v1", tags=["agent"])


@router.post("/conversation")
async def create_conversation(request: Dict[str, Any]):
    """Create a new podcast conversation."""
    conversation_id = str(uuid4())
    topic = request.get("topic", "")
    role_mode = request.get("role_mode", "host_guest")
    max_turns = request.get("max_turns", 20)
    
    state_dir = os.path.expanduser("~/.agentic-ai/state")
    os.makedirs(state_dir, exist_ok=True)
    
    state_file = os.path.join(state_dir, f"{conversation_id}.json")
    
    initial_state = {
        "conversation_id": conversation_id,
        "topic": topic,
        "role_mode": role_mode,
        "max_turns": max_turns,
        "turn_count": 0,
        "is_complete": False,
        "messages": [],
        "current_speaker": "host"
    }
    
    with open(state_file, "w") as f:
        json.dump(initial_state, f)
    
    return {
        "conversation_id": conversation_id,
        "topic": topic,
        "role_mode": role_mode,
        "max_turns": max_turns
    }


@router.get("/conversation/{conversation_id}")
async def get_conversation(conversation_id: str):
    """Get conversation state."""
    state_dir = os.path.expanduser("~/.agentic-ai/state")
    state_file = os.path.join(state_dir, f"{conversation_id}.json")
    
    try:
        with open(state_file, "r") as f:
            state = json.load(f)
        return state
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Conversation not found")


@router.delete("/conversation/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """Delete conversation and stop streaming."""
    state_dir = os.path.expanduser("~/.agentic-ai/state")
    state_file = os.path.join(state_dir, f"{conversation_id}.json")
    
    try:
        os.remove(state_file)
    except FileNotFoundError:
        pass
    
    return {"message": "Conversation deleted"}


@router.get("/stream/{conversation_id}")
async def stream_conversation(conversation_id: str):
    """Stream conversation updates via Server-Sent Events with token-level streaming."""
    state_dir = os.path.expanduser("~/.agentic-ai/state")
    state_file = os.path.join(state_dir, f"{conversation_id}.json")
    
    try:
        with open(state_file, "r") as f:
            state = json.load(f)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    async def event_generator():
        # Process conversation turns until complete
        while not state.get("is_complete", False) and state.get("turn_count", 0) < state.get("max_turns", 20):
            # Determine next speaker
            role_mode = state.get("role_mode", "host_guest")
            current_speaker = state.get("current_speaker", "host")
            
            if role_mode == "host_guest":
                next_speaker = "guest" if current_speaker == "host" else "host"
            else:  # skeptic_enthusiast
                next_speaker = "enthusiast" if current_speaker == "skeptic" else "skeptic"
            
            # Build system prompt for the agent
            system_prompt = ""
            if next_speaker == "host":
                system_prompt = f"""You are the HOST of a podcast discussing: {state['topic']}

Your role:
- Guide the conversation and keep it engaging
- Ask insightful questions
- Encourage the guest to share their expertise
- Summarize key points periodically
- Maintain a friendly, professional tone

Speak concisely and keep the conversation flowing. 
Your responses should be natural and conversational."""
            elif next_speaker == "guest":
                system_prompt = f"""You are the GUEST on a podcast discussing: {state['topic']}

Your role:
- Share your expertise on the topic
- Answer the host's questions thoughtfully
- Provide examples and insights
- Keep explanations clear and accessible
- Maintain an engaging, knowledgeable tone

Speak with authority but remain approachable. 
Your responses should be informative and engaging."""
            elif next_speaker == "skeptic":
                system_prompt = f"""You are the SKEPTIC in a debate about: {state['topic']}

Your role:
- Question assumptions and claims
- Ask for evidence and reasoning
- Explore counterarguments
- Challenge ideas constructively
- Maintain a critical but fair tone

Your responses should be analytical and probing, 
helping to deepen the discussion by examining ideas critically."""
            elif next_speaker == "enthusiast":
                system_prompt = f"""You are the ENTHUSIAST in a debate about: {state['topic']}

Your role:
- Support and defend ideas
- Explain benefits and advantages
- Provide examples and enthusiasm
- Build on others' points
- Maintain an energetic, positive tone

Your responses should be passionate and supportive, 
helping to highlight the value and potential of the ideas being discussed."""
            
            system_prompt += """

IMPORTANT OUTPUT RULES:
- Reply with ONLY your own spoken lines, in character as your podcast role.
- Start directly with your words. NEVER prefix your reply with a label such as "host:", "guest:", "skeptic:", or "enthusiast:".
- NEVER quote, copy, or repeat a previous speaker's message.
- Keep your reply natural and conversational."""

            # Build messages for the LLM
            messages = [SystemMessage(content=system_prompt)]

            for msg in state.get("messages", [])[-6:]:
                if msg.get("agent") == next_speaker:
                    messages.append(AIMessage(content=msg.get("content", "")))
                else:
                    messages.append(HumanMessage(content=f"{msg.get('agent', 'user')}: {msg.get('content', '')}"))
            
            # Create LLM client for streaming
            llm = ChatOpenAI(
                model="gemma-4-E4b-it.Q4_K_M.gguf",
                base_url=os.getenv("LLM_URL", "http://localhost:8080/v1"),
                api_key=SecretStr("dummy-key"),
                temperature=0.7,
                streaming=True
            )
            
            # Stream the response token by token
            full_response = ""
            try:
                async for chunk in llm.astream(messages):
                    if chunk.content:
                        full_response += chunk.content
                        # Send token event
                        yield f"event: token\ndata: {json.dumps({'agent': next_speaker, 'token': chunk.content})}\n\n"
                
                # Defensive cleanup: strip speaker labels/headers the model may have copied
                cleaned = full_response.strip()
                label_re = re.compile(r"^(?:%s)\s*(?::|response)[\s:-]*" % re.escape(next_speaker), re.IGNORECASE)
                divider_re = re.compile(r"^\s*[-=#>*\s]{2,}\s*", re.DOTALL)
                cleaned = divider_re.sub("", cleaned).strip()
                while True:
                    before = cleaned
                    cleaned = label_re.sub("", cleaned).strip()
                    cleaned = divider_re.sub("", cleaned).strip()
                    if cleaned == before:
                        break
                full_response = cleaned
                
                # Add the complete response to messages
                if "messages" not in state:
                    state["messages"] = []
                
                message_obj = {
                    "agent": next_speaker,
                    "content": full_response,
                    "timestamp": datetime.now().isoformat()
                }
                state["messages"].append(message_obj)
                
                # Update state
                state["turn_count"] = state.get("turn_count", 0) + 1
                state["current_speaker"] = next_speaker
                
                # Check if complete
                if state["turn_count"] >= state.get("max_turns", 20):
                    state["is_complete"] = True
                
                # Save updated state to file
                with open(state_file, "w") as f:
                    json.dump(state, f, indent=2)
                
                # Send message complete event
                yield f"event: message\ndata: {json.dumps(message_obj)}\n\n"
                
                # Send update event for turn counter
                update_json = json.dumps({
                    "turn_count": state["turn_count"], 
                    "max_turns": state.get("max_turns", 20), 
                    "is_complete": state.get("is_complete", False)
                })
                yield f"event: update\ndata: {update_json}\n\n"
                
                # Wait briefly before next turn to simulate thinking time
                await asyncio.sleep(1.0)
                
            except Exception as e:
                # If there's an error, yield an error event and break
                error_json = json.dumps({"error": str(e)})
                yield f"event: error\ndata: {error_json}\n\n"
                break
        
        # Send final state when complete
        final_json = json.dumps({
            "turn_count": state.get("turn_count", 0), 
            "max_turns": state.get("max_turns", 20), 
            "is_complete": state.get("is_complete", False)
        })
        yield f"event: complete\ndata: {final_json}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache"}
    )