"""Web search functionality for the Research Agent."""

import requests
from rich.console import Console
from config import SEARXNG_URL, nLinksToSearchPerQuery, relevanceThreshold
from models import ResearchAgentState
from utils import generate_embedding, cosine_similarity
import trafilatura


def search_web(query: str, state: ResearchAgentState) -> str:
    """Search the web using SearXNG and return scraped content."""
    console = Console()
    
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
            return ""
        text = ""
        articleCount = 0
        for result in results:
            url = result["url"]
            console.print(f"[dim]📄 Fetching:[/dim] {url}")
            
            downloaded = trafilatura.fetch_url(url)
            chunk = trafilatura.extract(downloaded)
            if chunk is not None:
                query_embedding = generate_embedding(query)
                chunk_embedding = generate_embedding(chunk[:1000])
                relevance_score = cosine_similarity(query_embedding, chunk_embedding)
                
                # Convert to percentage (0.0-1.0 → 0%-100%)
                relevance_percentage = relevance_score * 100
                
                # Format as percentage with 1 decimal place
                relevance_str = f"{relevance_percentage:.1f}%"
                
                console.print(f"[dim]Relevance:[/dim] {relevance_str}")
                
                if relevance_score > relevanceThreshold:
                    text += chunk
                    articleCount += 1
                    state.nTotalArticlesProcessed += 1
                    if articleCount == nLinksToSearchPerQuery:
                        return text
            else:
                console.print(f"[yellow]⚠️  Could not extract content from: {url}[/yellow]")
        
        return text
    except requests.exceptions.RequestException as e:
        console.print(f"[red]❌ Network error for '{query}': {e}[/red]")
        return ""
    except Exception as e:
        console.print(f"[red]❌ Unexpected error for '{query}': {e}[/red]")
        return ""