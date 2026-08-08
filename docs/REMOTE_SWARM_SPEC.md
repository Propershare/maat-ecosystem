# Remote swarm spec — federation, identity, events, and session index

**Purpose:** One canonical cross-machine contract for the Lab. **Culture** (how we behave) and **runtime** (how we connect and leave traces) are deliberately separate.

---

## Two layers

### 1. Culture / policy (workspace-local)

[`AGENTS.md`](../AGENTS.md) governs repo-rooted sessions: role definitions (Scout / Analyst / Archivist), Archivist structured output, “query gitMaat first” where Maat Law applies, naming norms, escalation habits. It does **not** automatically apply to every laptop or phone.

### 2. Runtime / infrastructure (every participant)

What actually makes each machine participate the same **way** in the **same system of record**:

- MCP organs reachable from the LAN (or VPN), not only `127.0.0.1`.
- **Ka Discovery** (`8010`) — resolve brain / Maat Memory / other organs from `GET …/manifest`; avoid hardcoding localhost-only URLs on remote clients.
- Per-client config (see [`tehuti-config/swarm.config.example.yaml`](../tehuti-config/swarm.config.example.yaml)).
- **Auth** — same pattern everywhere (`KA_API_KEY` / Bearer where enabled); no silent anonymous LAN access unless you explicitly want it.
- **Shared identity** — stable `agent_id`, `device_id`, non-colliding `session_id`.
- **Shared event spine** — meaningful actions emit **canonical** event types (aligned with [`maat-ecosystem/skeleton/schemas/maat_event.schema.json`](../maat-ecosystem/skeleton/schemas/maat_event.schema.json)); eventually every client honors the same taxonomy.
- **Shared memory spine** — gitMaat / Maat Memory as **truth** for durable tasks and memory; structured writes with provenance.

**Key framing:** Do not ask “can every machine read the same `AGENTS.md`?” Ask: **“How does every machine behave compatibly and leave traces in the same system of record?”**

The trio alone is not enough; the operational law is:

**Scout / Analyst / Archivist + Discovery + auth + gitMaat (and canonical events) + stable identity.**

Without shared events and identity, you have **parallel clients calling the same tools**, not **swarm awareness**.

---

## Three artifacts (recommended)

| Artifact | Role |
|-----------|------|
| [`AGENTS.md`](../AGENTS.md) | Human-readable workspace law for Cursor/repo agents. |
| [`tehuti-config/swarm.config.example.yaml`](../tehuti-config/swarm.config.example.yaml) | Machine-readable routing, discovery URL, service hints, identity flags — copy per host as `swarm.config.yaml` (gitignore secrets). |
| [`docs/REMOTE_CLIENTS.md`](REMOTE_CLIENTS.md) | Onboarding checklist for any new machine or orchestrator. |
| **This spec** | Normative field names, session index shape, event names — **hand to implementers**. |
| [`docs/SESSION-INDEX-SERVICE.md`](SESSION-INDEX-SERVICE.md) | Session Index **HTTP service**: routes, auth, heartbeats, Redis/Postgres. |
| [`docs/TEHUTI-GUARD-INTEGRATION-MATRIX.md`](TEHUTI-GUARD-INTEGRATION-MATRIX.md) | **Where to call** Tehuti Guard before execution. |

---

## Standards every client should share

**Identity**

- `agent_id` — unique per agent instance (e.g. `cursor_staydangerous`, `openclaw-phone-alpha`).
- `device_id` — stable per physical device or VM.
- `user_id` — optional human operator.
- `session_id` — unique per conversation/run; use UUIDs or monotonic server-assigned ids to avoid collisions across machines.

**Discovery**

- Resolve Tehuti Core / Maat Memory / organs via **`http://<lab-host>:8010/manifest`** first.
- Use **LAN hostname or IP** from the manifest’s `organs.*.endpoint`, not `localhost`, unless the client **is** the server.

**Role behavior** (aligned with [`docs/SCOUT-ANALYST-ARCHIVIST.md`](SCOUT-ANALYST-ARCHIVIST.md))

- **Scout** — fast triage, gather sources, minimal commitment.
- **Analyst** — synthesis, arbitration, explicit recommendations.
- **Archivist** — structured JSON (or schema-aligned records), tags, provenance, compact summaries.

**Event logging**

Emit canonical types for anything that affects coordination (exact names evolve; align with `maat_event` and [`docs/MAAT-CHECKPOINT-NEXT-TRANCHE.md`](MAAT-CHECKPOINT-NEXT-TRANCHE.md)):

- `task.started`, `task.delegated`, `task.completed`, `task.failed`
- `memory.read`, `memory.written`
- `tool.requested`, `tool.executed`, `tool.denied`
- `analysis.escalated` / policy outcomes as needed

**Memory discipline**

- Query gitMaat when the task is coordination or continuity-heavy.
- Write back **structured** summaries; avoid duplicate writes; attach **sources** and **memory_refs**.

**Auth**

- All clients use the same **Bearer** (or agreed) pattern; document in [`REMOTE_CLIENTS.md`](REMOTE_CLIENTS.md).

---

## Tehuti Guard (governance gate)

