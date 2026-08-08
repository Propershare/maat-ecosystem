# MAAT Forge (lab skeleton)

**Status:** First job loop only — scheduler/MCP server are future work. See [`docs/MAAT-FORGE.md`](../docs/MAAT-FORGE.md) and [`docs/MAAT-IMMUNE-SYSTEM.md`](../docs/MAAT-IMMUNE-SYSTEM.md).

## Purpose

Bounded experiments and repair **candidates** run **after** runtime immune hooks exist (`maat-runtime` extension). Forge does **not** mutate sacred layers; results go to reports and optional gitMaat ingestion.

## Layout

```
maat-forge/
├── README.md
├── lib/
│   └── guard-preflight.mjs      # envelope, Guard POST, optional maat-memory row
├── jobs/
│   └── first-bounded-loop.mjs   # template: read immune log, emit report, stub repair candidate
└── reports/                     # job output (gitignored artifacts optional)
```

## Run the first job

From the lab root (`~/.n8n`):

```bash
node maat-forge/jobs/first-bounded-loop.mjs
```

The job **preflights Tehuti Guard** (`POST /decision` to `TEHUTI_GUARD_URL`, default `http://127.0.0.1:8013`) before doing any work. Guard pulls Sentinel’s unified view for `machine_id`. Execution proceeds only when the decision is **`allow`**; otherwise the job exits **2** and writes a short report under `reports/`.

Every run emits a machine-readable **`preflight_decision`** (`schema: maat-forge/preflight_decision/v1`) in the report: `envelope_sent`, `decision_received`, `machine_id`, `job_type`, `risk_class`, `outcome` (`allow` \| `deny` \| `blocked_constitutional` \| `skipped` \| `error`), `reason`, and `tags`. Fetch failures add **`guard_unreachable`** and **`stack_unavailable`** (plus optional `request_timeout`, `connection_refused`, `dns_failure`). The same record is logged to stdout as event **`forge.preflight_decision`** for downstream sinks.

**Risk classes** (Forge): `low_risk` | `medium_risk` | `high_risk` | `constitutional_risk`. The template job uses **`low_risk`**. **`constitutional_risk` is never run autonomously** — blocked locally with no execution.

Shared helper: [`lib/guard-preflight.mjs`](lib/guard-preflight.mjs) (`buildDecisionEnvelope`, `postGuardDecision`, …).

Environment:

| Variable | Purpose |
|----------|---------|
| `TEHUTI_GUARD_URL` | Tehuti Guard v1 base URL (default `http://127.0.0.1:8013`) |
| `SKIP_GUARD_PREFLIGHT` | If `1` / `true`, bypass Guard (**dev only**; logs a warning) |
| `MAAT_MACHINE_ID` | Machine id for envelopes (else `MAAT_DEVICE_ID` or hostname) |
| `FORGE_AGENT_ID` | Actor id for Guard (else `MAAT_AGENT_ID` or `maat-forge`) |
| `FORGE_CORRELATION_ID` | Optional stable id for cross-system stitching; if unset, Forge generates `corr-<uuid>` per job |
| `FORGE_SESSION_ID` | Optional stable session id |
| `FORGE_TASK_ID` | Optional task id |
| `MAAT_IMMUNE_LOG` | Same JSONL path as `maat-runtime` MAAT Immune extension (input tail) |
| `FORGE_REPORT_DIR` | Override report directory (default: `maat-forge/reports`) |
| `FORGE_LOG_MEMORY` / `MAAT_GOVERNANCE_MEMORY` | Set `1` / `true` to write compact **`forge_preflight`** rows to PostgreSQL (`maat_governance_events`) via [`../maatlangchain/scripts/log_governance_event.py`](../maatlangchain/scripts/log_governance_event.py) — requires **`PGVECTOR_DB_URL`** |
| `MAAT_LOG_GOVERNANCE_SCRIPT` | Override path to `log_governance_event.py` |
| `PYTHON` | Python binary for the governance script (default `python3`) |

Rows include **`explanation_id`** and **`matched_rules`** from Guard’s **`POST /decision`** when present (same correlation as `/explain` without an extra call).

For preflight to return **`allow`**, run **Sentinel** (4242) and **Guard** (8013) so Guard can fetch `GET {Sentinel}/status/{machine_id}`; align `MAAT_MACHINE_ID` with your doctor/Sentinel identity.

## Immune alignment

- **No sacred mutation** — job only reads logs and writes under `reports/`.
- **Promotion** — repair candidates are **stubs**; real promotion goes through human approval + Guard (see immune doc §5.3).
