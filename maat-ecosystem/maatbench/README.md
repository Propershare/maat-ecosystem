# MaatBench v2

**System-level verification for the MAAT ecosystem.**

**North-star spec (standalone repo, API, suites, first 10 scenarios):** [`docs/MAATBENCH-v2.md`](../../docs/MAATBENCH-v2.md) (lab root).

Not "does the model answer well?" but "does the system preserve its guarantees under stress?"

## The 7 Guarantee Categories

| # | Category | What It Proves |
|---|----------|---------------|
| 1 | Contract Integrity | Schemas are valid, required fields present, versions compatible |
| 2 | Policy Fidelity | Forbidden actions denied, escalations triggered, no bypass |
| 3 | Memory Fidelity | Attribution exists, append-only honored, rollback works |
| 4 | Event Fidelity | Actions emit events, types canonical, logs reconstructable |
| 5 | Portability | Identity/memory/policy survive adapter swaps |
| 6 | Behavior Balance | Model uses tools when needed, converses when not *(optional — requires live model)* |
| 7 | Learning Safety | Snapshots required, approval gated, rollback restores state |
| 8 | Gateway Contract | KA2 archivist records, scorecard math, `pass_at=40` |
| 9 | Gateway Policy | Lived-truth `guard_cases/` round-trip through Guard validator |
| 10 | Lab Spine | OpenClaw, MAAT Gateway, Hermes skills, registry triad (multi-agent) |

## MAAT Score

```
MAAT Score = average(
    contract_integrity,
    policy_fidelity,
    memory_fidelity,
    event_fidelity,
    portability,
    behavior_balance,
    learning_safety
)
```

A score of 0.91 means: "This system is 91% MAAT-compliant."
That is a defensible, measurable claim.

**Public surfaces (websites, demos):** Always label **which tier** produced a score (e.g. `contract_integrity` only vs full suite with `maat_core`) and **when** (date or git SHA). A fixed “100%” or “49/49” on a landing page without that context is **not** Maat‑truthful.

## Run

Run from **`maat-ecosystem/`** (the parent of this folder). The module is `maatbench`, not `maatbench.run` as a path inside `maatbench/`.

```bash
cd maat-ecosystem

# Full suite — bootstraps lab paths (maat_core.kernel shim, maat_adapters symlink):
python3 -m maatbench.run                    # run all tests (9 categories, 68 tests)
python3 -m maatbench.run --category contract_integrity  # schema tier only
python3 -m maatbench.run --category gateway_contract    # KA2 archivist record validator
python3 -m maatbench.run --category gateway_policy      # guard_cases round-trip
python3 -m maatbench.run --report json      # output JSON report
python3 -m maatbench.run --verbose          # show each test result
```

**Tehuti Lab one-shot** (from monorepo root): `bash scripts/run-tehuti-local-tests.sh`

**Dissertation evidence record** (every atomic bench run):

```bash
bash scripts/run-lab-bench-workflow.sh
# → appendices/evidence-records/maatbench-evidence-record-*.json
```

Schema: [`evidence/SCHEMA.md`](evidence/SCHEMA.md)

## Structure

```
maatbench/
├── contracts/        ← Test definitions (structured JSON)
├── fixtures/         ← Test data (identities, memories, policies)
├── runners/          ← Test execution engines
├── scorers/          ← Scoring logic per category
├── reports/          ← Report generation
└── run.py            ← Single entry point
```
