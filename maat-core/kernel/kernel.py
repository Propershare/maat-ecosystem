"""
MAAT Kernel

The permanent, boring center of the ecosystem.
Does exactly 8 things. No more.

1. load config
2. enforce policy
3. manage identity
4. manage task lifecycle
5. route memory
6. dispatch tools
7. emit events
8. select runtime adapters

No model-specific logic. No DB-specific logic. No transport-specific logic.
All of that lives in adapters.
"""

from __future__ import annotations

import importlib
import uuid
from datetime import datetime, timezone
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from maat_core.adapters.base import ModelAdapter, MemoryAdapter, ToolAdapter

from maat_core.kernel.policy import PolicyEngine
from maat_core.kernel.events import EventBus
from maat_core.kernel.identity import IdentityStore
from maat_core.kernel.registry import AdapterRegistry


class MaatKernel:
    """
    The MAAT Kernel.

    Instantiate once. Everything talks to this.
    Agents, adapters, apps — all go through the kernel.
    """

    def __init__(self, config: dict):
        self.config = config
        self.session_id = str(uuid.uuid4())

        # Core subsystems
        self.events = EventBus(config.get("events", {}))
        self.policy = PolicyEngine(config.get("policies", []))
        self.identity = IdentityStore(config.get("identity_store", {}))
        self.adapters = AdapterRegistry()

        # Load adapters from config
        self._load_adapters()

        self.emit("kernel.started", {"session_id": self.session_id})

    # ── 1. Config ──────────────────────────────────────────────────

    def get_config(self, key: str, default: Any = None) -> Any:
        """Dot-path config access."""
        parts = key.split(".")
        val = self.config
        for p in parts:
            if isinstance(val, dict):
                val = val.get(p)
            else:
                return default
        return val if val is not None else default

    # ── 2. Policy ──────────────────────────────────────────────────

    def check_policy(self, agent_id: str, action: str, resource: str = "") -> dict:
        """
        Enforce policy before any action.
        Returns: {"allowed": bool, "reason": str, "action": str}
        """
        result = self.policy.evaluate(agent_id=agent_id, action=action, resource=resource)
        self.emit("policy.evaluated", {
            "agent_id": agent_id,
            "action": action,
            "resource": resource,
            "allowed": result["allowed"],
        })
        if not result["allowed"]:
            self.emit("policy.violated", {
                "agent_id": agent_id,
                "action": action,
                "reason": result["reason"],
            }, severity="warning")
        return result

    # ── 3. Identity ────────────────────────────────────────────────

    def get_identity(self, agent_id: str) -> dict | None:
        return self.identity.get(agent_id)

    def register_agent(self, identity: dict) -> str:
        """Register an agent identity. Returns agent_id."""
        agent_id = self.identity.register(identity)
        self.emit("agent.registered", {"agent_id": agent_id, "name": identity.get("name")})
        return agent_id

    # ── 4. Task Lifecycle ──────────────────────────────────────────

    def create_task(self, agent_id: str, title: str, **kwargs) -> dict:
        task = {
            "id": str(uuid.uuid4()),
            "agent_id": agent_id,
            "title": title,
            "status": "pending",
            "priority": kwargs.get("priority", "medium"),
            "loop_mode": kwargs.get("loop_mode", "on-the-loop"),
            "requires_human": kwargs.get("requires_human", False),
            "description": kwargs.get("description", ""),
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        self.emit("task.created", {"task_id": task["id"], "title": title, "agent_id": agent_id})
        return task

    def update_task(self, task: dict, status: str, **kwargs) -> dict:
        task["status"] = status
        if status == "completed":
            task["completed_at"] = datetime.now(timezone.utc).isoformat()
        self.emit(f"task.{status}", {"task_id": task["id"], "agent_id": task["agent_id"]})
        return task

    # ── 5. Memory Routing ──────────────────────────────────────────

    def remember(self, agent_id: str, content: str, memory_class: str = "episodic", **kwargs) -> bool:
        """Write to memory via the configured memory adapter."""
        policy = self.check_policy(agent_id, "memory.write")
        if not policy["allowed"]:
            return False
        adapter = self.adapters.get_memory()
        if not adapter:
            return False
        result = adapter.write({
            "id": str(uuid.uuid4()),
            "agent_id": agent_id,
            "memory_class": memory_class,
            "content": content,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            **kwargs,
        })
        self.emit("memory.written", {"agent_id": agent_id, "memory_class": memory_class})
        return result

    def recall(self, agent_id: str, query: str, memory_class: str | None = None, limit: int = 5) -> list[dict]:
        """Retrieve memory via the configured memory adapter."""
        adapter = self.adapters.get_memory()
        if not adapter:
            return []
        results = adapter.search(query, agent_id=agent_id, memory_class=memory_class, limit=limit)
        self.emit("memory.retrieved", {"agent_id": agent_id, "query": query, "results": len(results)})
        return results

    # ── 6. Tool Dispatch ───────────────────────────────────────────

    def use_tool(self, agent_id: str, tool_name: str, params: dict) -> Any:
        """Dispatch a tool call through policy check → adapter → result."""
        policy = self.check_policy(agent_id, f"tool.{tool_name}")
        if not policy["allowed"]:
            self.emit("tool.denied", {"agent_id": agent_id, "tool": tool_name, "reason": policy["reason"]})
            return {"error": f"Tool denied: {policy['reason']}"}

        adapter = self.adapters.get_tool(tool_name)
        if not adapter:
            return {"error": f"No adapter for tool: {tool_name}"}

        try:
            result = adapter.call(tool_name, params)
            self.emit("tool.called", {"agent_id": agent_id, "tool": tool_name})
            return result
        except Exception as e:
            self.emit("tool.failed", {"agent_id": agent_id, "tool": tool_name, "error": str(e)}, severity="error")
            return {"error": str(e)}

    # ── 7. Event Emission ──────────────────────────────────────────

    def emit(self, event_type: str, payload: dict = None, severity: str = "info") -> None:
        """Emit a MAAT event. Everything important gets evented."""
        self.events.emit({
            "id": str(uuid.uuid4()),
            "type": event_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "session_id": self.session_id,
            "payload": payload or {},
            "severity": severity,
        })

    # ── 8. Adapter Selection ───────────────────────────────────────

    def _load_adapters(self) -> None:
        """Load adapters from config. Swap adapters without touching kernel."""
        adapter_config = self.config.get("adapters", {})

        model_path = adapter_config.get("model", "maat_adapters.models.ollama.OllamaAdapter")
        memory_path = adapter_config.get("memory", "maat_adapters.memory.postgres.PostgresAdapter")
        tool_path = adapter_config.get("tools", "maat_adapters.tools.mcp.MCPAdapter")

        self.adapters.register_model(self._import_adapter(model_path, adapter_config.get("model_config", {})))
        self.adapters.register_memory(self._import_adapter(memory_path, adapter_config.get("memory_config", {})))
        self.adapters.register_tool_adapter(self._import_adapter(tool_path, adapter_config.get("tool_config", {})))

        self.emit("adapter.loaded", {
            "model": model_path,
            "memory": memory_path,
            "tools": tool_path,
        })

    @staticmethod
    def _import_adapter(dotpath: str, config: dict) -> Any:
        """Dynamically import and instantiate an adapter by dotpath."""
        try:
            module_path, class_name = dotpath.rsplit(".", 1)
            module = importlib.import_module(module_path)
            cls = getattr(module, class_name)
            return cls(config)
        except Exception as e:
            print(f"[kernel] Could not load adapter {dotpath}: {e}")
            return None
