# Maat Memory Wire Contract

**Status:** Canonical v1 (mcpo hybrid)  
**Contract version:** `1`  
**Purpose:** One network surface for all builds that call Maat Memory.

Maat Memory is a **shared organ**: central Postgres/pgvector backend + HTTP MCP on **`:8022`**. Builds must not invent per-repo wire shapes. Client libraries may expose ergonomic methods (`remember`, `recall`) but must map to the tools below.

## Transport

| Item | Value |
|------|--------|
| Default base URL | `http://127.0.0.1:8022` |
| Env override | `MAAT_MEMORY_URL` or `MAAT_MEMORY_MCP_BASE` |
| HTTP method | `POST /{tool_name}` |
| Content-Type | `application/json` |
| Body | JSON object = tool arguments |
| Auth (optional) | `Authorization: Bearer <key>` from `MAAT_MEMORY_API_KEY`, `MCPO_API_KEY`, or `KA_API_KEY` |

When mcpo is started with `--api-key`, clients **must** supply a bearer token. The `maat-memory-client` reads keys from environment or workspace `.env` files automatically.

Server stack: FastMCP (`maat_memory_server.py`) wrapped by **mcpo** (see `maat-ecosystem/mcp-servers/maat-memory/start_maat_memory.sh`).

## Discovery

Ka discovery manifest lists the memory organ:

```text
GET http://<host>:8010/manifest
→ organs.memory.endpoint  (port 8022)
```

Clients should resolve endpoint in order:

1. `MAAT_MEMORY_URL` / `MAAT_MEMORY_MCP_BASE`
2. Ka discovery `organs.memory.endpoint`
3. `http://127.0.0.1:8022`

## Tool catalog

### Store (write)

| Tool | Required args | Notes |
|------|---------------|--------|
| `memory_log_conversation` | `agent`, `role`, `content` | Optional: `session_id`, `metadata_json` |
| `memory_log_task` | `agent`, `title`, `description` | Optional: `status`, `priority`, `related_files_json` |
| `memory_log_decision` | `agent`, `context`, `decision_made`, `rationale` | Optional: `options_considered_json` |
| `memory_log_change` | `agent`, `file_path`, `change_type`, `summary`, `reason` | Optional: `diff_preview` |
| `memory_log_learning` | `agent`, `topic`, `insight`, `source` | Optional: `confidence` |
| `memory_log_error` | `agent`, `error_type`, `message` | Optional: `context` |
| `memory_log_audit` | `agent`, `action`, `details` | Optional: `result` (default `success`) |

**Justice (attribution):** Every write tool requires a **non-empty** `agent` string (e.g. `cursor_staydangerous`). Empty or whitespace-only `agent` is rejected with `❌ agent is required…`.

### Recall (read)

| Tool | Required args | Notes |
|------|---------------|--------|
| `memory_search` | `query` | Optional: `agent`, `limit` |
| `memory_get_context` | `agent` | Optional: `limit` |
| `memory_get_tasks` | — | Optional: `status`, `limit` |
| `memory_get_decisions` | — | Optional: `limit` |
| `memory_get_learnings` | — | Optional: `limit` |
| `memory_get_recent_changes` | — | Optional: `limit` |
| `memory_get_recent_work` | `agent` | Optional: `limit` |
| `memory_get_sessions` | — | Optional: `agent`, `limit` |

### Health

| Tool | Args |
|------|------|
| `memory_health` | none |
| `memory_stats` | Optional: `agent` |

### Session

| Tool | Required args |
|------|---------------|
| `memory_start_session` | `agent` |
| `memory_end_session` | `agent`, `summary` |

## Response shapes

**Success (writes):** JSON string, e.g.

```json
{"ok": true, "task_id": "uuid", "agent": "cursor_staydangerous"}
```

**Success (reads):** JSON array or object (serialized from Postgres backend).

**Failure:** Plain string starting with `❌` and error message.

## Client ergonomics (hybrid rule)

Installable clients (`maat-memory-client`) may expose:

| Client method | Maps to tool |
|---------------|--------------|
| `remember(text, tags=...)` | `memory_log_learning` or `memory_log_conversation` |
| `recall(query)` | `memory_search` |
| `search(query)` | `memory_search` |
| `log_task(...)` | `memory_log_task` |
| `log_decision(...)` | `memory_log_decision` |
| `health()` | `memory_health` |

Do **not** add alternate REST verbs (`/remember`, `/recall`) in v1 unless a separate facade is explicitly deployed.

## Backend (not wire)

Direct Python import of `maat_memory.MaatMemory` remains valid for the MCP server and lab scripts. **Consumers in other builds** should prefer `maat-memory-client` over `sys.path` hacks.

## Related

- [GUARD-ADOPTION.md](GUARD-ADOPTION.md) — Guard organ (separate product)
- [MAAT-MEMORY-ADOPTION.md](MAAT-MEMORY-ADOPTION.md) — how to adopt Memory in a build
- [GITMAAT-CONNECT.md](GITMAAT-CONNECT.md) — Postgres URL matrix
