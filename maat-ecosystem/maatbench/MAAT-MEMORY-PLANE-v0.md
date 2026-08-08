# Maat Memory Plane v0

**Status:** Doctrine + executable plane (registry, learning loop, storage awareness, session presence)  
**Date:** 2026-07-26  
**Lab:** Tehuti Research Lab  
**Stack fit:** package → run → should → prove → resist → attest

---

## 1. Purpose

The Memory Plane is how Tehuti Lab achieves **enterprise balance** across:

- every **machine** enrolled on the network / business
- every **agent** registered to the organ
- every **storage class** (what may be written, where, by whom)
- **time** (adapters change; Maat contracts do not)

It does **not** replace gitMaat. It **governs** how agents and machines use gitMaat.

> MaatBench proves. Isfet resists. Maat Attest promotes or denies.  
> **Memory Plane balances** — who may remember, learn, and retrieve across the fleet.

---

## 2. Maat audit (baseline this plane fixes)

| Finding | Gap | Plane fix |
|--|--|--|
| Shared Postgres organ | Soft identity only (`cursor_<host>`) | `maat_machines` + `maat_agents` enroll |
| `file://` artifact URIs | Bytes local; catalog shared | Storage awareness + content hash / resolve map |
| `maat_learnings` | Insight text; weak snapshots | Propose → Guard → apply with before/after |
| Session Index | Spec only | `maat_session_presence` (live presence in Postgres) |
| Write law uneven | Instructional for Cursor | Preflight + enroll gate for durable writes |
| Learning safety | MaatBench schema ≠ live PG | Learning loop enforces reversible contract |

---

## 3. Stack verbs (memory)

| Layer | Verb | Memory Plane duty |
|--|--|--|
| Workflowware | package | Learning/artifact packages carry schema + hash |
| Hermes | run | Preflight recall before plan |
| Guard / MAAT | should | Gate durable learning apply |
| MaatBench | prove | Memory-plane category |
| Isfet | resist | Poison / wipe / anonymous write |
| Maat Attest | promote/deny | “Fleet shares memory” is a claim |

---

## 4. Storage classes (Order)

Every durable object carries a **storage_class**:

| Class | Store | Who writes | Notes |
|--|--|--|--|
| `constitutional` | soul / schemas / policy | amendment only | Never via learning loop |
| `coordination` | Postgres gitMaat | enrolled agents | Tasks, decisions, changes |
| `learning` | `maat_learnings` (+ snapshots) | propose → review → apply | Reversible |
| `artifact` | object roots + DB URI | promote from local | Portable resolve |
| `ephemeral` | session / local cache | free | TTL; not truth |

**Storage awareness** = resolve `(uri, machine_id) → bytes | redirect | not_found` without agents hardcoding host paths.

**Host Body Awareness (v0.1):** mount classes are authority boundaries — see `docs/MAAT_STORAGE_ROOTS_v0.1.yaml` and `memory_plane/write_preflight.py` (`write-check` / `body` CLI). Doctrine: root is cockpit, not warehouse.

Technology under the adapter may change (NFS → MinIO → IPFS). Agents see **class + URI + sha256**.

---

## 5. Registry (Justice)

### Machines (`maat_machines`)

- `machine_id` — stable (hostname+MAC style from `machine_info`)
- `hostname`, `storage_roots` (JSONB map of logical roots → absolute paths)
- `status`: `enrolled` | `revoked` | `degraded`
- `last_seen_at`

### Agents (`maat_agents`)

- `agent_id` — e.g. `cursor_staydangerous`
- `machine_id` FK
- `tool_type`, `ring` (`inner` | `middle` | `outer`), `role` (scout/analyst/archivist/…)
- `capabilities` JSONB
- `status`: `enrolled` | `revoked` | `suspended`
- `last_seen_at`

**Law:** Durable learning apply requires `agent_id` enrolled and `machine_id` enrolled (unless `MAAT_MEMORY_PLANE_PERMISSIVE=1` for bootstrap).

---

## 6. Learning loop (Balance)

```
Recall (preflight)
  → Propose learning (applied=false, before_snapshot)
  → Guard should (or lab review flag)
  → Apply (after_snapshot, applied=true, approved_by)
  → Rollback (restore before_snapshot)
```

### Learning types (from `maat_learning` contract)

`memory_consolidation` · `prompt_refinement` · `tool_usage_refinement` · `fine_tune_metadata` · `policy_update` · `rollback`

- `policy_update` and constitutional targets → **deny** in loop (amendment path only)
- Hostile / personal poison → Isfet / Guard deny
- Default `applied=false` until apply()

---

## 7. Session presence (Balance across network)

Table `maat_session_presence` holds **live** who/where/what — not transcripts.

Fields align with `swarm.session.v1` (see `.n8n/docs/SESSION-INDEX-SERVICE.md`):  
`session_id`, `agent_id`, `machine_id`, `role`, `task_id`, `status`, `current_topic`, `last_seen_at`.

Heartbeat / register / complete. Expired rows are idle (TTL query), not deleted sacred history.

---

## 8. Preflight (every agent, every machine)

Before planning work, enrolled agents run:

1. `ensure_enrolled(machine, agent)`
2. `heartbeat_presence(...)`
3. `get_tasks(pending)`
4. `get_learnings` (topic-relevant, prefer `applied=true`)
5. `get_decisions` / recent changes (Sankofa)
6. Optional: resolve artifact URIs via storage layer

CLI: `python3 hermes/scripts/maat_memory_plane.py preflight`

---

## 9. Enterprise balance rules

1. One coordination organ (Postgres) — no silent JSON brain in lab.
2. No anonymous durable learning apply.
3. Portable truth: content hash + resolve map; host path is not the claim.
4. Ring-aware writes (outer may not amend constitutional).
5. Reversible learning only.
6. Presence visible (Session Index / presence table).
7. Prove the plane (MaatBench `memory_plane`).
8. Attest fleet-memory claims via Maat Attest — not slogans.

---

## 10. Evolution (time + technology)

| Frozen | Replaceable |
|--|--|
| Storage class enum | Object store backend |
| Learning type enum | Embedding model |
| Enroll / apply / rollback API | MCP transport |
| Evidence hash on artifacts | CDN / IPFS pin |
| Honesty tiers for Attest | UI |

---

## 11. Files

| Piece | Path |
|--|--|
| Doctrine | `hermes/docs/MAAT-MEMORY-PLANE-v0.md` |
| Schema | `maatlangchain/maat_memory/schema_memory_plane_v0.sql` |
| Package | `maatlangchain/maat_memory/memory_plane/` |
| CLI | `hermes/scripts/maat_memory_plane.py` |
| MaatBench | `maatbench/contracts/memory_plane_tests.json` |
| Runner | `maatbench/runners/memory_plane_runner.py` |

---

## 12. Success criterion

Any enrolled agent on any enrolled machine can answer:

1. Who else is active?  
2. What durable learnings apply to this task?  
3. Where do artifact bytes live (resolved)?  
4. Can I apply this learning (Guard + enroll)?  
5. Can we **Maat-Attest** that the fleet shares governed memory?

If not — the plane is incomplete; do not claim enterprise balance.
