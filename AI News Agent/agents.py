"""Agent implementations for the AI News Multi-Agent System."""

import asyncio
import os
from typing import Optional, TypedDict
from langgraph.graph import StateGraph, START, END
from dotenv import load_dotenv
import trafilatura

load_dotenv()


# ============================================================================
# Configuration
# ============================================================================

LLM_URL = os.getenv("LLM_URL", "http://localhost:8080/v1")
LLM_MODEL = os.getenv("LLM_MODEL", "Qwen3.5-9B.Q4_K_M.gguf")


# ============================================================================
# Agent State Definition (TypedDict for LangGraph compatibility)
# ============================================================================

class NewsAgentState(TypedDict, total=False):
    """State shared across all agents in the pipeline."""

    feed_url: Optional[str]
    feed_data: dict
    article_url: Optional[str]
    article_content: str
    summary: str
    image_url: Optional[str]
    category: str
    discord_result: str


# ============================================================================
# Agent Base Class
# ============================================================================

class BaseAgent:
    """Base class for all agents in the system."""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    def process(self, state: NewsAgentState) -> NewsAgentState:
        """Process the state and return updated state."""
        raise NotImplementedError


# ============================================================================
# Feed Parser Agent
# ============================================================================

class FeedParserAgent(BaseAgent):
    """Agent responsible for parsing RSS/Atom feeds."""

    def __init__(self):
        super().__init__("FeedParserAgent", "Parses RSS/Atom feeds and extracts article metadata")
        self.feedparser = None

    def initialize(self):
        """Initialize the feedparser library."""
        import feedparser
        self.feedparser = feedparser

    def process(self, state: NewsAgentState) -> NewsAgentState:
        """Parse the RSS/Atom feed and extract article metadata."""
        if not state.get("feed_url"):
            return state

        if self.feedparser is None:
            self.initialize()

        feed = self.feedparser.parse(state["feed_url"])

        if not feed.entries:
            return state

        entry = feed.entries[0]

        title = getattr(entry, "title", "Untitled").strip() or "Untitled"
        if title == "Untitled":
            return state
        link = self._get_entry_link(entry)

        published = getattr(entry, "published_parsed", None)
        pub_date = None
        if published:
            try:
                from datetime import datetime
                pub_date = datetime(*published[:6]).date()
            except (ValueError, TypeError):
                pass

        image_url = self._get_entry_image(entry)

        feed_title = getattr(feed, "feed", {}).get("title", "General")
        category = feed_title.split("/")[-1].strip() or "General"

        state["feed_data"] = {
            "title": title,
            "link": link,
            "published": pub_date,
            "image": image_url,
            "category": category,
        }
        
        state["article_url"] = link

        return state

    def _get_entry_link(self, entry) -> Optional[str]:
        """Get the destination URL for the feed item."""
        link = getattr(entry, "link", None)
        if link:
            return link

        for link_data in getattr(entry, "links", []):
            if link_data.get("rel") == "alternate":
                href = link_data.get("href")
                if href:
                    return href

        return None

    def _get_entry_image(self, entry) -> Optional[str]:
        """Extract an image URL from an RSS/Atom entry."""
        media_content = getattr(entry, "media_content", None)
        if media_content:
            for media in media_content:
                media_type = media.get("type", "")
                url = media.get("url")

                if url and (
                    media_type.startswith("image/")
                    or any(
                        url.lower().split("?")[0].endswith(ext)
                        for ext in [".jpg", ".jpeg", ".png", ".gif", ".webp"]
                    )
                ):
                    return url

        media_thumbnail = getattr(entry, "media_thumbnail", None)
        if media_thumbnail:
            for thumbnail in media_thumbnail:
                url = thumbnail.get("url")
                if url:
                    return url

        enclosures = getattr(entry, "enclosures", None)
        if enclosures:
            for enclosure in enclosures:
                url = enclosure.get("href") or enclosure.get("url")
                media_type = enclosure.get("type", "")

                if url and (
                    media_type.startswith("image/")
                    or any(
                        url.lower().split("?")[0].endswith(ext)
                        for ext in [".jpg", ".jpeg", ".png", ".gif", ".webp"]
                    )
                ):
                    return url

        return None

# ============================================================================
# Content Fetcher Agent
# ============================================================================

class ContentFetcherAgent(BaseAgent):
    """Agent responsible for fetching article content from URLs."""

    def __init__(self):
        super().__init__(
            "ContentFetcherAgent",
            "Fetches and extracts content from article URLs"
        )
        self.session = None

    def initialize(self):
        """Initialize HTTP session with proper headers."""
        import requests
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/91.0.4472.124 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
        })

    def process(self, state: NewsAgentState) -> NewsAgentState:
        """Fetch content from the article URL."""
        if not state.get("article_url"):
            return state

        try:
            articlePage = trafilatura.fetch_url(state["article_url"])
            text = trafilatura.extract(articlePage)

            state["article_content"] = text
            return state

        except Exception as e:
            print(f"Error fetching content from {state.get('article_url')}: {e}")
            return state



