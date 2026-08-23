"""Base agent class for the AI News Multi-Agent System."""

from abc import ABC, abstractmethod

from .state import NewsAgentState


class BaseAgent(ABC):
    """Base class for all agents in the system."""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    @abstractmethod
    def process(self, state: NewsAgentState) -> NewsAgentState:
        """Process the state and return updated state."""
        raise NotImplementedError