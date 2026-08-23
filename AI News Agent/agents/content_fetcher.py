"""Content fetcher agent for the AI News Multi-Agent System."""

import requests
import trafilatura

from .base import BaseAgent
from .state import NewsAgentState


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