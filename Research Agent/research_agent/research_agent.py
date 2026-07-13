"""Main entry point for the Research Agent."""

import argparse
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule
from rich.markdown import Markdown
from config import DEFAULT_MODEL, DEFAULT_LLM_URL
from models import ResearchAgentState
from llm import expand_query, research_topic, summarize


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
        console = Console()
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
    
    console = Console()
    console.print(Panel.fit("[bold white]🚀 RESEARCH AGENT INITIALIZED[/bold white]", style="white"))
    console.print(Rule(style="white"))
    console.print(f"[dim]Model:[/dim] {DEFAULT_MODEL}")
    console.print(f"[dim]Base URL:[/dim] {DEFAULT_LLM_URL}")
    console.print(f"[dim]Timestamp:[/dim] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    console.print(Rule(style="white"))
    
    console.print(f"\n[bold]📝 Research Topic:[/bold] {topic}")
    console.print("\n[bold]Starting research process...[/bold]\n")
    
    # Build the graph
    from langgraph.graph import StateGraph, START, END
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