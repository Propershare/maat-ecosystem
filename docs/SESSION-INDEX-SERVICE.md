# Swarm Session Index — service design

**Norms and stack:** [`REMOTE_SWARM_SPEC.md`](REMOTE_SWARM_SPEC.md)  
**Client wiring:** [`../tehuti-config/swarm.config.example.yaml`](../tehuti-config/swarm.config.example.yaml)

This document is for **implementers**: HTTP API, storage split, auth, heartbeats, and how **canonical events** drive the index. It does **not** replace gitMaat; it holds **live presence** only.

---

## Purpose and non-goals

**Purpose:** A small, fast registry so every client can answer: *who is active, on which device, in which role, on which task, last seen when?*

**Non-goals:**

- Storing full transcripts or RAG chunks (Archivist / Maat Memory).
- Being the system of record for tasks (gitMaat).
- Semantic policy (“is this summary good?”)—that stays Analyst / schema / events.
- Authorization—use **Tehuti Guard** at execution boundaries ([`TEHUTI-GUARD-INTEGRATION-MATRIX.md`](TEHUTI-GUARD-INTEGRATION-MATRIX.md)).

---

## Auth model

Align with the rest of the Lab (see [`REMOTE_CLIENTS.md`](REMOTE_CLIENTS.md)):

| Mechanism | Usage |
|-----------|--------|
| **`Authorization: Bearer <token>`** | Primary; same secret family as `KA_API_KEY` / organ keys unless you split scope. |
| **Optional API key header** | Only if you must integrate a client that cannot send Bearer; document one canonical header name (e.g. `X-API-Key`). |
| **mTLS / network ACL** | Optional hardening on the Lab LAN; not a substitute for app auth on exposed routes. |

**Rules:**

- **No anonymous writes** unless you deliberately run a dev-only profile (document it).
- **`GET /sessions/active`** SHOULD require auth too so presence is not leaked to the LAN.
- Return **401** missing/invalid token; **403** if token is valid but not scoped for session-index writes.

---

## Canonical payloads

### Schema version

All bodies SHOULD include `"schema": "swarm.session.v1"` where the record is a full session document.

### Session document (`swarm.session.v1`)

Aligned with [`REMOTE_SWARM_SPEC.md`](REMOTE_SWARM_SPEC.md) — fields below are normative for the service.

| Field | Required | Notes |
|--------|-----------|--------|
| `schema` | register / full get | Constant `swarm.session.v1`. |
| `session_id` | yes | Client-generated UUID v4 or server-issued id; must not collide across swarm (client responsibility or server upsert). |
| `agent_id` | yes | Stable agent instance id. |
| `device_id` | yes | Stable device id. |
| `role` | yes | `scout` \| `analyst` \| `archivist` (lowercase in JSON). |
| `user_id` | no | Opaque human operator id. |
| `task_id` | no | gitMaat / task spine id when known. |
| `status` | yes | `active` \| `idle` \| `complete` \| `failed` |
| `current_topic` | no | Short human label; not a memory blob. |
| `current_tools` | no | String array (tool / organ names). |
| `memory_refs` | no | URIs into gitMaat (`gm://…`). |
| `started_at` | yes | ISO 8601 UTC; set at register. |
| `last_seen_at` | server-maintained | Updated on register, heartbeat, patch. |
| `parent_session_id` | no | Set on delegation. |
| `child_session_ids` | no | Array; append on delegate. |

**Server MAY add:** `server_revision`, `closed_at` (do not require clients to send).

### Register request body

Minimum:

```json
{
  "schema": "swarm.session.v1",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "agent_id": "cursor_lab_01",
  "device_id": "lab-node-01",
  "role": "analyst",
  "status": "active",
  "task_id": "task-8841",
  "current_topic": "session index rollout",
  "started_at": "2026-04-08T16:00:00Z"
}
```

**Idempotency:** `PUT /v1/sessions/{session_id}` (upsert) or `POST /v1/sessions/register` with same `session_id` should **overwrite non-terminal** rows or return **409** if terminal and client retries — pick one policy and document it (recommended: allow refresh while `active`/`idle`).

### Heartbeat / patch body

Partial JSON; at least bumps `last_seen_at` server-side. Clients MAY send:

```json
{
  "status": "active",
  "current_topic": "updated subtask",
  "task_id": "task-8842",
  "current_tools": ["gitmaat", "tehuti_core"],
  "memory_refs": ["gm://task/8842"]
}
```

### Close body

```json
{
  "status": "complete",
  "memory_refs": ["gm://task/8841"]
}
```

or `"status": "failed"` with optional `failure_reason` (short string) in payload extension.

---

