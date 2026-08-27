# Agentic AI Podcast Platform

## Agent Service

### Project Structure

```
agents/
├── __init__.py
├── models.py            # Pydantic models
├── agents.py            # Agent implementations
├── orchestrator.py      # LangGraph orchestrator
├── execution.py         # Agent execution
├── routes.py            # API routes
├── main.py              # FastAPI app entry point
├── Dockerfile
└── requirements.txt
```

### Agent Roles

1. **Host Agent**: Guides conversation, asks questions
2. **Guest Agent**: Provides expertise, answers questions
3. **Skeptic Agent**: Questions claims, seeks evidence
4. **Enthusiast Agent**: Supports ideas, explains benefits

### Running

```bash
cd agents
pip install -r requirements.txt
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```
