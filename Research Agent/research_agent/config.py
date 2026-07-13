"""Configuration constants for the Research Agent."""

# SearXNG API endpoint
SEARXNG_URL = "http://searxng:8080/search"

# Default LLM model
DEFAULT_MODEL = "Qwen3.5-9B.Q4_K_M.gguf"

# Default LLM endpoint
DEFAULT_LLM_URL = "http://localhost:8080/v1"

# Default embedding endpoint
DEFAULT_EMBED_URL = "http://localhost:8081/v1/embeddings"

# Configuration parameters
nQueriesToGenerate = 3
nLinksToSearchPerQuery = 3
relevanceThreshold = 0.60