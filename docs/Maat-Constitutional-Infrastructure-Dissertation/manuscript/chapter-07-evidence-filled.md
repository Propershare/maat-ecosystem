# Chapter 7 — Tehuti Research Lab as a Ma'at-Governed AI Infrastructure Prototype

*(Evidence-filled draft — 2026-06-18. Insert into Version 1 manuscript.)*

## 7.1 Introduction

This chapter is the empirical center of the dissertation. The Tehuti Research Lab provides a practical environment for testing Ma'at-governed AI infrastructure: policy gates, accountable memory, discovery manifests, governance event logs, and installable client contracts. The purpose is not to claim that the lab has solved AI governance. It is to show how Ma'at principles become testable infrastructure—and to report failures as honestly as successes.

**Scope note:** This chapter reports systems tested with recorded evidence as of June 2026. The public product surface is Ma'at constitutional infrastructure, MaatBench, Tehuti Guard, and Maat Memory — not a catalog of every experiment in the lab.

## 7.2 Case Study Method

The case study uses a normative-architectural method. Components are evaluated against the six Ma'at principles plus a seventh requirement derived from testing: **liveness and conformance** (constitutional gates must be running and consumers must speak the governed wire contract).

| Principle | Infrastructure question |
|-----------|-------------------------|
| Truth | Are claims and decisions traceable to records? |
| Balance | Does the system fail safe when posture is missing? |
| Order | Are roles, schemas, and contracts explicit? |
| Justice | Are decisions reviewable and non-arbitrary? |
| Reciprocity | Are users and operators protected from invisible harm? |
| Accountability | Are actions logged with correlation IDs? |
| Liveness & conformance | Are published organs actually reachable and correctly invoked? |

Evidence sources: unit tests, HTTP health sweeps, `maat_governance_events` rows in gitMaat/Postgres, wire-contract documents, and reproducible scripts (`scripts/guard_adapter_e2e_demo.py`). See `appendices/EVIDENCE-APPENDIX-2026-06-15.md`.

---

## 7.3 RAG Testing and the Truth Principle

Retrieval-augmented generation remains a central truth problem for the lab, but **formal Ma'at-audit test runs for RAG are deferred** to a later phase. MaatLangChain pipeline organs exist (`:8020`), and RAG is in active use, yet this dissertation does not claim citation fidelity, contradiction detection, or provenance labeling scores without logged benchmark output.

**Planned audit questions (not yet reported):** sourced vs unsupported claims; citation-support alignment; contradiction surfacing; freshness; distinction between user files and retrieved corpora.

*Status: design target — evidence pending.*

---

## 7.4 Memory Server Testing and Accountability

### Architecture

Maat Memory (gitMaat) is the lab's shared coordination organ: PostgreSQL/pgvector backend, MCP service on `:8022`, and a thin installable Python client (`maat-memory-client`) for consumers outside the monorepo.

### Tests performed

1. **Path portability** — Removed hardcoded lab paths; configuration via environment variables (`PGVECTOR_DB_URL`, discovery, API keys).
2. **Clean-environment client** — `maat-memory-client` installed in a fresh venv; auto-discovered `http://192.168.4.21:8022`; `doctor` self-diagnosis succeeded.
3. **Offline fallback** — Client degrades gracefully when the service is unreachable (no crash).
4. **Wire contract** — Documented in `docs/MAAT-MEMORY-WIRE-CONTRACT.md`; argument-mapping fixes for `memory_log_conversation` / `memory_log_audit` MCP tools.

### Ma'at audit

| Principle | Finding |
|-----------|---------|
| Truth | Memory writes attributable to `agent_id` (e.g. `cursor_staydangerous`) |
| Order | Versioned MCP tool catalog; env-driven endpoints |
| Accountability | Governance events table `maat_governance_events` with `correlation_id`, `payload`, timestamps |
| Balance | Auth required on `:8022` (401 without bearer) — usability gap found and addressed in client discovery |

**Conclusion:** Memory passed accountability and order tests for the client/service split. MaatBench `memory_fidelity` category: **8/8 passing** (2026-06-20).

---

## 7.4a Tehuti Guard and Policy Gates

*(Inserted evidence section — policy layer is the strongest lab prototype.)*

### Architecture

Tehuti Guard exposes `POST /decision` on `:8013` with a nested envelope (`machine_id`, `actor`, `action`, `policy_version`, `correlation_id`). Decisions: `allow`, `review`, `quarantine`, `escalate`, `deny`. Posture context may be supplied by maat-sentinel (`:4242`).

### Tests performed

1. **Unit tests** — Python rule core: 9/9 passing (`tehuti-guard/guard/tests/`).
2. **Fail-safe behavior** — With Sentinel unavailable, `/decision` returns `review` (`sentinel_unreachable_review`), not silent `allow`.
3. **Positive control (2026-06-06)** — gitMaat row `42c1c0d4-ce47-496c-b52f-66f51c5805d6`: `allow` / `operational_low_risk_allow` after posture feed live.
4. **Fail-safe control (same session)** — Row `d8d4e16d-5537-4d15-a681-92a6aaa6184c`: `review` when Sentinel unreachable.
5. **Build/CI** — TypeScript helpers fixed; `.github/workflows/tehuti-guard-ci.yml`; PR `Propershare/maat-ecosystem#1`.
6. **Contract drift finding** — `maat-runtime` guard client flat body vs nested API envelope → would 400 as `invalid_envelope` (governance theater risk).

### Liveness finding (2026-06-15)

Health sweep: Ka Discovery `:8010` listed `policy` organ while `:8013` and `:4242` were **connection refused**. The constitution was published but unenforced.