## HTTP routes (recommended)

Base path: `/v1` (or mount under Tehuti Core under `/session-index/v1`).

| Method | Path | Purpose |
|--------|------|---------|
| `PUT` | `/v1/sessions/{session_id}` | **Upsert** register or replace non-terminal session. |
| `PATCH` | `/v1/sessions/{session_id}` | **Partial update** + heartbeat bump. |
| `POST` | `/v1/sessions/{session_id}/heartbeat` | **No body required** — server sets `last_seen_at` to now; optional JSON same as PATCH. |
| `POST` | `/v1/sessions/{session_id}/close` | Terminal transition; body has `status` `complete` \| `failed`. |
| `GET` | `/v1/sessions/{session_id}` | Full record (auth). |
| `GET` | `/v1/sessions/active?device_id=&role=&task_id=` | List non-terminal sessions, optionally filtered. |
| `DELETE` | `/v1/sessions/{session_id}` | Optional admin purge; prefer **close** + TTL for normal clients. |

**Responses:** `200` OK with full session JSON; `201` on first create if you split POST; `404` unknown id; `401`/`403` auth; `409` conflict (policy choice).

---

## Heartbeat semantics

| Topic | Recommendation |
|--------|----------------|
| **Client interval** | From [`swarm.config`](../tehuti-config/swarm.config.example.yaml) `session_index.heartbeat_interval_sec` (e.g. 30). |
| **Server staleness** | Sessions with `last_seen_at` older than `3–5 × interval` MAY be marked `idle` by a background sweeper or left `active` until TTL — **document** chosen behavior. |
| **Offline** | Do not delete immediately; **close** from client when possible; else TTL eviction from **live store** after N hours. |
| **Coalescing** | Clients MAY skip heartbeats if no activity and connection is expensive; **must** heartbeat at least once per interval while `active`. |
| **Clock** | Server authority for `last_seen_at` (use server time on heartbeat receipt). |

---

## Redis vs Postgres (and optional event spine)

| Store | Responsibility |
|--------|----------------|
| **Redis** (recommended for v1) | **Live registry**: key `session:{session_id}` → JSON or hash; optional index sets `sessions:active`, `sessions:device:{device_id}`. Fast heartbeat; TTL per key matches eviction policy. |
| **Postgres** (optional) | **Session ledger** / audit: append-only rows for `registered`, `heartbeat`, `updated`, `closed` with timestamps and diff snapshots; **not** on the hot read path for “who is active.” |
| **gitMaat / event bus** | **Durable narrative**: emit `maat:event:v1` style events ([`maat-ecosystem/skeleton/schemas/maat_event.schema.json`](../maat-ecosystem/skeleton/schemas/maat_event.schema.json)) when you need replay; **do not** block heartbeat on gitMaat commit. |

**Principle:** **Redis = present**; **Postgres ledger = optional history**; **gitMaat = tasks/memory truth** — same split as in `REMOTE_SWARM_SPEC.md`.

---

## Event ↔ index lifecycle mapping

Map **swarm canonical** types (and close `maat_event` names where they differ) to **index operations**:

| Event (`type` / canonical) | Index operation | Notes |
|----------------------------|------------------|--------|
| `task.started` | Upsert register; `status: active`; set `task_id` | First time or merge into existing session. |
| `task.delegated` | PATCH parent; append `child_session_ids`; child session upsert with `parent_session_id` | Two session rows linked. |
| `task.completed` | `close` with `complete` | Terminal. |
| `task.failed` | `close` with `failed` | Terminal. |
| Heartbeat tick (client timer) | `POST …/heartbeat` or PATCH | Updates `last_seen_at` only. |
| `tool.executed` (optional) | PATCH `current_tools` / metadata | Keep payload small. |
| `policy.evaluated` / `tool.denied` | No index requirement | Log to events/gitMaat; optional PATCH for debugging flags only. |

**Ordering:** Emit or observe **task.started** → register session **before** heavy tool fan-out; **task.completed** → close **after** Archivist writes land in gitMaat (or in parallel, but close must not replace gitMaat).

---

## Discovery (8010)

Expose the service in the manifest, e.g. `organs.session_index.endpoint` → `http://<lab>:8030`, and optional `auth: bearer`. Clients already read [`swarm.config`](../tehuti-config/swarm.config.example.yaml); manifest wins when present.

---

## Related

- **Authorization at execution:** [`TEHUTI-GUARD-INTEGRATION-MATRIX.md`](TEHUTI-GUARD-INTEGRATION-MATRIX.md)
- **Operator norms:** [`../AGENTS.md`](../AGENTS.md) (Swarm awareness section)

**Last updated:** 2026-04-08
