"""LLM-related functionality for the Research Agent."""

from models import ResearchAgentState
from utils import get_llm, get_llm_with_output
from search import search_web
from rich.rule import Rule
from langchain_core.messages import HumanMessage


def expand_query(state: ResearchAgentState) -> dict:
    """Expand the user topic into multiple search queries."""
    from rich.console import Console
    from rich.panel import Panel
    from rich.rule import Rule
    from langchain_core.messages import SystemMessage, HumanMessage
    
    console = Console()
    
    console.print(Panel.fit("[bold blue]📌 STAGE: Query Expansion[/bold blue]", style="blue"))
    console.print(Rule(style="blue"))
    console.print(f"\n[bold]Original topic:[/bold] {state.topic}")
    
    # Get current date for context
    from datetime import datetime
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


def research_topic(state: ResearchAgentState) -> dict:
    """Research the topic using multiple search queries."""
    from rich.console import Console
    from rich.panel import Panel
    from rich.rule import Rule
    
    console = Console()
    
    console.print(Panel.fit("[bold magenta]🔬 STAGE: Web Research[/bold magenta]", style="magenta"))
    console.print(Rule(style="magenta"))
    
    scraped_data = []
    nArticleCount = 0
    for i, query in enumerate(state.queries, 1):
        console.print(f"\n[dim]Query {i}/{len(state.queries)}:[/dim] {query}")
        search_result = search_web(query, state)
        scraped_data.append(search_result["text"] if search_result["text"] else "")
        nArticleCount += search_result["nArticles"]
    
    return {
        "scrapedData": scraped_data,
        "nTotalArticlesProcessed": nArticleCount
    }


def summarize(state: ResearchAgentState) -> dict:
    """Summarize the research findings."""
    from rich.console import Console
    from rich.panel import Panel
    from rich.markdown import Markdown
    from langchain_core.messages import SystemMessage, HumanMessage
    
    console = Console()
    
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