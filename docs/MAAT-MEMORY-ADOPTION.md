# Maat Memory Adoption Guide

**Maat Memory** is a **shared organ** (not a per-repo copy). Central brain: Postgres/pgvector + MCP on **`:8022`**. Every build gets a **thin client**, not the full `maatlangchain/maat_memory` backend.

## Quick start (any build)

```bash
pip install ./maat-memory-client   # from lab root, or git URL when published
maat-memory-client doctor          # auto-discovers endpoint + agent id
```

```python
from maat_memory_client import MaatMemoryClient

memory = MaatMemoryClient()   # zero manual config
memory.remember("Operator prefers concise answers.", tags=["preference"])
hits = memory.recall("operator preferences")
memory.log_task("Fix Guard wiring", "Wire systemd units for :8013", status="pending")
```

No `sys.path.insert(...)` required.

## Self-setup (what the client resolves)

| Setting | Resolution order |
|---------|------------------|
| Endpoint | `MAAT_MEMORY_URL` / `MAAT_MEMORY_MCP_BASE` → Ka `:8010/manifest` `organs.memory.endpoint` → `http://127.0.0.1:8022` |
| Agent id | `MAAT_AGENT_ID` → `cursor_<hostname>` (or prefix via constructor) |
| Auth | `MAAT_MEMORY_API_KEY`, `MCPO_API_KEY`, or `KA_API_KEY` (Bearer) |
| Strict mode | Default **off** — unreachable service logs warning, does not crash host build |

## Wire contract

All HTTP calls use mcpo `POST /{tool_name}`. See [MAAT-MEMORY-WIRE-CONTRACT.md](MAAT-MEMORY-WIRE-CONTRACT.md).

Client ergonomics map to tools:

- `remember()` → `memory_log_learning`
- `recall()` / `search()` → `memory_search`
- `log_task()` → `memory_log_task`
- `log_decision()` → `memory_log_decision`
- `health()` → `memory_health`

## When to use direct `maat_memory` import

Use **`from maat_memory import MaatMemory`** only when:

- running inside the lab monorepo with `maatlangchain` on `PYTHONPATH`, and
- you are the MCP server, migration scripts, or backend maintenance.

**All other builds** (OpenClaw hooks, standalone repos, CI, agents on other machines) should use **`maat-memory-client`**.

## Environment variables (portable backend)

| Variable | Purpose |
|----------|---------|
| `PGVECTOR_DB_URL` | Postgres backend (server-side / direct import) |
| `MAAT_MEMORY_URL` | Client HTTP base (no trailing slash) |
| `MAAT_AGENT_ID` | Override auto agent id |
| `MAAT_MEMORY_JSON_PATH` | JSON fallback file path |
| `MAAT_MEMORY_BACKUP_DIR` | JSON backup directory |
| `MAAT_WORKSPACE_ROOT` | Lab root when autodetect fails |
| `MAAT_MEMORY_ALLOW_JSON` | Set `1` to allow local JSON when `PGVECTOR_DB_URL` is unset (lab default: refuse — split-brain risk) |
| `MAAT_MEMORY_REQUIRE_POSTGRES` | Set `1` to always refuse JSON even outside detected lab workspace |

## Product boundary

- **Free / open:** client + wire contract + local templates
- **Hosted / paid (future):** managed `:8022`, audit retention, dashboards, policy packs, fleet correlation

Maat Memory is **not** Tehuti Guard and **not** a separate "Tehuti Memory" product.

## Related

- [GITMAAT-CONNECT.md](GITMAAT-CONNECT.md)
- [maat-memory-client/README.md](../maat-memory-client/README.md)
- [GUARD-ADOPTION.md](GUARD-ADOPTION.md) — separate governance organ