### Ma'at audit

| Principle | Finding |
|-----------|---------|
| Balance | Fail-safe `review` when posture missing — verified |
| Order | Wire contract documented; consumer drift detected |
| Justice | Closed decision set; `matched_rules` and `explanation_id` in payload |
| Accountability | Decisions logged to `maat_governance_events` |
| Liveness | Manifest ≠ enforcement; requires continuous verification |

---


## 7.5 OpenClaw Gateway and Bounded Automation

**n8n is retired from the lab** (decision 2026-06-18; see `docs/N8N-RETIRED.md`). Workflow automation for governed agents now runs through **OpenClaw** — channels, cron, hooks, and tool execution on gateway port `:18790`, with workspace rooted at the Tehuti Lab tree. This section reports bounded-action testing against that stack, not legacy n8n workflow exports.

### Architecture

OpenClaw is the operator-facing gateway: Telegram and other channels, scheduled jobs, voice hooks, and MCP tool calls against lab organs (Guard `:8013`, Memory `:8022`, Ka discovery `:8010`). High-impact actions are expected to pass through Tehuti Guard before execution; gitMaat records tasks and governance rows.

### Tests performed

1. **Gateway liveness** — OpenClaw control UI reachable on `:18790` in June 2026 health sweeps when the gateway process is running.
2. **Workspace alignment** — `agents.defaults.workspace` in `~/.openclaw/openclaw.json` must match the lab root (`/home/suspect/.n8n`); misalignment breaks agent continuity and memory files.
3. **MaatBench gateway suites** — `gateway_contract` (5/5) validates KA2 archivist records and scorecard math; `gateway_policy` (4/4) round-trips lived-truth cases from `guard_cases/`.
4. **Retirement boundary** — n8n MCP (`:8015`) removed from Ka manifest; no dissertation evidence claims n8n workflows.

### Ma'at audit

| Principle | Finding |
|-----------|---------|
| Balance | Automation power routed through gateway + Guard, not unbounded webhook chains |
| Order | Single workspace truth; channel allowlists in `openclaw.json` |
| Accountability | Agent actions loggable to gitMaat when workers call memory tools |
| Liveness | Gateway must be running; manifest alone is insufficient |

*Status: gateway organ exercised; formal end-to-end OpenClaw → Guard → gitMaat correlation scenarios remain on the MaatBench v2 E2E roadmap.*

---

## 7.6 Security File System and Order

Three-ring governance (inner / middle / outer) is documented in Tehuti Guard and lab policy. Filesystem MCP (`:8016`) exposes the lab root with high trust. **Formal file-classification and blocked-access test logs are not yet inserted** as dissertation evidence.

*Status: partial — policy documented; empirical audit pending.*

---

## 7.7 Tehuti SQL and Structured Memory

gitMaat uses PostgreSQL (`maat_memory` database) for tasks, decisions, learnings, changes, and `maat_governance_events`. This satisfies **order** (schemas) and **accountability** (queryable rows) at the persistence layer.

**Sample governance query surface:** `MaatMemoryPostgres.query_governance_events(machine_id=..., correlation_id=...)`.

Representative 2026-06-06 correlation: `maat-security-stack:20260606T144720Z:3efa879b:guard-sentinel-smoke` links sentinel posture → guard `review` → guard `allow` in sequence.

---

## 7.8 Agent and Swarm Testing

Scout / Analyst / Archivist roles are specified (`docs/SCOUT-ANALYST-ARCHIVIST.md`). Session Index is **spec-only** (`docs/SESSION-INDEX-SERVICE.md`) — not reported as live in June 2026 sweeps. OpenClaw gateway (`:18790`) was reachable; multi-agent swarm benchmarks are **not** claimed here.

*Status: architectural — formal swarm Ma'at audit pending.*

---

## 7.9 ComfyUI, Wan, Bark, and Media Provenance

ComfyUI MCP (`:8019`) was reachable in the 2026-06-15 sweep. **Media provenance schema and Ma'at-audit runs for generated assets are not reported** in this chapter.

*Status: organ live — provenance audit pending.*

---

## 7.10 LabRat.ai and Real-World Bounded Agency

LabRat.ai / vehicle assistant work is referenced in lab planning but **no formal test log is included** in this evidence pass.

*Status: future work.*

---

## 7.11 Case Study Conclusion

The Tehuti Research Lab case study supports three claims:

1. **Ma'at can be operationalized** — Guard decisions, memory client, wire contracts, and governance rows are concrete, not metaphorical.
2. **Failure modes are constitutional** — The most dangerous state observed was not absence of governance but **advertised-but-absent governance** and **silent contract drift**.
3. **A Ma'at-governed system is one that makes failure visible** — Fail-safe `review`, logged correlation IDs, and health sweeps that contradict the manifest are evidence of a system designed for correction—not perfection.

The lab does not yet prove full-stack Ma'at compliance across remaining MaatBench categories and unaudited subsystems. It proves that **constitutional infrastructure can be built, tested, and falsified**—which is what a dissertation case study must do.

**MaatBench (2026-06-20):** Eight categories, **58/58 tests passing** — `contract_integrity`, `policy_fidelity`, `memory_fidelity`, `event_fidelity`, `portability`, `learning_safety`, `gateway_contract`, `gateway_policy`. MAAT Score **100%** for this tier (excludes live-model `behavior_balance` and HTTP E2E organs). JSON report: `appendices/maatbench-report-2026-06-20.json`. Public claims must label tier and date (see `maat-ecosystem/maatbench/README.md`). Sentinel/Forge E2E and RAG audit tiers remain future work.
