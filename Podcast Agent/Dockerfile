FROM python:3.11-slim

WORKDIR /app

COPY agents/requirements.txt requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

# Copy all agents files - preserving _agents.py (renamed from agents.py)
COPY agents/__init__.py .
COPY agents/models.py .
COPY agents/_agents.py .
COPY agents/main.py .
COPY agents/routes.py .
COPY agents/execution.py .
COPY agents/orchestrator.py .
COPY agents/services.py .
COPY agents/run.py .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]