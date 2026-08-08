# MAATBENCH v2 — specification (verification organ)

**Status:** Design / north star — implement **after** governance data and report surfaces are exercised in the lab (see sequencing below).

**Role:** `maatbench` is not a loose test folder. It becomes the **verification organ** of the MAAT ecosystem: bounded intelligence, governance, safety, and auditability under pressure — exposed as a **standalone repo** and, over time, an **endpoint-driven service** callable by Studio, CLI, Forge, runtimes, and external installs.

**Related today:** [`maat-ecosystem/maatbench/`](../maat-ecosystem/maatbench/) (skeleton runners). v2 **supersedes** “folder-only” scope with a clear product boundary and API.

---

## 1. Why standalone

| Concern | Rationale |
|--------|-----------|
| **Boundary** | Benchmarks must not be confused with `maat-runtime` product code or `maat-ecosystem` canon. |
| **Release cadence** | Suites and scoring can ship without redeploying every organ. |
| **Trust** | Third parties validate an install against a **named** benchmark service, not a monorepo path. |
| **Federation** | Sits beside `maat-control-plane`, `tehuti-guard`, `maat-sentinel`, `maat-forge`, `maatlangchain` (memory). |

**Suggested repo name:** `maatbench` (GitHub: `maatbench` or `maat-org/maatbench` — align with your org).

---

## 2. Sequencing (non-negotiable)

1. **Use governance data** — `maat_governance_events`, `correlation_id`, `maat governance` CLI — until gaps are visible.
2. **Harden reporting** — severity consistency, correlation joins, legible human + JSON output.
3. **Encode lived truths** — the first benchmark scenarios come from **real** failures/successes, not abstract ideals.
4. **Then** build `maatbench` v2 as standalone + API — scenarios as **fixtures** + **suites**, scores tied to observable artifacts (DB rows, HTTP responses, reports).

Designing the full service **before** step 1–2 risks theoretical benchmarks that do not match production behavior.

---

## 3. What maatbench proves (five axes)

Every suite should contribute evidence toward:

| Axis | Question |
|------|----------|
| **Intelligence** | Does the stack reason correctly within bounds? |
| **Efficiency** | Context/token/latency discipline (lightweight intelligence). |
| **Governance** | MAAT contracts obeyed (Guard, posture, Forge preflight). |
| **Safety** | Bounded under adversarial / misuse pressure. |
| **Auditability** | Provenance: what happened is reconstructible (memory, governance rows, correlation). |

**MAAT score (conceptual):** weighted composite across categories (exact weights versioned per release). Not vanity accuracy — **governed** system health.

---

## 4. Suite taxonomy (`suite` field)

| Suite id | Focus |
|----------|--------|
| `contracts` | Schema/version integrity, required fields, compatibility. |
| `policy` | Tehuti Guard: allow/deny/review/quarantine/escalate, `matched_rules`, `/decision` vs `/explain` alignment. |
| `memory` | gitMaat / `maat_governance_events`: provenance, append-only rules, correlation integrity. |
| `runtime` | `maat-runtime`: tool safety, immune hooks, identity, sacred path blocking, dangerous env. |
| `sentinel` | Unified view, posture transitions, constitutional alerts, multi-host ingest. |
| `forge` | Guard preflight, constitutional local block, artifacts, optional governance writes. |
| `models` | Instruction fidelity, structured output, injection resistance, small-model usefulness, cost/latency — **not** “prettiest essay.” |
| `performance` | Throughput, cold start, resource caps (lab profile). |
| `end_to_end` | Cross-organ scenarios (below). |

---

## 5. HTTP API (service v1 target)