# ============================================================================
# Summarization Agent
# ============================================================================

class SummarizationAgent(BaseAgent):
    """Agent responsible for summarizing article content using a local LLM."""

    def __init__(self, max_tokens: int = 500):
        super().__init__(
            "SummarizationAgent",
            "Summarizes article content using local LLM"
        )
        self.max_tokens = max_tokens
        self.llm = None
        self.system_prompt = """You are an expert at creating concise descriptions of web articles.

            Your task is to read the provided webpage content and write a short description that tells the reader what the article is about.

            The goal is NOT to summarize the entire article. The goal is to give the reader enough context to understand the article's main subject, focus, and key takeaway.

            ## STEP 1 — CHECK ARTICLE AVAILABILITY

            First determine whether the extracted content contains meaningful article content.

            The extracted content may contain only:
            - A paywall or subscription prompt
            - "Subscribe to continue reading"
            - "Sign in to read the full article"
            - Login or registration forms
            - Cookie notices
            - Advertisements
            - Navigation menus
            - Website headers or footers
            - Error or access-denied messages
            - A headline or short teaser without the actual article
            - Other website boilerplate

            If the extracted content does not contain enough substantive article content to understand what the article is about, do NOT generate a description.

            Return EXACTLY:

            Unable to summarize: article content is not available.

            Do not add any explanation or additional text.

            ## ARTICLE DESCRIPTION

            If meaningful article content is available, describe what the article is about.

            Focus on:
            - The central topic
            - The main event, issue, development, finding, or subject discussed
            - The most important context needed to understand the article
            - The primary conclusion or takeaway, if clearly stated

            Do NOT attempt to cover every fact, detail, statistic, quote, or argument in the article.

            The reader should finish reading your response knowing:

            "What is this article about?"

            ## CONTENT RULES

            1. Use only information explicitly supported by the article.
            2. Do not invent facts or speculate.
            3. Do not provide your own opinion.
            4. Do not reproduce detailed facts unless they are essential to explaining the article's subject.
            5. Do not list multiple secondary points.
            6. Do not turn the description into a detailed summary.
            7. Do not describe the article's structure or writing style.
            8. Do not mention that you are an AI or that you are summarizing the article.
            9. Ignore navigation, advertisements, cookie notices, menus, boilerplate, and unrelated content.
            10. Do not infer article content from the title, URL, metadata, or teaser when the actual article content is unavailable.

            ## LENGTH

            - Prefer approximately 50–80 words.
            - 100 words is an absolute maximum, not a target.
            - Be concise.
            - Do not add information simply to reach a word count.
            - If the article can be adequately described in fewer than 40 words, use fewer words.

            ## OUTPUT FORMAT

            The output MUST:
            - Be exactly ONE paragraph.
            - Contain plain text only 
            - Contain no Markdown.
            - Contain no title or headline.
            - Contain no headings or sections.
            - Contain no bullet points or numbered lists.
            - Contain no tables.
            - Contain no emojis.
            - Contain no line breaks.
            - Return ONLY the article description.
            - Color/highlight important keywords/numbers

            If article content is unavailable, return exactly:

            Unable to summarize: article content is not available.

            Do not provide reasoning, analysis, explanations, or additional text.

            ## IMPORTANT

            Think about the article internally, but output ONLY the final one-paragraph description.

            The purpose of the response is to answer:

            "What is this article about?"

            Do not answer:

            "What are all the important details in this article?"
            
                        
            ## EXAMPLES

            ### Example 1 — Technology

            INPUT:
            Title: Major technology company expands investment in artificial intelligence

            Content:
            The company announced plans to significantly increase its investment in artificial intelligence infrastructure over the next three years. The investment will fund new data centers, specialized AI chips, and additional engineering teams. Executives said the expansion is intended to meet growing demand for generative AI services from businesses and consumers. The company expects AI-related revenue to become an increasingly important part of its business. Analysts noted that the investment reflects the rapidly increasing cost of developing and operating large AI systems.

            EXPECTED OUTPUT:
            **The technology company** is significantly expanding its AI infrastructure investment to meet growing demand for generative AI services. The expansion will focus on data centers, specialized AI hardware, and engineering capacity, reflecting the increasing importance and cost of AI development and operations.

            ### Example 2 — Business

            INPUT:
            Title: Central bank keeps interest rates unchanged

            Content:
            The central bank decided to leave its benchmark interest rate unchanged at its latest policy meeting. Officials said inflation has continued to moderate but remains above the bank's long-term target. The decision follows several months of economic uncertainty and comes as policymakers assess the impact of previous rate increases. Economists expect the bank to remain cautious about reducing rates until there is clearer evidence that inflation is under control. The bank said future decisions will depend on incoming economic data.

            EXPECTED OUTPUT:
            **The central bank** is keeping interest rates unchanged as inflation remains above its target. With economic uncertainty still elevated, policymakers are taking a cautious approach to potential rate cuts and will continue to assess incoming economic data before making further changes.

            ### Example 3 — Science

            INPUT:
            Title: Researchers discover potential new treatment approach

            Content:
            Researchers have identified a potential new approach for treating a common disease in an early-stage study. The treatment targets a biological mechanism believed to contribute to disease progression. Initial laboratory results showed promising effects, but researchers emphasized that additional studies and clinical trials will be required to determine whether the approach is safe and effective in humans.

            EXPECTED OUTPUT:
            Researchers have identified a **potential new treatment approach** that targets a biological mechanism linked to disease progression. Early laboratory results are promising, but further research and clinical trials are needed to determine whether the treatment is safe and effective in humans.

            ### Example 4 — BAD OUTPUT

            INPUT:
            Title: Central bank keeps interest rates unchanged

            Content:
            The central bank decided to leave its benchmark interest rate unchanged at its latest policy meeting. Officials said inflation has continued to moderate but remains above the bank's long-term target. The decision follows several months of economic uncertainty and comes as policymakers assess the impact of previous rate increases.

            BAD OUTPUT:
            The article discusses the central bank's decision to keep interest rates unchanged. It explains that inflation has moderated but remains above the bank's target. The article also provides details about economic uncertainty, previous rate increases, and the possibility of future rate cuts.

            WHY THIS IS BAD:
            It describes the article instead of directly describing what happened. It also repeats unnecessary details and uses phrases such as "the article discusses" and "the article provides."

            ## ARTICLE INPUT

        """

    def initialize(self, llm_url: str = LLM_URL):
        """Initialize the LLM client."""
        
        from langchain_openai import ChatOpenAI
        from pydantic import SecretStr

        self.llm = ChatOpenAI(
            model=LLM_MODEL,
            base_url=LLM_URL,
            reasoning_effort="low",
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


# ============================================================================
# Discord Poster Agent
# ============================================================================

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
            reasoning_effort="low",
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


# ============================================================================
# Main Pipeline
# ============================================================================

def create_pipeline() -> StateGraph:
    """Create the complete agent pipeline using LangGraph."""
    state = NewsAgentState()

    builder = StateGraph(NewsAgentState)

    feed_parser = FeedParserAgent()
    builder.add_node("feed_parser", feed_parser.process)

    content_fetcher = ContentFetcherAgent()
    builder.add_node("content_fetcher", content_fetcher.process)

    summarizer = SummarizationAgent()
    builder.add_node("summarizer", summarizer.process)

    poster = DiscordPosterAgent()
    builder.add_node("poster", poster.process)

    builder.add_edge(START, "feed_parser")
    builder.add_edge("feed_parser", "content_fetcher")
    builder.add_edge("content_fetcher", "summarizer")
    builder.add_edge("summarizer", "poster")
    builder.add_edge("poster", END)

    graph = builder.compile()

    return graph


async def run_pipeline(feed_url: str, category: str = "General") -> dict:
    """Run the complete pipeline for a single feed item."""
    graph = create_pipeline()

    state = NewsAgentState()
    state["feed_url"] = feed_url
    state["category"] = category

    result = await graph.ainvoke(state)

    return result


async def main():
    import json

    test_feed = "https://techcrunch.com/feed/"

    print("Running AI News Multi-Agent Pipeline...\n")
    print(f"Processing feed: {test_feed}\n")

    result = await run_pipeline(test_feed, category="Technology")

    print("\n" + "=" * 60)
    print("Pipeline Results:")
    print("=" * 60)

    if result.get("feed_data"):
        print(f"Title: {result['feed_data'].get('title', 'N/A')}")
        print(f"Link: {result['feed_data'].get('link', 'N/A')}")
        print(f"Category: {result['feed_data'].get('category', 'N/A')}")
        print(f"Image: {result['feed_data'].get('image', 'N/A')}")

    if result.get("summary"):
        print(f"\nSummary:\n{result['summary'][:500]}...")

    print("\n" + "=" * 60)
    

if __name__ == "__main__":
    asyncio.run(main())