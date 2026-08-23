"""Feed parser agent for the AI News Multi-Agent System."""

from typing import Optional

from .base import BaseAgent
from .state import NewsAgentState


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