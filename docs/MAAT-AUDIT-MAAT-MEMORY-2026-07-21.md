# Maat audit — Maat Memory (gitMaat)

**Date:** 2026-07-21  
**Auditor:** `cursor_staydangerous`  
**Scope:** `maatlangchain/maat_memory/` (backend), MCP organ `:8022`, `maat-memory-client/`, wire contract  
**Verdict:** **Pass with conditions**

---

## Thesis

Maat Memory is a real shared organ — Postgres schema, attributable writes, MCP catalog, portable client, documented wire contract. It is **not** fully Maat-compliant until live-organ evidence is separated from SQLite adapter tests, dual-store split-brain is refused in lab mode, and writes reject empty `agent`.

---

## Principle table

| Principle | Finding | Status |
|-----------|---------|--------|
| **Truth** | Writes carry `agent` / `cursor_<hostname>`; wire contract is explicit. MaatBench `memory_fidelity` tests a **temp SQLite adapter**, not live Postgres / `:8022`. | Conditional → remediate with `memory_live` tier |
| **Balance** | Client vs backend split is correct. JSON fallback without `PGVECTOR_DB_URL` can create a local shadow beside the shared organ. | Conditional → lab refuse JSON unless `MAAT_MEMORY_ALLOW_JSON=1` |
| **Order** | Clear tables + tool catalog. Hardcoded `/home/suspect/.n8n/open-webui/.env` in `memory_postgres.py` violates portability. | Fail → fix to `paths.get_pgvector_db_url()` |
| **Justice** | `get_unique_agent_id` is correct; empty `agent` on MCP writes must be rejected. | Conditional → MCP boundary check |
| **Accountability** | `log_audit` / change / decision APIs exist; callers optional. Ops debt: mcpo-maat-memory systemd/venv (open gitMaat tasks). | Conditional |
| **Liveness** | Designed for `:8022` + Ka discovery; systemd health is an open item. | Conditional |

---

## Rational kernels (keep)

1. Postgres-first coordination + schema under `maat_memory/`
2. Wire contract — `docs/MAAT-MEMORY-WIRE-CONTRACT.md`
3. Thin client — `maat-memory-client` with discovery chain
4. Machine-aware agent IDs — multi-laptop justice
5. Adoption law — builds use client; backend import for MCP/migrations only

---

## Trash / debt

1. Hardcoded open-webui `.env` path in `memory_postgres.py`
2. Selling SQLite `memory_fidelity` as proof of live gitMaat
3. Silent JSON fallback in lab (split-brain)
4. Doc sprawl / dual call patterns (sys.path vs client)
5. Open ops: agent logging law; mcpo-maat-memory unit

---

## Remediation (this session)

| # | Action | Status |
|---|--------|--------|
| 1 | This audit document | Done |
| 2 | Route Postgres URL via `paths.py` only | Done |
| 3 | Lab mode: refuse JSON without `MAAT_MEMORY_ALLOW_JSON=1` | Done |
| 4 | MCP reject empty `agent` on all write tools | Done |
| 5 | MaatBench category `memory_live` (hits Postgres) | Done |

**Still open (separate tasks):** mcpo-maat-memory systemd/venv; enforce agent logging law across Hermes/OpenClaw.

---

## Evidence labeling rule (Truth)

| Claim | Valid evidence |
|-------|----------------|
| `memory_fidelity` score | SQLite adapter contract only — label as such |
| `memory_live` score | Live `PGVECTOR_DB_URL` write → read → attribution |
| “gitMaat is the LAW” | Process + docs until write-gate / Guard on publish |

Never publish a naked “Memory 100%” without **tier + date + git SHA**.

---

## Related

- [`MAAT-MEMORY-WIRE-CONTRACT.md`](MAAT-MEMORY-WIRE-CONTRACT.md)
- [`MAAT-MEMORY-ADOPTION.md`](MAAT-MEMORY-ADOPTION.md)
- [`GITMAAT-CONNECT.md`](GITMAAT-CONNECT.md)
- Dissertation §7.4 (2026-06 client/service evidence)
