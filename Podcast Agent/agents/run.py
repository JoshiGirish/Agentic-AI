"""Agent service entry point."""

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "agents.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
