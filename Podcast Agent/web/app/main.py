"""Main FastAPI application for the Podcast Conversation Platform."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from datetime import datetime
import os

from app.routes.conversation import router as conversation_router


app = FastAPI(
    title="Agentic AI Podcast Conversation Platform",
    description="A platform for simulating podcast-style conversations between two AI agents",
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", include_in_schema=False)
async def root():
    """Redirect to docs."""
    return RedirectResponse(url="/docs")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


# Serve static files from React build
@app.get("/{full_path:path}")
async def serve_react_app(full_path: str):
    """Serve React app for all non-API routes."""
    if full_path.startswith("api"):
        return RedirectResponse(url=f"/{full_path}")
    
    index_path = os.path.join(os.path.dirname(__file__), "..", "..", "dist", "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    
    return {"error": "React app not found. Run 'npm run build' first."}


app.include_router(conversation_router)
