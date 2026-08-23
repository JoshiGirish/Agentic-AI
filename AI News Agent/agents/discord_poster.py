"""Discord poster agent for the AI News Multi-Agent System."""

from .base import BaseAgent
from .config import LLM_MODEL, LLM_URL
from .state import NewsAgentState


class DiscordPosterAgent(BaseAgent):
    """Agent responsible for deciding whether/how to post to Discord."""

    def __init__(self, mcp_url: str = "http://ai-news-mcp:8000/mcp"):
        super().__init__(
            "DiscordPosterAgent",
            "Uses an MCP Discord server to publish news articles"
        )

        self.mcp_url = mcp_url
        self.mcp_client = None
        self.agent = None

    async def initialize(self):
        """Connect to the Discord MCP server and create the agent."""
        
        from langchain_openai import ChatOpenAI
        from pydantic import SecretStr
        from langchain_mcp_adapters.client import MultiServerMCPClient
        from langchain.agents import create_agent


        self.mcp_client = MultiServerMCPClient(
            {
                "discord": {
                    "transport": "streamable_http",
                    "url": self.mcp_url,
                }
            }
        )

        tools = await self.mcp_client.get_tools()

        # Don't give configuration tools to the LLM.
        tools = [
            tool
            for tool in tools
            if tool.name in {
                "post_discord_article",
                "get_discord_status",
            }
        ]

        print("Discord MCP tools:")
        for tool in tools:
            print(f"  - {tool.name}")

        llm = ChatOpenAI(
            model=LLM_MODEL,
            base_url=LLM_URL,
            api_key=SecretStr("dummy-key"),
            temperature=0.0,
        )

        self.agent = create_agent(
            model=llm,
            tools=tools,
            system_prompt="""
                    You are the Discord publishing agent for an AI news system.

                    Your job is to decide whether a news article should be posted
                    to Discord and, when appropriate, use the available Discord
                    MCP tools to publish it.

                    When posting an article:
                    - Use the article title exactly as provided.
                    - Use the provided summary as the content.
                    - Use the original article URL.
                    - Include the image URL when available.
                    - Include the category when available.

                    Do not invent URLs, titles, summaries, or images.

                    Only post an article when explicitly instructed to publish it.

                    After calling the Discord tool, report whether the operation succeeded.
                    """,
        )

    async def process(self, state: NewsAgentState) -> NewsAgentState:

        if self.agent is None:
            await self.initialize()

        feed_data = state.get("feed_data", {})

        result = await self.agent.ainvoke({
            "messages": [
                {
                    "role": "user",
                    "content": f"""
                        Publish this news article to Discord.

                        Title:
                        {feed_data.get("title", "")}

                        Summary:
                        {state.get("summary", "")}

                        URL:
                        {feed_data.get("link", "")}

                        Image:
                        {feed_data.get("image", "")}

                        Category:
                        {feed_data.get("category", "")}
                        """
                }
            ]
        })

        state["discord_result"] = result["messages"][-1].content

        return state