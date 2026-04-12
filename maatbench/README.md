# MaatBench v2 (legacy root copy)

> **Deprecated path.** Canonical bench + contracts for the **Ka-body** live under **[`../maat-ecosystem/maatbench/`](../maat-ecosystem/maatbench/)**.  
> This **root-level** `maatbench/` exists from an older standalone repo merge — **do not** diverge it with new suites; add work under `maat-ecosystem/maatbench/` instead.  
> See [`../archive/README.md`](../archive/README.md).

---

# MaatBench v2

**System-level verification for the MAAT ecosystem.**

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

## Run

```bash
python3 -m maatbench.run                    # run all tests
python3 -m maatbench.run --category policy  # run one category
python3 -m maatbench.run --report json      # output JSON report
python3 -m maatbench.run --verbose          # show each test result
```

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