**Tehuti Guard** is **not** the Session Index and **not** `AGENTS.md`. In this workspace it is primarily a **policy library** ([`tehuti-guard/`](../tehuti-guard/)): **three-ring** roles, **path-prefix** resources, LDAP-backed **read / write / execute / propose** decisions (`enforceLDAPPolicy`, `isResourceAccessible`).

| Layer | Question it answers |
|--------|---------------------|
| Session Index | Who is active, where, on what task (present state)? |
| Tehuti Guard | Is this **identity** allowed this **action** on this **resource**? |
| gitMaat / Archivist | What was decided and stored (durable record)? |

**Operational rule:** **Session Index** (or register intent) **before** heavy coordination; **Tehuti Guard** **before** execution on protected surfaces; **Archivist / gitMaat** **after** outcomes.

Guard only applies **where you call it**—wrap file writes, memory writes to protected stores, MCP tool execution, deploy/shell, and proposals against inner/middle ring paths first.

**Call-site matrix (hand to implementers):** [`docs/TEHUTI-GUARD-INTEGRATION-MATRIX.md`](TEHUTI-GUARD-INTEGRATION-MATRIX.md).

---

## Swarm Session Index (session registry)

**What it is:** A **coordination layer**, not the full memory store. Think **air traffic control** for active sessions; **gitMaat / Maat Memory** remains the **archive and task spine**.

**Why:** Shared tools + shared DB without a **session index** still leave you blind to *who is doing what right now*, handoffs, and collisions. Mobile and multi-laptop setups need a small **presence and routing** map.

**What it is not:** Long-term RAG store, replacement for `AGENTS.md`, or a second gitMaat. Do **not** merge the live registry into gitMaat as the primary hot path; keep **present** state cheap and **past** truth in Maat Memory.

### Minimal bootstrap record

Smallest useful shape (expand to `swarm.session.v1` below as the service matures):

```json
{
  "session_id": "",
  "agent_id": "",
  "device_id": "",
  "role": "scout | analyst | archivist",
  "status": "active | idle | complete",
  "task_id": "",
  "current_topic": "",
  "last_seen_at": "",
  "started_at": ""
}
```

### Event alignment (canonical types)

Wire client/runtime behavior so coordination stays consistent:

| Event | Session Index effect |
|--------|----------------------|
| `task.started` | Register session (or ensure row exists) |
| `task.delegated` | Link parent/child sessions, update `task_id` |
| `task.completed` / `task.failed` | Close session (`status` terminal) |
| Heartbeat tick | Update `last_seen_at` (and optional `status` / `current_topic`) |

Durable task/memory rows still go to **gitMaat**; the index reflects **live** presence only.

### Two sub-layers (minimal design)

1. **Live registry** — fast, current: who is online, role, task in flight, heartbeat.
2. **Session ledger** — historical: delegations, conclusions, pointers into gitMaat rows (`memory_refs`).

**Source of truth:** Durable facts still land in **gitMaat/Postgres**. The index is a **map**; events **replay** against the ledger.

### Example record (`swarm.session.v1`)

```json
{
  "schema": "swarm.session.v1",
  "session_id": "sess-2026-04-08-00123",
  "agent_id": "analyst-lab-node-02",
  "device_id": "lab-node-02",
  "role": "analyst",
  "user_id": null,
  "task_id": "task-8841",
  "status": "active",
  "current_topic": "dataset planning for Gemma swarm",
  "current_tools": ["tehuti_core", "gitmaat"],
  "memory_refs": ["gm://task/8841"],
  "started_at": "2026-04-08T15:02:11Z",
  "last_seen_at": "2026-04-08T15:08:44Z",
  "parent_session_id": "sess-2026-04-08-00110",
  "child_session_ids": []
}
```

**Operational rules (clients):**

1. **Register** on session start (or first tool use) with `session_id`, `agent_id`, `device_id`, `role`.
2. **Heartbeat** every N seconds (or on meaningful state change) — update `last_seen_at`, `status`, `current_topic` as needed.
3. **Update** on handoff — set `parent_session_id` / `child_session_ids`, `task_id`.
4. **Close** on completion — `status: complete` or `failed`; keep row for TTL or archive to ledger.
5. **Durable results** — still **write** summaries and tasks to **gitMaat** via Archivist/tools.

### Service implementation (routes, storage, auth)

Normative design for implementers: **[`docs/SESSION-INDEX-SERVICE.md`](SESSION-INDEX-SERVICE.md)** (HTTP `/v1` routes, Bearer auth, heartbeat semantics, Redis vs Postgres split, canonical payloads, event lifecycle).

**Plain-English name:** **Swarm Session Index** (or `lab-presence` in metrics).

---

## Mental model (one paragraph)

[`AGENTS.md`](../AGENTS.md) is the **constitution for one workspace**; **client configs + MCP + Discovery + gitMaat + (future) session index + canonical events** are the **federation mechanism for the whole Lab**. Same roles everywhere; same traces in one spine; session index for **now**, gitMaat for **what lasted**.

---

**Last updated:** 2026-04-08 — Tehuti Lab (session index service doc + Guard matrix linked).
