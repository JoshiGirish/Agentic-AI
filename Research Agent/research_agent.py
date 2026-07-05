from time import sleep
from pydantic import BaseModel, Field, SecretStr
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage, SystemMessage
import trafilatura
import requests
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule
from rich.markdown import Markdown

# Configuration
SEARXNG_URL = "http://localhost:8888/search"
DEFAULT_MODEL = "Qwen3.5-9B.Q4_K_M.gguf"
DEFAULT_BASE_URL = "http://localhost:8080/v1"
nQueriesToGenerate = 3
nLinksToSearchPerQuery = 3

# Initialize console for rich output
console = Console()

class ResearchAgentState(BaseModel):
    question: str = Field(
        description="Question from the user"
    )
    queries: list = Field(
        default_factory=list,
        description="list of semantically similar search queries for the question"
    )
    scrapedData: list[str] = Field(
        default_factory=list,
        description="list of content scraped from web for each query"
    )
    summary: str = Field(
        default="",
        description="final summary of the research"
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
        base_url=DEFAULT_BASE_URL,
        reasoning_effort="low",
        api_key=SecretStr("dummy-key"),
        temperature=0.2
    )

def get_llm_with_output() -> ChatOpenAI:
    """Get the LLM with structured output capability."""
    return get_llm().with_structured_output(QueryList)

def expand_query(state: ResearchAgentState) -> dict:
    """Expand the user question into multiple search queries."""
    console.print(Panel.fit("[bold blue]📌 STAGE: Query Expansion[/bold blue]", style="blue"))
    console.print(Rule(style="blue"))
    console.print(f"\n[bold]Original question:[/bold] {state.question}")
    
    # Get current date for context
    current_date = datetime.now().strftime("%B %d, %Y")
    console.print(f"[dim]Current date:[/dim] {current_date}")
    
    llm = get_llm_with_output()
    
    # Include current date in system prompt to prevent outdated references
    sys_msg = SystemMessage(content=f"""
        Current date: {current_date}
        
        Generate at least three semantic search queries for the user's question.
        Each query should be independent and explore different angles.
        IMPORTANT: Use the current date for any time references.
        Return only the structured output.
    """)
    
    messages = [sys_msg, HumanMessage(content=state.question)]
    result = llm.invoke(messages)
    
    console.print("\n[bold cyan]🔍 Generated search queries:[/bold cyan]")
    for i, query in enumerate(result.queries, 1):
        console.print(f"   [{i}] {query}")
    
    return {
        "queries": result.queries
    }

def search_web(query: str) -> str:
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
        for result in results[:nLinksToSearch]:
            url = result["url"]
            console.print(f"[dim]📄 Fetching:[/dim] {url}")
            
            downloaded = trafilatura.fetch_url(url)
            text += str(trafilatura.extract(downloaded))
        
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
        text = search_web(query)
        scraped_data.append(text if text else "")
    
    return {
        "scrapedData": scraped_data
    }

def summarize(state: ResearchAgentState) -> dict:
    """Summarize the research findings."""
    console.print(Panel.fit("[bold yellow]📝 STAGE: Summary Generation[/bold yellow]", style="yellow"))
    console.print(Rule(style="yellow"))
    console.print(f"\n[bold]Question:[/bold] {state.question}")
    console.print(f"[dim]Articles processed:[/dim] {len(state.scrapedData)}")
    
    context = [
        SystemMessage(content=f"""You are an expert at summarizing research from different individual articles.
        Ignore any articles that are not relevant to the question.
        Propose the summary in clean markdown code.
        
        Question: {state.question}
        
        Summarize the following articles to answer the aforementioned question: """)
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
    console.print(Panel.fit("[bold white]🚀 RESEARCH AGENT INITIALIZED[/bold white]", style="white"))
    console.print(Rule(style="white"))
    console.print(f"[dim]Model:[/dim] {DEFAULT_MODEL}")
    console.print(f"[dim]Base URL:[/dim] {DEFAULT_BASE_URL}")
    console.print(f"[dim]Timestamp:[/dim] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    console.print(Rule(style="white"))
    
    question = "Last week news on new tools/processes/operations/architectures for Generative AI developers"
    
    console.print(f"\n[bold]📝 Research Question:[/bold] {question}")
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
            "question": question,
            "queries": [],
            "scrapedData": [],
            "summary": ""
        }
    )
    
    console.print(Panel.fit("[bold green]✅ RESEARCH COMPLETE[/bold green]", style="green"))
    console.print(Rule(style="green"))
    console.print(f"\n[bold]Final Summary:[/bold]")
    console.print(Markdown(response['summary']))

if __name__ == "__main__":
    main()