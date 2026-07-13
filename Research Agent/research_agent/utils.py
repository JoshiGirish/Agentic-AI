"""Utility functions for the Research Agent."""

import json
import requests
import numpy as np
from typing import Optional
from config import DEFAULT_MODEL, DEFAULT_LLM_URL, DEFAULT_EMBED_URL, nQueriesToGenerate


def get_llm():
    """Get the LLM instance with proper error handling."""
    from langchain_openai import ChatOpenAI
    from pydantic import SecretStr
    
    return ChatOpenAI(
        model=DEFAULT_MODEL,
        base_url=DEFAULT_LLM_URL,
        reasoning_effort="low",
        api_key=SecretStr("dummy-key"),
        temperature=0.2
    )


def get_llm_with_output():
    """Get the LLM with structured output capability."""
    from langchain_openai import ChatOpenAI
    from langchain_core.messages import SystemMessage, HumanMessage
    from pydantic import BaseModel, Field
    
    llm = get_llm()
    
    class QueryList(BaseModel):
        """Model for query list output."""
        queries: list[str] = Field(
            min_length=nQueriesToGenerate,
            description="Three or more independent search engine queries."
        )
    
    return llm.with_structured_output(QueryList)


def generate_embedding(
    input_text: str, 
    model: str = "nomic-embed-text", 
    base_url: str = DEFAULT_EMBED_URL
) -> Optional[np.ndarray]:
    """
    Generate embeddings for input text using a remote embedding model.
    
    Args:
        input_text: The text to generate embeddings for
        model: The model name to use (default: "nomic-embed-text")
        base_url: The base URL of the embedding service (default: "http://localhost:8081/v1/embeddings")
    
    Returns:
        A numpy array representing the embedding vector, or None if an error occurs
    """
    try:
        # Prepare the JSON payload
        payload = {
            "input": input_text,
            "model": model
        }
        
        # Create connection
        response = requests.post(
            base_url,
            json=payload,
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json"
            },
            timeout=30
        )
        
        # Check response status
        if response.status_code >= 200 and response.status_code < 300:
            # Parse the JSON response
            try:
                json_response = response.json()
                
                # Extract embedding from the response
                if "data" in json_response:
                    data = json_response["data"]
                    if data and len(data) > 0:
                        embedding = data[0].get("embedding", [])
                        if embedding:
                            # Return as numpy array for efficient computation
                            return np.array(embedding, dtype=np.float32)
            except json.JSONDecodeError:
                pass
            
            # Return empty array if no embedding found
            return np.array([], dtype=np.float32)
        else:
            # Print error response if available
            error_response = response.text
            if error_response:
                print(f"Error response (status {response.status_code}): {error_response}")
            
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Network error: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None


def cosine_similarity(
    embedding1: np.ndarray, 
    embedding2: np.ndarray,
    normalize: bool = True
) -> float:
    """
    Compute cosine similarity between two embedding vectors.
    
    Args:
        embedding1: First embedding vector (numpy array)
        embedding2: Second embedding vector (numpy array)
        normalize: If True, uses normalized dot product (more numerically stable)
    
    Returns:
        Cosine similarity value between -1.0 and 1.0
        - 1.0: identical direction
        - 0.0: orthogonal
        - -1.0: opposite direction
    """
    if embedding1.size == 0 or embedding2.size == 0:
        return 0.0
    
    # Handle mismatched dimensions
    if embedding1.shape[0] != embedding2.shape[0]:
        raise ValueError(f"Dimension mismatch: {embedding1.shape[0]} vs {embedding2.shape[0]}")
    
    if normalize:
        # Normalized dot product (more numerically stable)
        norm1 = np.linalg.norm(embedding1)
        norm2 = np.linalg.norm(embedding2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(np.dot(embedding1, embedding2) / (norm1 * norm2))
    else:
        # Standard formula: (A·B) / (||A|| × ||B||)
        dot_product = np.dot(embedding1, embedding2)
        norm1 = np.linalg.norm(embedding1)
        norm2 = np.linalg.norm(embedding2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(dot_product / (norm1 * norm2))