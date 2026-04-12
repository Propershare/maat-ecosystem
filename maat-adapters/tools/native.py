"""
MAAT Native Tool Adapter

Register Python functions as tools directly.
No network. No MCP. Just functions.

Use for: built-in tools that should always be available
regardless of which MCP servers are running.
"""

from __future__ import annotations

from typing import Any, Callable
from maat_adapters.base import ToolAdapter


class NativeAdapter(ToolAdapter):
    """Register Python callables as MAAT tools."""

    def __init__(self, config: dict = None):
        super().__init__(config or {})
        self._tools: dict[str, dict] = {}  # name → {fn, schema}

    def register(self, name: str, fn: Callable, description: str = "",
                 required_ring: str = "outer-ring", reversible: bool = True) -> None:
        """Register a Python function as a tool."""
        self._tools[name] = {
            "id": name,
            "name": name,
            "description": description or fn.__doc__ or "",
            "required_ring": required_ring,
            "reversible": reversible,
            "fn": fn,
        }

    def call(self, tool_name: str, params: dict) -> Any:
        tool = self._tools.get(tool_name)
        if not tool:
            return {"error": f"Unknown native tool: {tool_name}"}
        try:
            return tool["fn"](**params)
        except Exception as e:
            return {"error": str(e)}

    def list_tools(self) -> list[dict]:
        return [{k: v for k, v in t.items() if k != "fn"} for t in self._tools.values()]
