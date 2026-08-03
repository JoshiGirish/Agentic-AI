"""LLM utilities for the AI News Multi-Agent System."""

import os
from typing import Optional, List, Dict, Any
from datetime import datetime
import json

# ============================================================================
# Configuration
# ============================================================================

DEFAULT_LLM_URL = os.getenv("LLM_URL", "http://localhost:8080/v1/chat")


# ============================================================================
# LLM Client
# ============================================================================

class LLMClient:
    """
    Client for interacting with local LLM services.

    Supports:
    - Ollama (default)
    - Any OpenAI-compatible API
    """

    def __init__(
        self,
        url: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.2,
        max_tokens: Optional[int] = None,
    ):
        self.url = url or DEFAULT_LLM_URL
        self.model = model or os.getenv("LLM_MODEL", "llama3.2")
        self.temperature = temperature
        self.max_tokens = max_tokens or int(os.getenv("MAX_TOKENS", "500"))

    def invoke(
        self,
        messages: List[Dict[str, str]],
        stream: bool = False,
    ) -> Any:
        """
        Invoke the LLM with a list of messages.

        Args:
            messages: List of message dictionaries with 'role' and 'content'
            stream: Whether to stream the response

        Returns:
            LLM response object
        """
        import requests

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
        }

        if self.max_tokens:
            payload["max_tokens"] = self.max_tokens

        try:
            response = requests.post(
                self.url,
                json=payload,
                timeout=120,
                headers={"Content-Type": "application/json"},
            )

            response.raise_for_status()

            # Parse response
            data = response.json()

            # Ollama response format
            if "message" in data:
                content = data["message"]["content"]
            elif "choices" in data:
                content = data["choices"][0]["message"]["content"]
            else:
                content = str(data)

            return type("Response", (), {"content": content})()

        except requests.exceptions.RequestException as e:
            print(f"LLM request failed: {e}")
            return None

    def chat(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
    ) -> str:
        """
        Simple chat interface.

        Args:
            prompt: User message
            system_prompt: System instruction

        Returns:
            LLM response
        """
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        response = self.invoke(messages)

        if response:
            return response.content
        return ""


# ============================================================================
# Summary Templates
# ============================================================================

SUMMARY_TEMPLATES = {
    "brief": """
    BRIEF SUMMARY
    ==============

    {summary}

    Key Points:
    - {key_point_1}
    - {key_point_2}
    """,

    "detailed": """
    DETAILED SUMMARY
    ================

    Source: {source}
    Date: {date}
    Category: {category}

    SUMMARY:
    {summary}

    KEY INSIGHTS:
    {insights}
    """,

    "json": """
    {{
    "title": "{title}",
    "source": "{source}",
    "date": "{date}",
    "summary": "{summary}",
    "key_points": [
        "{key_point_1}",
        "{key_point_2}",
        "{key_point_3}"
    ]
    }}
    """,
}


# ============================================================================
# Utility Functions
# ============================================================================

def truncate_text(text: str, max_length: int = 500) -> str:
    """Truncate text to maximum length with ellipsis."""
    if len(text) <= max_length:
        return text
    return text[: max_length - 3] + "..."


def format_timestamp() -> str:
    """Get current timestamp in ISO format."""
    return datetime.now().isoformat()


def extract_key_points(text: str, max_points: int = 3) -> List[str]:
    """
    Extract key points from text using simple heuristics.

    Args:
        text: Input text
        max_points: Maximum number of key points to extract

    Returns:
        List of key point strings
    """
    import re

    # Split into sentences
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]

    if not sentences:
        return []

    # Score sentences by length and punctuation (questions/statements are more likely to be key points)
    scored = []
    for sentence in sentences:
        score = len(sentence)
        if '?' in sentence or '!' in sentence:
            score += 10
        if any(punct in sentence for punct in ['"', "'", ':']):
            score += 5
        scored.append((score, sentence))

    # Sort by score and take top points
    scored.sort(reverse=True)
    return [s[1] for s in scored[:max_points]]


def create_summary_metadata(
    title: str,
    source: str,
    date: Optional[str] = None,
    category: str = "General",
) -> Dict[str, Any]:
    """
    Create metadata for a summary.

    Args:
        title: Article title
        source: Source URL
        date: Publication date (defaults to current date)
        category: Article category

    Returns:
        Metadata dictionary
    """
    if not date:
        date = format_timestamp()

    return {
        "title": title,
        "source": source,
        "date": date,
        "category": category,
    }