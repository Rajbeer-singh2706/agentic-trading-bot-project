"""Base agent class for all agents."""

from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseAgent(ABC):
    """Abstract base class for all agents."""

    def __init__(self, name: str):
        """Initialize agent.

        Args:
            name: Agent name
        """
        self.name = name
        self.state = "idle"

    @abstractmethod
    def execute(self, **kwargs: Any) -> Dict[str, Any]:
        """Execute agent logic.

        Args:
            **kwargs: Variable arguments

        Returns:
            Execution result
        """

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name}, state={self.state})"
