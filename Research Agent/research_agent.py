import json
import argparse
import requests
import trafilatura
import numpy as np
from pydantic import BaseModel, Field, SecretStr
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage, SystemMessage
from typing import List, Optional, Tuple
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule
from rich.markdown import Markdown

# Configuration
SEARXNG_URL = "http://searxng:8080/search"
DEFAULT_MODEL = "Qwen3.5-9B.Q4_K_M.gguf"
DEFAULT_LLM_URL = "http://localhost:8080/v1"
DEFAULT_EMBED_URL = "http://localhost:8081/v1/embeddings"
nQueriesToGenerate = 3
nLinksToSearchPerQuery = 3
relevanceThreshold = 0.60

# Initialize console for rich output
console = Console()

class ResearchAgentState(BaseModel):
    topic: str = Field(
        description="Topic from the user"
    )
    queries: list = Field(
        default_factory=list,
        description="list of semantically similar search queries for the topic"
    )
    scrapedData: list[str] = Field(
        default_factory=list,
        description="list of content scraped from web for each query"
    )
    summary: str = Field(
        default="",
        description="final summary of the research"
    )
    nTotalArticlesProcessed: int = Field(
        default=0,
        description="Total number of web articles processed for research"
    )
    
class QueryList(BaseModel):
    queries: list[str] = Field(
        min_length=nQueriesToGenerate,
        description="Three or more independent search engine queries."
    )

def get_llm() -> ChatOpenAI:
    """Get the LLM instance with proper error handling."""
    return ChatOpenAI(
        model=DEFAULT_MODEL,
        base_url=DEFAULT_LLM_URL,
        reasoning_effort="low",
        api_key=SecretStr("dummy-key"),
        temperature=0.2
    )

def get_llm_with_output() -> ChatOpenAI:
    """Get the LLM with structured output capability."""
    return get_llm().with_structured_output(QueryList)

def expand_query(state: ResearchAgentState) -> dict:
    """Expand the user topic into multiple search queries."""
    console.print(Panel.fit("[bold blue]📌 STAGE: Query Expansion[/bold blue]", style="blue"))
    console.print(Rule(style="blue"))
    console.print(f"\n[bold]Original topic:[/bold] {state.topic}")
    
    # Get current date for context
    current_date = datetime.now().strftime("%B %d, %Y")
    console.print(f"[dim]Current date:[/dim] {current_date}")
    
    llm = get_llm_with_output()
    
    # Include current date in system prompt to prevent outdated references
    sys_msg = SystemMessage(content=f"""
        Current date: {current_date}
        
        Generate at least three semantic search queries for the user's topic.
        Each query should be independent and explore different angles.
        IMPORTANT: Use the current date for any time references.
        Return only the structured output.
    """)
    
    messages = [sys_msg, HumanMessage(content=state.topic)]
    result = llm.invoke(messages)
    
    console.print("\n[bold cyan]🔍 Generated search queries:[/bold cyan]")
    for i, query in enumerate(result.queries, 1):
        console.print(f"   [{i}] {query}")
    
    return {
        "queries": result.queries
    }

def search_web(query: str, state: ResearchAgentState) -> str:
    """Search the web using SearXNG and return scraped content."""
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
                
                if not text:
                    console.print(f"[yellow]⚠️  Could not extract content from: {url}[/yellow]")
                    return ""
        
        return text
    except requests.exceptions.RequestException as e:
        console.print(f"[red]❌ Network error for '{query}': {e}[/red]")
        return ""
    except Exception as e:
        console.print(f"[red]❌ Unexpected error for '{query}': {e}[/red]")
        return ""

def research_topic(state: ResearchAgentState) -> dict:
    """Research the topic using multiple search queries."""
    console.print(Panel.fit("[bold magenta]🔬 STAGE: Web Research[/bold magenta]", style="magenta"))
    console.print(Rule(style="magenta"))
    
    scraped_data = []
    for i, query in enumerate(state.queries, 1):
        console.print(f"\n[dim]Query {i}/{len(state.queries)}:[/dim] {query}")
        text = search_web(query, state)
        scraped_data.append(text if text else "")
    
    return {
        "scrapedData": scraped_data
    }

def generate_embedding(
    input_text: str, 
    model: str = "nomic-embed-text", 
    base_url: str = DEFAULT_EMBED_URL
) -> Optional[np.ndarray]:
    """
    Generate embeddings for input text using a remote embedding model.
    
    Args:
        input_text: The text to generate embeddings for
        model: The model name to use (default: "nomic-embed-text")
        base_url: The base URL of the embedding service (default: "http://localhost:8081/v1/embeddings")
    
    Returns:
        A numpy array representing the embedding vector, or None if an error occurs
    """
    try:
        # Prepare the JSON payload
        payload = {
            "input": input_text,
            "model": model
        }
        
        # Create connection
        response = requests.post(
            base_url,
            json=payload,
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json"
            },
            timeout=30
        )
        
        # Check response status
        if response.status_code >= 200 and response.status_code < 300:
            # Parse the JSON response
            try:
                json_response = response.json()
                
                # Extract embedding from the response
                if "data" in json_response:
                    data = json_response["data"]
                    if data and len(data) > 0:
                        embedding = data[0].get("embedding", [])
                        if embedding:
                            # Return as numpy array for efficient computation
                            return np.array(embedding, dtype=np.float32)
            except json.JSONDecodeError:
                pass
            
            # Return empty array if no embedding found
            return np.array([], dtype=np.float32)
        else:
            # Print error response if available
            error_response = response.text
            if error_response:
                print(f"Error response (status {response.status_code}): {error_response}")
            
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Network error: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None


