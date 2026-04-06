"""
MAAT Adapter Registry

Tracks which adapters are active.
Kernel asks registry; registry holds references.
"""

from __future__ import annotations

from typing import Any, Optional


class AdapterRegistry:
    """Single place to register and retrieve adapters."""

    def __init__(self):
        self._model: Optional[Any] = None
        self._memory: Optional[Any] = None
        self._tools: dict[str, Any] = {}
        self._tool_adapter: Optional[Any] = None

    def register_model(self, adapter: Any) -> None:
        self._model = adapter

    def register_memory(self, adapter: Any) -> None:
        self._memory = adapter

    def register_tool_adapter(self, adapter: Any) -> None:
        self._tool_adapter = adapter

    def get_model(self) -> Optional[Any]:
        return self._model

    def get_memory(self) -> Optional[Any]:
        return self._memory

    def get_tool(self, tool_name: str) -> Optional[Any]:
        """Get tool adapter. Falls back to the general tool adapter."""
        return self._tools.get(tool_name) or self._tool_adapter

    def swap_model(self, adapter: Any) -> None:
        """Hot-swap model adapter without restarting kernel."""
        self._model = adapter

    def swap_memory(self, adapter: Any) -> None:
        """Hot-swap memory backend without restarting kernel."""
        self._memory = adapter
