"""Main FastAPI application for the Agent service."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime

from routes import router as agent_router


app = FastAPI(
    title="Agentic AI Podcast Agent Service",
    description="Agent service for podcast conversation orchestration",
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


app.include_router(agent_router)
