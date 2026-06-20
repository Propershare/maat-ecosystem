# Lab bench workflow — atomic multi-agent testing

One command exercises the **whole agent lab**: MCP spine, OpenClaw, MAAT Gateway, Hermes skills, gemma4 swarm pytest, and MaatBench (including **`lab_spine`** category for registry triad + agent paths).

## Quick run

```bash
cd /home/suspect/.n8n
bash scripts/run-lab-bench-workflow.sh
```

With live Ollama/Gemma smoke:

```bash
LAB_BENCH_LIVE=1 bash scripts/run-lab-bench-workflow.sh
```

## What gets tested

| Tier | Target | Agents / organs |
|------|--------|-----------------|
| 0 | `lab-runtime-check.sh` | Ka 8010, Tehuti Core 8014, Memory 8022, Guard 8013, Sentinel 4242, OpenClaw 18790, Postgres |
| 0b | `:8040/health` | MAAT Gateway (scout, analyst, archivist, ka2-research, fl-trust-law) |
| 1 | `pytest gemma4-toolshim/swarm/tests/` | Gateway server, archivist, KA2 router, guard validator, forge |
| 2 | `python3 -m maatbench.run` | 58 contract/policy/memory/event tests + **10 lab_spine** checks |
| 3 | Optional `LAB_BENCH_LIVE=1` | Gemma e2b/e4b via Ollama |
| 4 | Hermes skills dir | `last30days`, `tehuti-research-memory` under `HERMES_SKILLS_ROOT` |
| 5 | `openclaw agents list` | OpenClaw agents (`main`, `ka2-research`, …) when CLI + gateway up |

## Agent map (do not collapse)

| Surface | Port | Role |
|---------|------|------|
| **OpenClaw** | 18790 | Channels, cron, hooks, tool execution, Hermes skills |
| **MAAT Gateway** | 8040 | Governed expert turns → archivist record + guard |
| **Swarm bridge** | 18080 | Alternative Telegram/router path |
| **Hermes skills** | disk | `/mnt/data_drive/hermes/skills/` (research pipeline) |
| **Cursor** | IDE | Same workspace; runs identical bench script |
| **MaatBench** | CLI | Verification organ — scores + JSON artifacts |

Scout / Analyst / Archivist are **roles** in `expert_config.py` and **gateway ids** in `registry.yaml`; OpenClaw preset **`ka2-research`** binds the research agent.

## Reports

| Artifact | Path |
|----------|------|
| **MaatBench Evidence Record** (formal) | `appendices/evidence-records/maatbench-evidence-record-*.json` |
| MaatBench JSON (backward compat) | `appendices/lab-bench-YYYY-MM-DD.json` |
| Workflow log | `logs/lab-bench-YYYY-MM-DD.log` |
| Workflow state (internal) | `logs/lab-bench-YYYY-MM-DD-state.json` |

Schema: [`maat-ecosystem/maatbench/evidence/SCHEMA.md`](../maat-ecosystem/maatbench/evidence/SCHEMA.md)

Each atomic run emits a **MaatBench Evidence Record** with git commit, machine_id, pass/fail/skip counts, optional-service rationale, `report_hash` (SHA-256 of MaatBench JSON), six-principle `maat_interpretation`, and `justice_exemplars`.

## Automation (atomic workflow on a schedule)

### Option A — systemd (recommended on staydangerous)

```bash
bash scripts/setup-lab-bench-automation.sh systemd
```

Installs `lab-bench-workflow.timer` → daily **07:00** (see `systemd-services/`).

### Option B — OpenClaw cron

Requires gateway running:

```bash
bash scripts/setup-lab-bench-automation.sh openclaw
```

Registers job **`lab-bench-daily`** that executes the same bash script.

### Status

```bash
bash scripts/setup-lab-bench-automation.sh status
```

## MaatBench categories

```bash
cd maat-ecosystem
python3 -m maatbench.run --category lab_spine --verbose
python3 -m maatbench.run --verbose   # all categories
```

**`lab_spine`** optional checks (OpenClaw, Gateway, Hermes, Ka discovery) **pass with a skip note** when organs are down — suitable for nightly cron without failing the whole run.

## Next tier (roadmap)

- **`triad_live`:** HTTP scout → analyst → archivist chain on `:8040` with shared `session_id` (requires Ollama)
- **Guard/Sentinel E2E:** correlation scenarios from `docs/MAATBENCH-v2.md` §7
- **Hermes artifact bench:** after `last30days` run, assert `artifact.yaml` + gitMaat row

## See also

- [`docs/MAATBENCH-v2.md`](MAATBENCH-v2.md)
- [`docs/N8N-RETIRED.md`](N8N-RETIRED.md) — OpenClaw replaces n8n for automation
- [`docs/SCOUT-ANALYST-ARCHIVIST.md`](SCOUT-ANALYST-ARCHIVIST.md)
- [`scripts/run-tehuti-local-tests.sh`](../scripts/run-tehuti-local-tests.sh) — lighter smoke (delegates to full workflow)