def cosine_similarity(
    embedding1: np.ndarray, 
    embedding2: np.ndarray,
    normalize: bool = True
) -> float:
    """
    Compute cosine similarity between two embedding vectors.
    
    Args:
        embedding1: First embedding vector (numpy array)
        embedding2: Second embedding vector (numpy array)
        normalize: If True, uses normalized dot product (more numerically stable)
    
    Returns:
        Cosine similarity value between -1.0 and 1.0
        - 1.0: identical direction
        - 0.0: orthogonal
        - -1.0: opposite direction
    """
    if embedding1.size == 0 or embedding2.size == 0:
        return 0.0
    
    # Handle mismatched dimensions
    if embedding1.shape[0] != embedding2.shape[0]:
        raise ValueError(f"Dimension mismatch: {embedding1.shape[0]} vs {embedding2.shape[0]}")
    
    if normalize:
        # Normalized dot product (more numerically stable)
        norm1 = np.linalg.norm(embedding1)
        norm2 = np.linalg.norm(embedding2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(np.dot(embedding1, embedding2) / (norm1 * norm2))
    else:
        # Standard formula: (A·B) / (||A|| × ||B||)
        dot_product = np.dot(embedding1, embedding2)
        norm1 = np.linalg.norm(embedding1)
        norm2 = np.linalg.norm(embedding2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(dot_product / (norm1 * norm2))


def summarize(state: ResearchAgentState) -> dict:
    """Summarize the research findings."""
    console.print(Panel.fit("[bold yellow]📝 STAGE: Summary Generation[/bold yellow]", style="yellow"))
    console.print(Rule(style="yellow"))
    console.print(f"\n[bold]Topic:[/bold] {state.topic}")
    console.print(f"[dim]Articles processed:[/dim] {state.nTotalArticlesProcessed}")
    
    context = [
        SystemMessage(content=f"""You are an expert at summarizing research from different individual articles.
        Ignore any articles that are not relevant to the topic.
        Propose the summary in clean markdown code.
        
        Topic: {state.topic}
        
        Summarize the following articles to answer the aforementioned topic: """)
    ]
    
    for i, text in enumerate(state.scrapedData, 1):
        if text.strip():
            context.append(HumanMessage(content=f"[Article {i}]\n{text}"))
        else:
            console.print(f"[yellow]⚠️  Skipping empty article {i}[/yellow]")
    
    llm = get_llm()
    summary = llm.invoke(context)
    
    return {
        "summary": summary.content
    }

def main():
    """Main entry point for the research agent."""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="Research Agent - Conduct web research on any topic"
    )
    parser.add_argument(
        "--topic",
        type=str,
        help="The research topic to investigate"
    )
    
    args = parser.parse_args()
    
    # Determine the research topic from arguments or use default
    if args.topic:
        topic = args.topic
    else:
        console.print(Panel.fit(
            "[bold red]❌ ERROR: No research topic provided![/bold red]",
            style="red"
        ))
        console.print(Rule(style="red"))
        console.print("\n[bold]Usage:[/bold] python research_agent.py --topic \"your research topic\"")
        console.print("\n[bold]Examples:[/bold]")
        console.print("  python research_agent.py --topic \"Latest AI developments\"")
        console.print("  python research_agent.py -q \"Climate change solutions\"")
        console.print("  python research_agent.py --topic \"Quantum computing\" -v")
        console.print("\n[bold]Or use a default topic:[/bold]")
        console.print("  python research_agent.py --topic \"\"  # Will use default topic")
        return
    
    console.print(Panel.fit("[bold white]🚀 RESEARCH AGENT INITIALIZED[/bold white]", style="white"))
    console.print(Rule(style="white"))
    console.print(f"[dim]Model:[/dim] {DEFAULT_MODEL}")
    console.print(f"[dim]Base URL:[/dim] {DEFAULT_LLM_URL}")
    console.print(f"[dim]Timestamp:[/dim] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    console.print(Rule(style="white"))
    
    console.print(f"\n[bold]📝 Research Topic:[/bold] {topic}")
    console.print("\n[bold]Starting research process...[/bold]\n")
    
    # Build the graph
    builder = StateGraph(ResearchAgentState)
    builder.add_node("expand", expand_query)
    builder.add_node("research", research_topic)
    builder.add_node("summarize", summarize)
    builder.add_edge(START, "expand")
    builder.add_edge("expand", "research")
    builder.add_edge("research", "summarize")
    builder.add_edge("summarize", END)
    
    graph = builder.compile()
    
    # Run the research
    response = graph.invoke(
        {
            "topic": topic
        }
    )
    
    console.print(Panel.fit("[bold green]✅ RESEARCH COMPLETE[/bold green]", style="green"))
    console.print(Rule(style="green"))
    console.print(f"\n[bold]Final Summary:[/bold]")
    console.print(Markdown(response['summary']))

if __name__ == "__main__":
    main()