# maatbench/suites — lived-truth fixtures

Fixtures here must trace to real events:

| Subfolder | Source of truth |
| --- | --- |
| `gateway_contract/` | Captured `maat.archivist_record.v1` records under `logs/archivist/records.jsonl` |
| `policy/` | `guard_cases/*.json` at the lab root |
| `memory/` | gitMaat rows (`maat_changes`, `maat_decisions`, `maat_learnings`) |
| `models/` | Per-gateway regression sets derived from the above |

Adding a fixture requires a correlation id (for records), a guard_case id, or
a gitMaat id. Silent deletion of a failing fixture is a Guard-denied action
per `docs/MAAT-EVOLUTION-LANES.md` Lane 6.

Run the gateway-contract suite:

```
python3 -m maatbench.run --category gateway_contract --verbose
```

Run the lived-truth policy suite (mirrors `guard_cases/`):

```
python3 -m maatbench.run --category gateway_policy --verbose
```
