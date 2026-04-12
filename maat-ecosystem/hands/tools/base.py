"""
MAAT Adapter Base Contracts

All adapters implement these interfaces.
Swap the implementation, keep the interface.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Optional


class ModelAdapter(ABC):
    """Interface for any language model."""

    def __init__(self, config: dict):
        self.config = config

    @abstractmethod
    def generate(self, messages: list[dict], system: str = "", **kwargs) -> str:
        """Generate a response from messages. Returns response text."""

    @abstractmethod
    def embed(self, text: str) -> list[float]:
        """Generate an embedding vector for text."""

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Return the current model identifier."""


class MemoryAdapter(ABC):
    """Interface for any memory backend."""

    def __init__(self, config: dict):
        self.config = config

    @abstractmethod
    def write(self, entry: dict) -> bool:
        """Write a MAAT memory entry. Returns True on success."""

    @abstractmethod
    def search(self, query: str, agent_id: str = "", memory_class: str = None, limit: int = 5) -> list[dict]:
        """Search memory. Returns list of matching entries."""

    @abstractmethod
    def get(self, memory_id: str) -> Optional[dict]:
        """Get a specific memory entry by ID."""

    @abstractmethod
    def delete(self, memory_id: str) -> bool:
        """Delete a memory entry (rollback support)."""


class ToolAdapter(ABC):
    """Interface for any tool transport (MCP, native, REST, etc.)"""

    def __init__(self, config: dict):
        self.config = config

    @abstractmethod
    def call(self, tool_name: str, params: dict) -> Any:
        """Call a tool by name with params. Returns result."""

    @abstractmethod
    def list_tools(self) -> list[dict]:
        """List available tools as MAAT tool contract dicts."""
