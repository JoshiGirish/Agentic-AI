"""Web search functionality for the Research Agent."""

import requests
from rich.console import Console
from config import SEARXNG_URL, relevanceThreshold
from models import ResearchAgentState
from utils import generate_embedding, cosine_similarity
import trafilatura
from w3lib.url import canonicalize_url
from log import create_logger, ArticleLogger
import os

def search_web(query: str, state: ResearchAgentState, nLinks: int = 3, logger: ArticleLogger = None) -> dict:
    """Search the web using SearXNG and return scraped content."""
    console = Console()
    nTotalArticlesProcessed = 0
    
    # Initialize logger if not provided
    if logger is None:
        log_file = os.environ.get("ARTICLE_LOG_FILE", "reference.md")
        logger = create_logger(log_file)
    
    try:
        response = requests.get(
            SEARXNG_URL,
            params={
                "q": query,
                "format": "json",
            },
            timeout=20,
        )
        response.raise_for_status()
        results = response.json()["results"]
        
        if not results:
            console.print(f"[yellow]⚠️  No results found for query: {query}[/yellow]")
            return {}
        text = ""
        articleCount = 0
        urls = state.visitedUrls
        for result in results:
            url = result["url"]
            if url not in urls:
                console.print(f"[dim]📄 Fetching:[/dim] {url}")
                urls.add(canonicalize_url(url))
                downloaded = trafilatura.fetch_url(url)
                chunk = trafilatura.extract(downloaded)
                if chunk is not None:
                    query_embedding = generate_embedding(query)
                    chunk_embedding = generate_embedding(chunk[:1000])
                    if query_embedding is not None and chunk_embedding is not None:
                        relevance_score = cosine_similarity(query_embedding, chunk_embedding)
                    
                        # Convert to percentage (0.0-1.0 → 0%-100%)
                        relevance_percentage = relevance_score * 100
                        
                        # Format as percentage with 1 decimal place
                        relevance_str = f"{relevance_percentage:.1f}%"
                        
                        console.print(f"[dim]Relevance:[/dim] {relevance_str}")
                        
                        if relevance_score > relevanceThreshold:
                            text += chunk
                            articleCount += 1
                            nTotalArticlesProcessed += 1
                            
                            # Log the article if logger is available
                            if logger is not None:
                                compressed_summary = f"[Article from {url}]" + chunk[:200] if len(chunk) > 200 else chunk
                                logger.add_entry(
                                    query=query,
                                    article_url=url,
                                    similarity_score=relevance_score,
                                    compressed_summary=compressed_summary
                                )
                            
                            if articleCount == nLinks:
                                return {"text": text, "nArticles": nTotalArticlesProcessed, "urls": urls}
                    else:
                        console.print(f"[yellow]⚠️  Could not extract content from: {url}[/yellow]")
                else:
                    console.print(f"[yellow]⚠️  Could not extract content from: {url}[/yellow]")
        
        return {"text": text, "nArticles": nTotalArticlesProcessed, "urls": urls}
    except requests.exceptions.RequestException as e:
        console.print(f"[red]❌ Network error for '{query}': {e}[/red]")
        return {}
    except Exception as e:
        console.print(f"[red]❌ Unexpected error for '{query}': {e}[/red]")
        return {}