"""
MAAT MCP Tool Adapter

Routes tool calls to MCP servers.
Swap for native.py or rest.py without touching the kernel.
"""

from __future__ import annotations

import json
from urllib.request import Request, urlopen
from maat_adapters.base import ToolAdapter


class MCPAdapter(ToolAdapter):

    def __init__(self, config: dict):
        super().__init__(config)
        self._servers: list[dict] = config.get("servers", [])
        self._tool_map: dict[str, str] = {}  # tool_name → server_url
        self._refresh_tool_map()

    def _refresh_tool_map(self) -> None:
        for server in self._servers:
            url = server["url"]
            try:
                tools = self.list_tools_for(url)
                for tool in tools:
                    self._tool_map[tool["name"]] = url
            except Exception:
                pass

    def list_tools_for(self, server_url: str) -> list[dict]:
        try:
            req = Request(f"{server_url}/tools", headers={"Accept": "application/json"})
            with urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read())
                return data.get("tools", [])
        except Exception:
            return []

    def list_tools(self) -> list[dict]:
        all_tools = []
        for server in self._servers:
            all_tools.extend(self.list_tools_for(server["url"]))
        return all_tools

    def call(self, tool_name: str, params: dict):
        server_url = self._tool_map.get(tool_name)
        if not server_url:
            # Try all servers
            for server in self._servers:
                server_url = server["url"]
                break
        if not server_url:
            return {"error": f"No server found for tool: {tool_name}"}

        payload = json.dumps({"name": tool_name, "arguments": params}).encode()
        req = Request(
            f"{server_url}/call",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urlopen(req, timeout=30) as resp:
                return json.loads(resp.read())
        except Exception as e:
            return {"error": str(e)}
