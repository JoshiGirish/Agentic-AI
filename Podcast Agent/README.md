# Agentic AI Podcast Conversation Platform

A containerized web application that simulates podcast-style conversations between two AI agents with distinct personalities.

## Features

- 🎙️ Two-agent conversation with distinct roles (Host & Guest / Skeptic & Enthusiast)
- 🔄 Real-time token-level streaming via Server-Sent Events (SSE)
- 🎨 Modern React + TypeScript web client
- 🐳 Fully containerized with Docker Compose
- 🤖 LangGraph-based agent orchestration
- 📊 OpenAI-compatible LLM support (Ollama, vLLM, etc.)

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    User Browser (React)                      │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ HTTP + SSE
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                  Web Service (FastAPI)                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   /topic     │  │  /stream     │  │  /history    │      │
│  │   POST       │  │   SSE        │  │   GET        │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ API Calls
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                 Agent Service (LangGraph)                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Host Agent │  │ Guest Agent  │  │ Orchestrator │      │
│  │   (LLM)      │  │  (LLM)       │  │  (LangGraph) │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.11+ (for local development)
- An OpenAI-compatible LLM API (e.g., Ollama running on port 8080)

### Running with Docker

```bash
# Start all services
docker-compose up --build

# Access the web client
# http://localhost:3000
```

### Running Locally (Development)

```bash
# Start Redis
docker run -d -p 6379:6379 --name redis valkey/valkey:8-alpine

# Start the agent service
cd agents
pip install -r requirements.txt
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Start the web service
cd web
npm install
npm run dev
```

## Conversation Modes

### Host & Guest
- **Host**: Guides conversation, asks questions, encourages insights
- **Guest**: Provides expertise, answers questions, shares knowledge

### Skeptic & Enthusiast
- **Skeptic**: Questions claims, seeks evidence, explores counterarguments
- **Enthusiast**: Supports ideas, explains benefits, builds enthusiasm

## API Endpoints

### Start Conversation
```bash
curl -X POST http://localhost:8000/api/v1/conversation \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "The future of quantum computing",
    "role_mode": "host_guest",
    "max_turns": 20
  }'
```

### Stream Conversation (SSE)
```bash
curl -N http://localhost:8000/api/v1/stream/{conversation_id}
```

### Get Conversation Status
```bash
curl http://localhost:8000/api/v1/conversation/{conversation_id}
```

### Stop Conversation
```bash
curl -X DELETE http://localhost:8000/api/v1/conversation/{conversation_id}
```

## Project Structure

```
Podcast Agent/            # Podcast creation and management agent
   ├── Dockerfile           # Docker configuration for the agent
   ├── README.md            # Agent-specific documentation
   ├── PROJECT_STRUCTURE.md # Detailed internal structure
   ├── requirements.txt     # Python dependencies
   ├── agents/              # Agent implementation module
   │   ├── _agents.py       # Agent definitions and configurations
   │   ├── execution.py     # Agent execution logic
   │   ├── main.py          # Entry point for agents
   │   ├── models.py        # Agent models and data structures
   │   ├── orchestrator.py  # Agent orchestration logic
   │   ├── routes.py        # API routes for agent services
   │   ├── services.py      # Agent services and utilities
   │   └── [other files]    # Additional agent utilities
   ├── docker-compose.yml   # Docker Compose configuration
   └── web/                 # Web interface for the agent
       ├── app/            # Application layer
       │   ├── main.py     # Application entry point
       │   ├── routes/     # HTTP routes
       │   ├── schemas/    # Data schemas
       │   └── services/   # Business logic services
       ├── src/            # React/TypeScript frontend
       │   ├── components/ # UI components
       │   ├── pages/      # Page components
       │   └── lib/        # Utilities and config
       └── [build files]   # Compiled assets


## Configuration

### Environment Variables

#### Agent Service
- `LLM_URL`: URL of the OpenAI-compatible LLM API (default: `http://localhost:8080/v1`)

#### Web Service
- `AGENTS_URL`: URL of the agent service (default: `http://agents:8000`)

### LLM Models

The application is configured to use `gemma-4-E4b-it.Q4_K_M.gguf` by default. You can change this in:

- `agents/agents.py` - Agent system prompts
- `agents/orchestrator.py` - LangGraph orchestrator

## Streaming

The application uses Server-Sent Events (SSE) for real-time streaming of agent responses. Each token is streamed as it's generated, providing a near real-time conversation experience.

### SSE Event Format

```
event: message
data: {"agent": "host", "content": "Welcome to today's episode...", "token_index": 0}

event: complete
data: {"conversation_id": "abc123", "turn_count": 20, "is_complete": true}
```
