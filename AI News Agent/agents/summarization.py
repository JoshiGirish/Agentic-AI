"""Summarization agent for the AI News Multi-Agent System."""

from .base import BaseAgent
from .config import LLM_MODEL, LLM_URL
from .state import NewsAgentState
from prompts import SUMMARIZATION_SYSTEM_PROMPT


class SummarizationAgent(BaseAgent):
    """Agent responsible for summarizing article content using a local LLM."""

    def __init__(self, max_tokens: int = 500):
        super().__init__(
            "SummarizationAgent",
            "Summarizes article content using local LLM"
        )
        self.max_tokens = max_tokens
        self.llm = None
        self.system_prompt = SUMMARIZATION_SYSTEM_PROMPT

    def initialize(self, llm_url: str = LLM_URL):
        """Initialize the LLM client."""
        
        from langchain_openai import ChatOpenAI
        from pydantic import SecretStr

        self.llm = ChatOpenAI(
            model=LLM_MODEL,
            base_url=llm_url,
            api_key=SecretStr("dummy-key"),
            temperature=0.2
        )
    

    async def process(self, state: NewsAgentState) -> NewsAgentState:
        """Summarize the article content."""
        if not state.get("article_content"):
            return state

        if self.llm is None:
            self.initialize()

        try:
            prompt = self.system_prompt + state["article_content"]

            if len(prompt) > 15000:
                prompt = prompt[:15000]

            response = await self.llm.ainvoke([{"role": "user", "content": prompt}])

            summary = response.content if hasattr(response, "content") else str(response)
            summary = summary.strip()

            state["summary"] = summary
            return state

        except Exception as e:
            print(f"Error in summarization: {e}")
            state["summary"] = f"[Summary unavailable - Error: {str(e)[:100]}]"
            return state