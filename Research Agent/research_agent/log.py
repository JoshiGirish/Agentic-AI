"""Logging module for the Research Agent."""

import json
import os
from datetime import datetime
from typing import Dict, List, Any
from rich.console import Console
from rich.panel import Panel
from rich import box

console = Console()


class ArticleLogEntry:
    """Data structure to store article logging information."""
    
    def __init__(
        self,
        query: str,
        article_url: str,
        similarity_score: float,
        compressed_summary: str = ""
    ):
        self.query = query
        self.url = article_url
        self.similarity_score = similarity_score
        self.compressed_summary = compressed_summary
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert entry to dictionary for JSON serialization."""
        return {
            "query": self.query,
            "url": self.url,
            "similarity_score": round(self.similarity_score, 4),
        }


class ArticleLogger:
    """Logger for tracking articles, similarity scores, and compressed summaries."""
    
    def __init__(self, log_file: str = "reference.md"):
        """Initialize the logger."""
        self.log_file = log_file
        self.entries: List[ArticleLogEntry] = []
        self.query_data: Dict[str, List[ArticleLogEntry]] = {}
        self.console = Console()
    
    def add_entry(
        self,
        query: str,
        article_url: str,
        similarity_score: float,
        compressed_summary: str = ""
    ) -> None:
        """Add a new log entry."""
        entry = ArticleLogEntry(
            query=query,
            article_url=article_url,
            similarity_score=similarity_score,
            compressed_summary=compressed_summary
        )
        self.entries.append(entry)
        
        if query not in self.query_data:
            self.query_data[query] = []
        self.query_data[query].append(entry)
    
    def get_entries_for_query(self, query: str) -> List[ArticleLogEntry]:
        """Get all entries for a specific query."""
        return self.query_data.get(query, [])
    
    def get_all_queries(self) -> List[str]:
        """Get list of all unique queries."""
        return list(self.query_data.keys())
    
    def clear(self) -> None:
        """Clear all stored entries."""
        self.entries.clear()
        self.query_data.clear()
    
    def generate_reference_file(self) -> str:
        """Generate the reference markdown file content."""
        if not self.entries:
            return "# No article data logged yet."

        # Serialize entries through their structured to_dict() form rather than
        # str(), which would produce "<log.ArticleLogEntry object at 0x...>".
        json_data = json.dumps(
            [entry.to_dict() for entry in self.entries],
            indent=2,
            ensure_ascii=False
        )

        return f"""## Detailed JSON Data

```json
{json_data}
```"""
    
    def log_to_file(self, title: str = "Article Log Reference") -> str:
        """Log all entries to a markdown file."""
        log_content = self.generate_reference_file()
        
        # Ensure directory exists
        log_dir = os.path.dirname(self.log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # Write to file
        with open(self.log_file, 'w', encoding='utf-8') as f:
            f.write(log_content)
        
        # Print confirmation
        self.console.print(Panel.fit(
            f"✅ Article log written to: {self.log_file}",
            box=box.SIMPLE
        ))
        
        return self.log_file
    
    def print_summary(self) -> None:
        """Print a summary to console."""
        if not self.entries:
            self.console.print("[yellow]No entries logged yet.[/yellow]")
            return
        
        total_articles = len(self.entries)
        unique_queries = len(self.get_all_queries())
        
        self.console.print(Panel.fit(
            f"\n📊 Article Log Summary:\n"
            f"   Total articles logged: {total_articles}\n"
            f"   Unique queries: {unique_queries}\n"
            f"   Log file: {self.log_file}",
            box=box.ROUNDED
        ))


def create_logger(log_file: str = "reference.md") -> ArticleLogger:
    """Factory function to create a new logger instance."""
    return ArticleLogger(log_file=log_file)
