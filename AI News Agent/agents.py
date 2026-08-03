"""Agent implementations for the AI News Multi-Agent System."""

import os
from typing import Optional, TypedDict
from langgraph.graph import StateGraph, START, END
from dotenv import load_dotenv

load_dotenv()


# ============================================================================
# Configuration
# ============================================================================

LLM_URL = os.getenv("LLM_URL", "http://localhost:8080/v1/chat")
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

        if self.session is None:
            self.initialize()

        try:
            response = self.session.get(
                state["article_url"],
                timeout=30,
                allow_redirects=True
            )

            if response.status_code != 200:
                return state

            text = self._extract_text(response.text)
            state["article_content"] = text
            return state

        except Exception as e:
            print(f"Error fetching content from {state.get('article_url')}: {e}")
            return state

    def _extract_text(self, html: str) -> str:
        """Extract readable text from HTML content."""
        import re

        text = re.sub(r'<[^>]+>', ' ', html)
        text = re.sub(r'[^\w\s.,!?;:()\-]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()

        return text


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
        self.system_prompt = """You are an expert news summarizer. Your task is to create a concise, informative summary of the provided article.

Guidelines:
1. Identify the main topic and key points
2. Include important facts, figures, and conclusions
3. Keep the summary neutral and objective
4. Aim for 100-200 words unless the content is exceptionally dense
5. Use clear, professional language
6. Format as plain text (no markdown)

Article content:
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
    

    def process(self, state: NewsAgentState) -> NewsAgentState:
        """Summarize the article content."""
        if not state.get("article_content"):
            return state

        if self.llm is None:
            self.initialize()

        try:
            prompt = self.system_prompt + state["article_content"]

            if len(prompt) > 10000:
                prompt = prompt[-10000:]

            response = self.llm.invoke([{"role": "user", "content": prompt}])

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
    """Agent responsible for posting summaries to Discord."""

    def __init__(self, webhook_url: Optional[str] = None):
        super().__init__(
            "DiscordPosterAgent",
            "Posts summaries to Discord webhook"
        )
        self.webhook_url = webhook_url or os.getenv("WEBHOOK_URL", "")
        self.session = None

    def initialize(self):
        """Initialize HTTP session for Discord webhook."""
        import requests
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
        })

    def process(self, state: NewsAgentState) -> NewsAgentState:
        """Post the summary to Discord."""
        if not self.webhook_url:
            print("No webhook URL configured. Skipping Discord posting.")
            return state

        if self.session is None:
            self.initialize()

        embed = {
            "title": state.get("feed_data", {}).get("title", "Untitled"),
            "url": state.get("feed_data", {}).get("link", ""),
        }

        category = state.get("feed_data", {}).get("category", "General")
        if category:
            embed["footer"] = {"text": category}

        image_url = state.get("feed_data", {}).get("image")
        if image_url:
            embed["thumbnail"] = {"url": image_url}

        summary = state.get("summary", "")
        if len(summary) > 1000:
            summary = summary[:1000] + "..."
        if summary:
            embed["description"] = summary

        payload = {"embeds": [embed]}

        try:
            response = self.session.post(
                self.webhook_url,
                json=payload,
                timeout=15
            )

            if response.status_code == 204:
                print(f"✓ Sent to Discord: {state.get('feed_data', {}).get('title', 'Untitled')}")
            else:
                print(f"⚠ Discord response: {response.status_code}")

        except Exception as e:
            print(f"✗ Error posting to Discord: {e}")

        return state


# ============================================================================
# Main Pipeline
# ============================================================================

def create_pipeline() -> StateGraph:
    """Create the complete agent pipeline using LangGraph."""
    state = NewsAgentState()

    builder = StateGraph(NewsAgentState)

    feed_parser = FeedParserAgent()
    builder.add_node("feed_parser", lambda s: feed_parser.process(s))

    content_fetcher = ContentFetcherAgent()
    builder.add_node("content_fetcher", lambda s: content_fetcher.process(s))

    summarizer = SummarizationAgent()
    builder.add_node("summarizer", lambda s: summarizer.process(s))

    poster = DiscordPosterAgent()
    builder.add_node("poster", lambda s: poster.process(s))

    builder.add_edge(START, "feed_parser")
    builder.add_edge("feed_parser", "content_fetcher")
    builder.add_edge("content_fetcher", "summarizer")
    builder.add_edge("summarizer", "poster")
    builder.add_edge("poster", END)

    graph = builder.compile()

    return graph


def run_pipeline(feed_url: str, category: str = "General") -> dict:
    """Run the complete pipeline for a single feed item."""
    graph = create_pipeline()

    state = NewsAgentState()
    state["feed_url"] = feed_url
    state["category"] = category

    result = graph.invoke(state)

    return result


if __name__ == "__main__":
    import json

    test_feed = "https://techcrunch.com/feed/"

    print("Running AI News Multi-Agent Pipeline...\n")
    print(f"Processing feed: {test_feed}\n")

    result = run_pipeline(test_feed, category="Technology")

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