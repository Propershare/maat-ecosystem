# MaatBench Evidence Record — schema v1

Formal JSON artifact emitted by `scripts/run-lab-bench-workflow.sh` after each atomic lab bench run.

**Formal name:** MaatBench Evidence Record  
**Informal label:** Evidence Packet (dissertation Appendix H)

## Required fields

| Field | Type | Description |
|-------|------|-------------|
| `schema_version` | string | e.g. `"1.0.0"` |
| `record_type` | string | `"MaatBench Evidence Record"` |
| `run_id` | string | Unique audit identifier |
| `timestamp` | string | ISO 8601 UTC end time |
| `started_at` | string | ISO 8601 UTC start time |
| `duration_seconds` | number | Wall-clock run duration |
| `git_commit` | string | `git rev-parse HEAD` or `"unknown"` |
| `branch` | string | Current git branch |
| `machine_id` | string | `MAAT_MACHINE_ID` or hostname |
| `operator` | string | `MAAT_OPERATOR` or `$USER` |
| `script_invoked` | string | Workflow command path |
| `environment` | object | OS, Python, lab root summary |
| `services_checked` | array | Port/service probes with status |
| `optional_services_down` | array | `{service, rationale}` for skipped optional organs |
| `pytest` | object | `{passed, failed, skipped, errors, exit_code}` |
| `maatbench` | object | Pass/fail/skip counts + categories |
| `categories_tested` | array | MaatBench category ids |
| `artifact_paths` | object | Paths to JSON, log, state, this record |
| `report_hash` | string | SHA-256 of MaatBench JSON report (hex) |
| `maat_interpretation` | object | Six principles → short audit notes |
| `justice_exemplars` | array | allow / review / deny-or-escalate examples if available |
| `limitations` | array | Explicit scope limits of this run |
| `workflow_status` | string | `"ok"` \| `"failed"` |

## See also

- [`docs/LAB-BENCH-WORKFLOW.md`](../../../../docs/LAB-BENCH-WORKFLOW.md)
- Output directory: `docs/Maat-Constitutional-Infrastructure-Dissertation/appendices/evidence-records/`
