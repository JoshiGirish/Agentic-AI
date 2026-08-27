"""Agent orchestrator for LangGraph-based podcast conversations."""

from langgraph.graph import StateGraph, START, END
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime


class PodcastState(BaseModel):
    """State for the podcast conversation."""
    topic: str = Field(..., description="The conversation topic")
    role_mode: str = Field(..., description="Role mode: host_guest or skeptic_enthusiast")
    messages: List[Dict[str, str]] = Field(default_factory=list, description="Conversation history")
    turn_count: int = Field(default=0, description="Number of turns completed")
    max_turns: int = Field(default=20, description="Maximum turns allowed")
    current_speaker: str = Field(default="host", description="Current speaker: host, guest, skeptic, or enthusiast")
    is_complete: bool = Field(default=False, description="Whether conversation is complete")


class PodcastAgentOrchestrator:
    """Orchestrates podcast conversations using LangGraph."""
    
    def __init__(self):
        self.graphs: Dict[str, Any] = {}
    
    def create_graph(self, role_mode: str) -> StateGraph:
        """Create a LangGraph for the podcast conversation."""
        builder = StateGraph(PodcastState)
        
        if role_mode == "host_guest":
            builder.add_node("host", self._host_agent)
            builder.add_node("guest", self._guest_agent)
        else:
            builder.add_node("skeptic", self._skeptic_agent)
            builder.add_node("enthusiast", self._enthusiast_agent)
        
        builder.add_edge(START, "host" if role_mode == "host_guest" else "skeptic")
        
        if role_mode == "host_guest":
            builder.add_conditional_edges(
                "host",
                lambda state: "guest" if state.turn_count < state.max_turns else END,
                {"guest": "guest", "end": END}
            )
            builder.add_conditional_edges(
                "guest",
                lambda state: "host" if state.turn_count < state.max_turns else END,
                {"host": "host", "end": END}
            )
        else:
            builder.add_conditional_edges(
                "skeptic",
                lambda state: "enthusiast" if state.turn_count < state.max_turns else END,
                {"enthusiast": "enthusiast", "end": END}
            )
            builder.add_conditional_edges(
                "enthusiast",
                lambda state: "skeptic" if state.turn_count < state.max_turns else END,
                {"skeptic": "skeptic", "end": END}
            )
        
        builder.add_edge("host" if role_mode == "host_guest" else "skeptic", END)
        
        return builder.compile()
    
    async def _host_agent(self, state: PodcastState) -> dict:
        """Host agent - guides conversation, asks questions."""
        return await self._generate_agent_response(
            state=state,
            agent_role="host",
            system_prompt=self._get_host_prompt(state.topic)
        )
    
    async def _guest_agent(self, state: PodcastState) -> dict:
        """Guest agent - provides expertise, answers questions."""
        return await self._generate_agent_response(
            state=state,
            agent_role="guest",
            system_prompt=self._get_guest_prompt(state.topic)
        )
    
    async def _skeptic_agent(self, state: PodcastState) -> dict:
        """Skeptic agent - questions claims, seeks evidence."""
        return await self._generate_agent_response(
            state=state,
            agent_role="skeptic",
            system_prompt=self._get_skeptic_prompt(state.topic)
        )
    
    async def _enthusiast_agent(self, state: PodcastState) -> dict:
        """Enthusiast agent - supports ideas, explains benefits."""
        return await self._generate_agent_response(
            state=state,
            agent_role="enthusiast",
            system_prompt=self._get_enthusiast_prompt(state.topic)
        )
    
    async def _generate_agent_response(
        self,
        state: PodcastState,
        agent_role: str,
        system_prompt: str
    ) -> dict:
        """Generate an agent response using LLM."""
        from langchain_openai import ChatOpenAI
        from pydantic import SecretStr
        from langchain_core.messages import SystemMessage, HumanMessage
        
        llm = ChatOpenAI(
            model="gemma-4-E4b-it.Q4_K_M.gguf",
            base_url="http://localhost:8080/v1",
            api_key=SecretStr("dummy-key"),
            temperature=0.7,
            streaming=True
        )
        
        messages = [SystemMessage(content=system_prompt)]
        
        for msg in state.messages[-5:]:
            role = "user" if msg["agent"] != agent_role else "assistant"
            messages.append(HumanMessage(content=f"{msg['agent']}: {msg['content']}"))
        
        response = await llm.ainvoke(messages)
        
        return {
            "messages": state.messages + [{"agent": agent_role, "content": response.content}],
            "turn_count": state.turn_count + 1
        }
    
    def _get_host_prompt(self, topic: str) -> str:
        """Get system prompt for host agent."""
        return f"""You are the HOST of a podcast discussing: {topic}

Your role:
- Guide the conversation and keep it engaging
- Ask insightful questions
- Encourage the guest to share their expertise
- Summarize key points periodically
- Maintain a friendly, professional tone

Speak concisely and keep the conversation flowing. 
Your responses should be natural and conversational."""

    def _get_guest_prompt(self, topic: str) -> str:
        """Get system prompt for guest agent."""
        return f"""You are the GUEST on a podcast discussing: {topic}

Your role:
- Share your expertise on the topic
- Answer the host's questions thoughtfully
- Provide examples and insights
- Keep explanations clear and accessible
- Maintain an engaging, knowledgeable tone

Speak with authority but remain approachable. 
Your responses should be informative and engaging."""

    def _get_skeptic_prompt(self, topic: str) -> str:
        """Get system prompt for skeptic agent."""
        return f"""You are the SKEPTIC in a debate about: {topic}

Your role:
- Question assumptions and claims
- Ask for evidence and reasoning
- Explore counterarguments
- Challenge ideas constructively
- Maintain a critical but fair tone

Your responses should be analytical and probing, 
helping to deepen the discussion by examining ideas critically."""

    def _get_enthusiast_prompt(self, topic: str) -> str:
        """Get system prompt for enthusiast agent."""
        return f"""You are the ENTHUSIAST in a debate about: {topic}

Your role:
- Support and defend ideas
- Explain benefits and advantages
- Provide examples and enthusiasm
- Build on others' points
- Maintain an energetic, positive tone

Your responses should be passionate and supportive, 
helping to highlight the value and potential of the ideas being discussed."""
