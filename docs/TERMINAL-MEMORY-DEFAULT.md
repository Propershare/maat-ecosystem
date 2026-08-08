# Terminal-capable agents — memory default posture

**Audience:** Any agent that can run shell commands, execute tools on the host, or otherwise act with **terminal-level reach** on the user’s machine in this lab.

This document is **design law** for Tehuti Lab: memory and gitMaat are **not** optional add-ons for such agents.

## Policy (clean)

**Terminal access implies Memory MCP + gitMaat context + protective posture by default, unless explicitly disabled by the user.**

## Enforcement (operational)

**No terminal-capable agent should run “memory-blind” on the user’s machine.**

## What must be true in practice

| Expectation | Meaning |
|-------------|---------|
| **Memory MCP** | On first meaningful work (or at session start), **check** Maat Memory MCP reachability (e.g. discovery manifest → `8022`, or `curl` / health). Treat it as **required infrastructure**, not a nice-to-have. |
| **gitMaat / Postgres** | **Check** that durable memory is available: `PGVECTOR_DB_URL` (or equivalent) loaded where scripts run; use `maatlangchain/maat_memory` or Tehuti Core gitMaat tools **per project norms** (see [`GITMAAT-CONNECT.md`](GITMAAT-CONNECT.md)). |
| **Persistent learning context** | Treat gitMaat + file memory (`memory/`, `MEMORY.md` when in main session per [`AGENTS.md`](../AGENTS.md)) as the **authoritative long-term record** for substantive work—not chat history alone. |
| **Document actions** | Log meaningful actions (tasks, changes, decisions, learnings) through the **documented** paths (`log_*`, Archivist discipline, [`SCOUT-ANALYST-ARCHIVIST.md`](SCOUT-ANALYST-ARCHIVIST.md)). |
| **Machine-protective defaults** | Prefer non-destructive commands, confirm risky operations, follow [`AGENTS.md`](../AGENTS.md) Safety and Tehuti Guard when applicable. **Protect the machine first.** |

## If memory is unavailable

**Say so clearly** (e.g. “Memory MCP unreachable” / “gitMaat DB not configured in this shell”). **Do not** imply full context or persistence. **Do not** behave as if “optional wiring” matches lab design—this session may be **misconfigured**, not “fine without memory.”

Distinguish:

- **“This session is not wired to Memory MCP / gitMaat yet”** — accurate when tools or env are missing.
- **“Memory is optional”** — **incorrect** default framing for terminal-capable agents on this machine.

## Relation to Cursor / OpenClaw loops

Physical wiring still passes through **Cursor MCP**, **OpenClaw + mcporter**, and **`.env`**—see [`AGENTS.md`](../AGENTS.md) *Credentials and connection loops* and [`RUNTIME-HOOKUP.md`](RUNTIME-HOOKUP.md). This doc states **intent**: agents must **assume** those connections are **required** for terminal work unless the user has **explicitly** disabled them.

## See also

- [`AGENTS.md`](../AGENTS.md) — workspace home, Safety, Memory, Scout/Analyst/Archivist
- [`GITMAAT-CONNECT.md`](GITMAAT-CONNECT.md) — ports, Bearer, DB URL
- [`RUNTIME-HOOKUP.md`](RUNTIME-HOOKUP.md) — spine check script
- [`LAB-CANONICAL-TREE-AND-STACK.md`](LAB-CANONICAL-TREE-AND-STACK.md) — lab folder tree + tech stack (GitHub / operators)
