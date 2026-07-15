from models import ResearchAgentState
from utils import get_llm, get_llm_with_output
from search import search_web

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
    
    You are an expert research assistant tasked with generating diverse search queries.
    
    Task: Generate at least three semantic search queries for the user's research topic.
    
    Guidelines:
    1. Each query should explore a different angle or aspect of the topic
    2. Queries should be independent but complementary
    3. Include various perspectives: foundational concepts, recent developments, applications, controversies, methodologies
    4. Use the current date for any time references
    5. Queries should be concise, specific, and suitable for semantic search
    
    Expected output format:
    Return a dictionary with a "queries" key containing a list of query strings.
    
    Example output:
    {{"queries": ["query 1", "query 2", "query 3"]}}
    
    Topic: {state.topic}
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
    
    scraped_data = []
    nArticleCount = 0
    if state.doPerQueryCompression:
        if state.nQueriesProcessed >= len(state.queries):
            return {
                "nQueriesProcessed": state.nQueriesProcessed + 1
            }
        else:        
            console.print(Panel.fit("[bold magenta]🔬 STAGE: Web Research[/bold magenta]", style="magenta"))
            console.print(Rule(style="magenta"))
            query = state.queries[state.nQueriesProcessed]
            console.print(f"\n[dim]Processing query {state.nQueriesProcessed + 1}/{len(state.queries)}:[/dim]")
            console.print(f"[dim]Query:[/dim] {query}")
            search_result = search_web(query, state)
            console.print(f"[dim]Articles found:[/dim] {search_result['nArticles']}")
            return {
                "queryCacheForCompression": search_result["text"],
                "nTotalArticlesProcessed": state.nTotalArticlesProcessed + search_result["nArticles"],
                "nQueriesProcessed": state.nQueriesProcessed + 1
            }
    else:
        for i, query in enumerate(state.queries, 1):
            console.print(f"\n[dim]Query {i}/{len(state.queries)}:[/dim] {query}")
            search_result = search_web(query, state)
            scraped_data.append(search_result["text"] if search_result["text"] else "")
            nArticleCount += search_result["nArticles"]
    
    return {
        "scrapedData": scraped_data,
        "nTotalArticlesProcessed": nArticleCount
    }
    
def compress(state: ResearchAgentState) -> dict:
    from rich.console import Console
    from langchain_core.messages import SystemMessage, HumanMessage
    
    console = Console()
    console.print(f"[dim]Compressing results from query:[/dim] {state.queries[state.nQueriesProcessed-1]}")
    
    # Calculate initial token count (approximate based on character count)
    initial_tokens = len(state.queryCacheForCompression) // 4  # Rough estimate: 4 chars per token
    
    context = [
        SystemMessage(content=f"""You are an expert at summarizing large text and articles into concise, relevant, and meaningful summaries.
        The proposed summary must be in clean markdown code.
        
        Topic: {state.topic}
        
        Summarize the following article to keep only the relevant information required to answer the aforementioned topic:
        
        Guidelines:
        1. Identify key points, findings, and conclusions
        2. Preserve important data, statistics, and citations
        3. Remove redundant information and tangential details
        4. Use clear, concise language
        5. Format output as clean markdown with appropriate headings
        6. Aim for 150-300 words unless the content is exceptionally dense
        
        Article content:
        """)
    ]
    querySummary = ""
    if state.queryCacheForCompression.strip():
        context.append(HumanMessage(content=state.queryCacheForCompression))
        llm = get_llm()
        querySummary = llm.invoke(context)
        
        # Calculate compressed token count
        compressed_tokens = len(querySummary.content) // 4
        
        # Calculate compression ratio
        compression_ratio = ((initial_tokens - compressed_tokens) / initial_tokens * 100) if initial_tokens > 0 else 0
        
        console.print(f"\n[dim]Compression statistics:[/dim]")
        console.print(f"   Initial tokens (approx): {initial_tokens:,}")
        console.print(f"   Compressed tokens (approx): {compressed_tokens:,}")
        console.print(f"   Compression: {compression_ratio:.1f}%")
    else:
        console.print(f"[yellow]⚠️  Skipping article compression for empty results [/yellow]")
    
    return {
        "scrapedData": state.scrapedData + [querySummary.content]
    }

def should_compress(state: ResearchAgentState) -> str:
    if state.doPerQueryCompression and state.nQueriesProcessed <= len(state.queries):
        return "compress"
    else:
        return "summarize"

def summarize(state: ResearchAgentState) -> dict:
    """Summarize the research findings."""
    from rich.console import Console
    from rich.panel import Panel
    from rich.rule import Rule
    from rich.markdown import Markdown
    from langchain_core.messages import SystemMessage, HumanMessage
    
    console = Console()
    
    console.print(Panel.fit("[bold yellow]📝 STAGE: Summary Generation[/bold yellow]", style="yellow"))
    console.print(Rule(style="yellow"))
    console.print(f"\n[bold]Topic:[/bold] {state.topic}")
    console.print(f"[dim]Articles processed:[/dim] {state.nTotalArticlesProcessed}")
    
    context = [
        SystemMessage(content=f"""You are an expert at synthesizing research from multiple articles into a cohesive summary.
        Ignore any articles that are not relevant to the topic.
        Propose a comprehensive summary in clean markdown code.
        
        Topic: {state.topic}
        
        Guidelines for the summary:
        1. Synthesize key findings across all articles
        2. Identify consensus and conflicting viewpoints
        3. Highlight important methodologies and results
        4. Structure with clear markdown headings and bullet points
        5. Aim for 300-600 words of comprehensive coverage
        6. Include a brief conclusion with key takeaways
        
        Articles to summarize:
        """)
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