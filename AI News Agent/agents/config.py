"""Configuration constants for the AI News Multi-Agent System."""

import os

# ============================================================================
# Configuration
# ============================================================================

LLM_URL = os.getenv("LLM_URL", "http://localhost:8080/v1")
LLM_MODEL = os.getenv("LLM_MODEL", "gemma-4-E4b-it.Q4_K_M.gguf")