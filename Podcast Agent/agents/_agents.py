"""Agent implementations for the Podcast Conversation Platform."""

import re

from langchain_openai import ChatOpenAI
from pydantic import SecretStr
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from models import PodcastState


class PodcastAgent:
    """Base class for podcast agents."""
    
    def __init__(self, role: str, personality: str):
        self.role = role
        self.personality = personality
        self.llm = None
    
    def initialize(self):
        """Initialize the LLM client."""
        self.llm = ChatOpenAI(
            model="gemma-4-E4b-it.Q4_K_M.gguf",
            base_url="http://localhost:8080/v1",
            api_key=SecretStr("dummy-key"),
            temperature=0.7,
            streaming=True
        )
    
    async def generate_response(
        self,
        topic: str,
        conversation_history: list,
        max_tokens: int = 500
    ) -> str:
        """Generate a response based on the topic and history."""
        if self.llm is None:
            self.initialize()
        
        system_prompt = self._get_system_prompt(topic)

        system_prompt += """

IMPORTANT OUTPUT RULES:
- Reply with ONLY your own spoken lines, in character as your podcast role.
- Start directly with your words. NEVER prefix your reply with a label such as "host:", "guest:", "skeptic:", or "enthusiast:".
- NEVER quote, copy, or repeat a previous speaker's message.
- Keep your reply natural and conversational."""

        messages = [SystemMessage(content=system_prompt)]

        for msg in conversation_history[-6:]:
            if msg.get("agent") == self.role:
                messages.append(AIMessage(content=msg.get("content", "")))
            else:
                messages.append(HumanMessage(content=f"{msg.get('agent', 'user')}: {msg.get('content', '')}"))

        response = await self.llm.ainvoke(messages)

        content = str(response.content).strip()
        label_re = re.compile(r"^(?:%s)\s*(?::|response)[\s:-]*" % re.escape(self.role), re.IGNORECASE)
        divider_re = re.compile(r"^\s*[-=#>*\s]{2,}\s*", re.DOTALL)
        content = divider_re.sub("", content).strip()
        while True:
            before = content
            content = label_re.sub("", content).strip()
            content = divider_re.sub("", content).strip()
            if content == before:
                break
        return content
    
    def _get_system_prompt(self, topic: str) -> str:
        """Get the system prompt for this agent."""
        raise NotImplementedError


class HostAgent(PodcastAgent):
    """Host agent - guides conversation, asks questions."""
    
    def __init__(self):
        super().__init__(
            role="host",
            personality="guiding, curious, clarifier"
        )
    
    def _get_system_prompt(self, topic: str) -> str:
        return f"""You are the HOST of a podcast discussing: {topic}

Your role:
- Guide the conversation and keep it engaging
- Ask insightful questions
- Encourage the guest to share their expertise
- Summarize key points periodically
- Maintain a friendly, professional tone

Speak concisely and keep the conversation flowing. 
Your responses should be natural and conversational."""


class GuestAgent(PodcastAgent):
    """Guest agent - provides expertise, answers questions."""
    
    def __init__(self):
        super().__init__(
            role="guest",
            personality="expert, knowledgeable, articulate"
        )
    
    def _get_system_prompt(self, topic: str) -> str:
        return f"""You are the GUEST on a podcast discussing: {topic}

Your role:
- Share your expertise on the topic
- Answer the host's questions thoughtfully
- Provide examples and insights
- Keep explanations clear and accessible
- Maintain an engaging, knowledgeable tone

Speak with authority but remain approachable. 
Your responses should be informative and engaging."""


class SkepticAgent(PodcastAgent):
    """Skeptic agent - questions claims, seeks evidence."""
    
    def __init__(self):
        super().__init__(
            role="skeptic",
            personality="critical, questioning, analytical"
        )
    
    def _get_system_prompt(self, topic: str) -> str:
        return f"""You are the SKEPTIC in a debate about: {topic}

Your role:
- Question assumptions and claims
- Ask for evidence and reasoning
- Explore counterarguments
- Challenge ideas constructively
- Maintain a critical but fair tone

Your responses should be analytical and probing, 
helping to deepen the discussion by examining ideas critically."""


class EnthusiastAgent(PodcastAgent):
    """Enthusiast agent - supports ideas, explains benefits."""
    
    def __init__(self):
        super().__init__(
            role="enthusiast",
            personality="supportive, passionate, explanatory"
        )
    
    def _get_system_prompt(self, topic: str) -> str:
        return f"""You are the ENTHUSIAST in a debate about: {topic}

Your role:
- Support and defend ideas
- Explain benefits and advantages
- Provide examples and enthusiasm
- Build on others' points
- Maintain an energetic, positive tone

Your responses should be passionate and supportive, 
helping to highlight the value and potential of the ideas being discussed."""
