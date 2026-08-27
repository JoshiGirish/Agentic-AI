# Agentic AI Podcast Conversation Platform

## Project Structure

```
Agentic-AI/
├── web/                    # FastAPI + React frontend
│   ├── app/               # FastAPI backend
│   │   ├── __init__.py
│   │   ├── main.py        # FastAPI app entry point
│   │   ├── routes/        # API routes
│   │   ├── schemas/       # Pydantic models
│   │   └── services/      # Business logic
│   ├── src/               # React frontend
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── pages/
│   │   ├── types/
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── public/
│   ├── Dockerfile
│   └── requirements.txt
├── agents/                # LangGraph agents
│   ├── __init__.py
│   ├── models.py          # Pydantic models
│   ├── agents.py          # Agent implementations
│   ├── orchestrator.py    # Conversation orchestrator
│   ├── Dockerfile
│   └── requirements.txt
├── docker-compose.yml
└── README.md
```
