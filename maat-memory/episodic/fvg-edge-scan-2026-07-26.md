# Episodic Memory — 2026-07-26
timestamp: 2026-07-26T13:04:24.391045+00:00
source: hermes-agent

2026-07-26 — Corrected lab brain bridge architecture. Initial approach was wrong: added @method('maat.artifacts.list') to Hermes backend (only works in desktop app on one machine). Corrected approach: added maat_memory_read_artifacts and maat_memory_write_artifact tools to maat_memory_mcp.py — the shared MCP server every agent already has configured. Verified both tools work against live Postgres. Updated semantic memory with corrected architecture. Key lesson: always build at the MCP layer for cross-agent tools, not the Hermes backend layer.
