"""Orchestrator for the AI News Multi-Agent System."""

import os
import json
from typing import Optional, List
from datetime import datetime
from agents import (
    NewsAgentState,
    create_pipeline,
    run_pipeline,
    FeedParserAgent,
    ContentFetcherAgent,
    SummarizationAgent,
    DiscordPosterAgent,
)


# ============================================================================
# Configuration
# ============================================================================

FEEDS_FILE = os.getenv("FEEDS_FILE", "feeds.json")
LOG_FILE = os.getenv("LOG_FILE", "news.log")
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "1"))


# ============================================================================
# Feeds Manager
# ============================================================================

class FeedsManager:
    """Manages RSS/Atom feeds to be processed."""

    def __init__(self, feeds_file: str = FEEDS_FILE):
        self.feeds_file = feeds_file
        self.feeds: List[dict] = []

    def load_feeds(self) -> List[dict]:
        """Load feeds from JSON file."""
        if os.path.exists(self.feeds_file):
            try:
                with open(self.feeds_file, "r") as f:
                    self.feeds = json.load(f)["feeds"]
                print(f"Loaded {len(self.feeds)} feeds from {self.feeds_file}")
                return self.feeds
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading feeds: {e}")
                return []
        return []

    def save_feeds(self, feeds: List[dict]) -> bool:
        """Save feeds to JSON file."""
        try:
            with open(self.feeds_file, "w") as f:
                json.dump(feeds, f, indent=2)
            return True
        except IOError as e:
            print(f"Error saving feeds: {e}")
            return False

    def add_feed(self, url: str, name: str = "", category: str = "") -> bool:
        """Add a new feed."""
        feed = {
            "url": url,
            "name": name,
            "category": category,
            "last_processed": None,
        }
        self.feeds.append(feed)
        return self.save_feeds(self.feeds)

    def remove_feed(self, url: str) -> bool:
        """Remove a feed by URL."""
        for i, feed in enumerate(self.feeds):
            if feed["url"] == url:
                del self.feeds[i]
                return self.save_feeds(self.feeds)
        return False

    def get_feeds(self) -> List[dict]:
        """Get all feeds."""
        return self.feeds

    def get_feed(self, url: str) -> Optional[dict]:
        """Get a feed by URL."""
        for feed in self.feeds:
            if feed["url"] == url:
                return feed
        return None


# ============================================================================
# Orchestrator
# ============================================================================

class AINewsOrchestrator:
    """
    Main orchestrator for the AI News Multi-Agent System.

    Responsibilities:
    - Load and manage feeds
    - Process feeds through the agent pipeline
    - Handle errors and retries
    - Log results and statistics
    """

    def __init__(
        self,
        feeds_file: Optional[str] = None,
        log_file: Optional[str] = None,
        batch_size: int = 1,
    ):
        self.feeds_manager = FeedsManager(feeds_file or FEEDS_FILE)
        self.log_file = log_file or LOG_FILE
        self.batch_size = batch_size
        self.processed_count = 0
        self.error_count = 0

    def log(self, message: str, level: str = "INFO") -> None:
        """Log a message with timestamp."""
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] [{level}] {message}\n"

        # Print to console
        print(log_entry.strip())

        # Write to file
        try:
            with open(self.log_file, "a") as f:
                f.write(log_entry)
        except IOError:
            pass

    def process_single_feed(self, feed: dict) -> Optional[NewsAgentState]:
        """
        Process a single feed item through the pipeline.

        Args:
            feed: Feed dictionary with url, name, category

        Returns:
            Processed state or None if failed
        """
        feed_url = feed["url"]
        name = feed.get("name", "Untitled")
        category = feed.get("category", "General")

        self.log(f"Processing feed: {name} ({feed_url})", "INFO")

        try:
            # Run the pipeline
            result = run_pipeline(feed_url, category=category)

            # Extract results
            feed_data = result.get("feed_data", {})
            summary = result.get("summary", "")

            # Update feed metadata
            feed["last_processed"] = datetime.now().isoformat()
            feed["name"] = name
            feed["category"] = category
            feed["summary"] = summary[:500]  # Truncate for storage

            # Save updated feeds
            self.feeds_manager.save_feeds(self.feeds_manager.get_feeds())

            self.log(
                f"✓ Processed: {feed_data.get('title', 'Untitled')}",
                "INFO",
            )

            return result

        except Exception as e:
            self.log(f"✗ Error processing {feed_url}: {e}", "ERROR")
            self.error_count += 1
            return None

    def process_all_feeds(self) -> List[dict]:
        """
        Process all loaded feeds.

        Returns:
            List of processed feed results
        """
        feeds = self.feeds_manager.get_feeds()
        results = []

        if not feeds:
            self.log("No feeds to process", "WARNING")
            return results

        self.log(f"Starting to process {len(feeds)} feeds", "INFO")

        for feed in feeds:
            print(f"feed ---------> {feed}")
            result = self.process_single_feed(feed)
            if result:
                results.append(result)
                self.processed_count += 1

        self.log(
            f"Completed: {self.processed_count}/{len(feeds)} feeds processed",
            "INFO",
        )

        return results

    def process_url(self, url: str, name: str = "", category: str = "") -> dict:
        """
        Process a single URL (not from a feed file).

        Args:
            url: URL of the RSS/Atom feed
            name: Name for the feed
            category: Category for the feed

        Returns:
            Processed result or empty dict if failed
        """
        # Add to feeds list
        self.feeds_manager.add_feed(url, name, category)

        # Process
        result = self.process_single_feed({
            "url": url,
            "name": name,
            "category": category,
        })

        return result or {}

    def get_statistics(self) -> dict:
        """Get processing statistics."""
        return {
            "processed": self.processed_count,
            "errors": self.error_count,
            "feeds_file": self.feeds_manager.feeds_file,
            "log_file": self.log_file,
        }


# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    """Main entry point for the orchestrator."""
    import argparse

    parser = argparse.ArgumentParser(
        description="AI News Multi-Agent System Orchestrator",
    )
    parser.add_argument(
        "--feeds",
        type=str,
        default=None,
        help="Path to feeds JSON file",
    )
    parser.add_argument(
        "--log",
        type=str,
        default=None,
        help="Path to log file",
    )
    parser.add_argument(
        "--add",
        type=str,
        metavar="URL",
        help="Add a new feed URL",
    )
    parser.add_argument(
        "--name",
        type=str,
        default="",
        help="Name for the new feed",
    )
    parser.add_argument(
        "--category",
        type=str,
        default="General",
        help="Category for the new feed",
    )

    args = parser.parse_args()

    # Create orchestrator
    orchestrator = AINewsOrchestrator(
        feeds_file=args.feeds,
        log_file=args.log,
    )

    # Handle add command
    if args.add:
        orchestrator.log(f"Adding feed: {args.add}", "INFO")
        orchestrator.process_url(
            url=args.add,
            name=args.name,
            category=args.category,
        )
        return

    # Load feeds
    feeds = orchestrator.feeds_manager.load_feeds()

    if not feeds:
        orchestrator.log("No feeds found. Use --add to add a feed.", "WARNING")
        return

    # Process all feeds
    orchestrator.process_all_feeds()

    # Print statistics
    stats = orchestrator.get_statistics()
    orchestrator.log(
        f"Statistics: {stats}",
        "INFO",
    )


if __name__ == "__main__":
    main()