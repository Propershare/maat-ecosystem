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
| 6 | Behavior Balance | Model uses tools when needed, converses when not |
| 7 | Learning Safety | Snapshots required, approval gated, rollback restores state |

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

# Contract / schema tier only — works without the optional `maat_core` package:
python3 -m maatbench.run --category contract_integrity --verbose

# Full suite — requires `maat_core` (policy, events, portability, …):
python3 -m maatbench.run                    # run all tests
python3 -m maatbench.run --category policy_fidelity
python3 -m maatbench.run --report json      # output JSON report
python3 -m maatbench.run --verbose          # show each test result
```

**Tehuti Lab one-shot** (from monorepo root): `bash scripts/run-tehuti-local-tests.sh`

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
