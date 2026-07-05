# Research Agent: Automated Web Research and Synthesis Agent

This project implements a multi-stage research agent built using LangGraph. The agent automates the process of answering complex questions by systematically expanding the query, gathering information from the web via multiple search queries, and synthesizing the gathered data into a final, coherent summary.

![Research Agent Diagram](Research_agent.png)

## 🚀 Overview

The `research_agent.py` script orchestrates a research workflow that mimics a junior researcher's process:
1.  **Query Expansion:** Takes a single user question and generates several semantically diverse search queries.
2.  **Web Research:** Executes web searches using SearXNG and scrapes the main content from the top results for each query.
3.  **Synthesis:** Passes all scraped content to a Large Language Model (LLM) to generate a final, structured summary answering the original question.

## 🛠️ Prerequisites & Setup

Before running the agent, ensure the following dependencies and services are running:

### 1. Python Dependencies
Install the required Python libraries:
```bash
pip install langchain-openai pydantic trafilatura requests rich langgraph
```

### 2. External Services
The agent relies on two external services:
*   **LLM Endpoint:** An accessible LLM endpoint (e.g., a local Ollama or OpenAI proxy) configured at `http://localhost:8080/v1`.
*   **Search Engine:** A running SearXNG instance accessible at `http://localhost:8888/search`.

### 3. Environment Variables & Configuration
The script uses hardcoded defaults, but for production use, consider setting environment variables for:
*   **LLM API Key:** The `api_key` for the LLM provider (currently mocked as `"dummy-key"`).
*   **LLM Base URL:** The base URL for the LLM API (`DEFAULT_BASE_URL`).

## ⚙️ Architecture Deep Dive (LangGraph Workflow)

The agent's logic is encapsulated within a `StateGraph` graph, defining a clear, sequential workflow:

**State:** `ResearchAgentState`
This class manages the entire state of the research process, holding the original `question`, the list of generated `queries`, the `scrapedData` from the web, and the final `summary`.

**Nodes (Stages):**

1.  **`expand_query` (Query Expansion):**
    *   **Input:** `ResearchAgentState` containing the user's question.
    *   **Process:** Calls an LLM to generate a list of at least three independent, semantically rich search queries. It also incorporates the current date into the system prompt to ensure temporal relevance.
    *   **Output:** Updates the state with the list of `queries`.

2.  **`research_topic` (Web Research):**
    *   **Input:** `ResearchAgentState` containing the list of `queries`.
    *   **Process:** Iterates through each query. For each query, it calls the `search_web` function, which:
        *   Queries SearXNG for search results.
        *   Fetches the content of the top links using `trafilatura`.
        *   Aggregates all extracted text into a list of scraped data.
    *   **Output:** Updates the state with `scrapedData` (a list of strings, one for each query).

3.  **`summarize` (Summary Generation):**
    *   **Input:** `ResearchAgentState` containing the `scrapedData`.
    *   **Process:** Constructs a detailed prompt containing the original question and all scraped articles. It invokes the LLM one final time to synthesize a comprehensive summary.
    *   **Output:** Updates the state with the final `summary` string.

**Graph Flow:**
`START` $\rightarrow$ `expand` $\rightarrow$ `research` $\rightarrow$ `summarize` $\rightarrow$ `END`

## ▶️ How to Run

1.  Ensure all prerequisites are installed and external services are running.
2.  Execute the main function:

```bash
python research_agent.py
```

The agent will print its progress to the console, showing the execution of each stage (Query Expansion, Web Research, Summary Generation). The final summary will be displayed using Markdown formatting.
