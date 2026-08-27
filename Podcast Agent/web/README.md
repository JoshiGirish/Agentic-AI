# Agentic AI Podcast Platform

## FastAPI Application

### Project Structure

```
web/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI app entry point
│   ├── routes/
│   │   └── conversation.py
│   └── services/
│       ├── agent_orchestrator.py
│       ├── streaming.py
│       └── agent_execution.py
├── Dockerfile
├── requirements.txt
├── package.json
├── tsconfig.json
├── vite.config.ts
└── index.html
```

### API Endpoints

- `POST /api/v1/conversation` - Start new conversation
- `GET /api/v1/stream/{conversation_id}` - SSE streaming
- `GET /api/v1/conversation/{id}` - Get conversation status
- `DELETE /api/v1/conversation/{id}` - Stop conversation

### Running

```bash
cd web
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