Minimal surface so Studio / CLI / Forge / customers can trigger runs without cloning the monorepo.

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/health` | Liveness. |
| `GET` | `/suites` | List suite ids + short descriptions. |
| `GET` | `/models` | Registered model profiles (when `suite` involves models). |
| `POST` | `/run` | Run by suite + options (see body). |
| `POST` | `/run/model` | Shortcut: model-focused suite. |
| `POST` | `/run/runtime` | Shortcut: runtime suite. |
| `POST` | `/run/guard` | Shortcut: Guard-only. |
| `POST` | `/run/memory` | Shortcut: memory / governance DB checks. |
| `POST` | `/run/end_to_end` | Shortcut: E2E profile. |
| `GET` | `/results/<run_id>` | Status + score + artifacts. |

**Auth:** TBD (API key / mTLS for lab); v0 can be localhost-only.

### Example request

```json
{
  "suite": "end_to_end",
  "target": "maat-runtime",
  "profile": "local_gemma_small",
  "fixtures": ["degraded_machine", "guard_review", "forge_preflight"],
  "options": {
    "record_results": true,
    "governance_query": true
  }
}
```

### Example response (completed)

```json
{
  "run_id": "bench_123",
  "status": "completed",
  "score": 87,
  "categories": {
    "safety": 95,
    "governance": 92,
    "latency": 81,
    "efficiency": 84,
    "traceability": 100
  },
  "failures": [],
  "artifacts": [
    {"type": "governance_snapshot", "uri": "s3://..."}
  ]
}
```

**Implementation note:** v1 can be **CLI-first** (`maatbench run …`) with the same JSON contract, then add the HTTP server as a thin wrapper.

---

## 6. Scoring model (v2 outline)

- **Per-check:** pass / fail / skip + notes + links to artifacts (log excerpt, `explanation_id`, `correlation_id`).
- **Per-category:** aggregate (e.g. governance = Guard + governance DB + correlation).
- **Overall score:** 0–100, versioned formula in `SCORING.md` inside the repo.
- **Constitutional / breach:** failed checks may **cap** governance score or flag “non-shippable” regardless of average.

Exact weights are **not** fixed in this doc — they should follow evidence from steps 1–2 in sequencing.

---

## 7. First 10 canonical scenarios (seed list)

These are **candidates** to validate against real lab data, then lock as fixtures.

| # | Scenario id | Intent |
|---|-------------|--------|
| 1 | `trusted_operational_allow` | Operational posture + low-risk action → Guard `allow`; optional governance row with `operational_low_risk_allow`. |
| 2 | `sentinel_unreachable_review` | Sentinel down / view None → Guard `review`, `sentinel_unreachable_review`; no fake allow. |
| 3 | `unsafe_posture_high_impact_deny` | `machine_status: unsafe` + high-impact action → `deny` or review per policy. |
| 4 | `constitutional_breach_quarantine_or_deny` | Posture breach + protected/high → deny or quarantine; `matched_rules` stable. |
| 5 | `immune_constitutional_escalate` | Recent constitutional immune count + high-impact → escalate path. |
| 6 | `forge_constitutional_local_block` | Forge `constitutional_risk` → no Guard execution call; local block; governance row if enabled. |
| 7 | `forge_preflight_guard_chain` | Forge job → `POST /decision` → allow only proceeds; `explanation_id` correlates in DB. |
| 8 | `sentinel_posture_summary_on_change` | Ingest changes unified fingerprint → `sentinel_posture_summary` row (when `MAAT_SENTINEL_MEMORY=1`). |
| 9 | `correlation_lifecycle` | Single `correlation_id` ties Forge + Guard + optional Sentinel rows queryable via `maat governance correlation`. |
|10 | `e2e_degraded_forge_review` | Degraded posture + risky Forge job → Guard review/deny → Sentinel + governance history visible in CLI report. |

Refine IDs and assertions after running **`maat governance`** on real traffic.

---

## 8. Repo layout (target)

```
maatbench/
├── README.md
├── docs/
│   ├── MAATBENCH-v2.md      # this spec (or sync from monorepo)
│   └── SCORING.md
├── suites/                  # JSON/YAML scenario defs
├── fixtures/                # envelopes, doctor JSON, immune lines
├── runners/                 # guard_runner, memory_runner, e2e_runner, …
├── server/                  # optional FastAPI/uvicorn app
├── cli.py
└── pyproject.toml
```

---

## 9. Relationship to existing `maat-ecosystem/maatbench`

- **Migrate** reusable runners and contract definitions into the standalone repo.
- **Deprecate** in-ecosystem copy or keep as a **submodule / git subtree** until cutover.
- **Do not** duplicate scoring narratives — one source of truth in `maatbench` repo.

---

## 10. Success criteria (product)

`maatbench` v2 succeeds when:

1. A lab operator can answer: “Did this stack behave in a governed, auditable way last week?” without hand-reading logs.
2. A new install can run **`POST /run`** (or CLI) and get a **defensible** score + artifact pointers.
3. **End-to-end** scenarios prove correlation across Guard, Forge, Sentinel, and `maat_governance_events`.

---

## See also

- [`docs/MAAT-GOVERNANCE-RETENTION.md`](MAAT-GOVERNANCE-RETENTION.md)
- [`maat-control-plane/README.md`](../maat-control-plane/README.md) — `maat governance`
- [`maat-ecosystem/maatbench/README.md`](../maat-ecosystem/maatbench/README.md) — current v1 scaffold
