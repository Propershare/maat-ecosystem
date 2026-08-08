# maat-sentinel (v1–v2 scaffold)

Minimal **live awareness** layer: ingest **maat doctor** snapshots, **maat-immune** JSONL events, and **presence** heartbeats; surface a unified JSON view per `machine_id`. Optional **HTTP API** for multi-host reporting.

**Doctrine:** Sentinel stays **live / operational** — append-only local JSONL for short retention; **long durable history** belongs in **maat-memory** / gitMaat, not unbounded Sentinel files.

## Record envelope (every JSONL line)

Each stored line is wrapped for evolution safety:

| Field | Meaning |
|--------|---------|
| `source` | `maat-sentinel` |
| `schema_version` | Wrapper version (`1`) |
| `ingested_at` | When Sentinel accepted the record (ISO UTC) |
| `record_type` | `doctor_snapshot` \| `immune_event` \| `presence` |
| `payload` | Typed payload + `payload_schema` |

Legacy flat lines (no wrapper) are still readable via `unwrap_row`.

## Canonical presence (`payload_schema` `.../presence/v1`)

| Field | Meaning |
|--------|---------|
| `machine_id` | Host identity |
| `runtime` | e.g. `maat-runtime` |
| `session_id` | Optional session key |
| `status` | e.g. `active`, `idle`, `unknown` |
| `last_seen_at` | ISO heartbeat time |

## Unified view (`unified_view`)

Includes:

- `machine_status` — `operational` \| `degraded` \| `unsafe` \| `constitutional_breach`
- `risk_summary`, `requires_human_review`
- `immune_summary` — recent constitutional / critical / blocked counts, `last_immune_event_at`
- `doctor`, `immune_recent`, `presence`

## Retention / compaction (policy)

- **Default:** raw JSONL grows unbounded until you rotate or truncate.
- **Recommended:** keep **7–30 days** of local JSONL for debugging; **compact** older lines to summaries or delete; ship **summaries** to maat-memory for durable audit.
- **Sentinel** should remain **live-state-focused**; do not treat it as the system of record for all immune history.

## Install

```bash
pip install -e ./maat-sentinel
```

## State

Default: `~/.maat/sentinel/*.jsonl`  
Override: `MAAT_SENTINEL_STATE_DIR`

## Environment

| Variable | Effect |
|----------|--------|
| `MAAT_SENTINEL_PORT` | Default HTTP port for `serve` (default **4242** if unset) |
| `MAAT_SENTINEL_STATE_DIR` | JSONL directory override |
| `MAAT_SENTINEL_MEMORY` | Set `1` / `true` to write compact governance rows to PostgreSQL (`maat_governance_events`): **`sentinel_posture_summary`** when unified-view fingerprint changes after ingest; **`sentinel_immune_alert`** for constitutional-severity immune events |
| `MAAT_WORKSPACE_ROOT` | Lab root containing `maatlangchain/` — used to import `maat_memory` |

See [`docs/MAAT-GOVERNANCE-RETENTION.md`](MAAT-GOVERNANCE-RETENTION.md) for retention intent.

**Doctrine:** **4242** is the conventional Sentinel port (see [`docs/MAAT-PRODUCT-MAP.md`](../docs/MAAT-PRODUCT-MAP.md#default-ports-lab-network-identity)). CLI `--port` still wins over the env default.

## CLI

```bash
maat-sentinel ingest-doctor /tmp/doctor.json
tail -f ~/.maat/immune.jsonl | maat-sentinel ingest-immune-stdin
maat-sentinel status --machine-id workstation-01
maat-sentinel ingest-doctor-pipe
maat-sentinel serve --host 0.0.0.0 --port 4242
```

## HTTP API (v2)

| Method | Path | Body |
|--------|------|------|
| GET | `/machines` | — |
| GET | `/alerts` | — |
| GET | `/status/<machine_id>` | — |
| POST | `/doctor` | Doctor JSON (maat doctor --json) |
| POST | `/immune` | One envelope object or array of objects |
| POST | `/presence` | Presence JSON (`machine_id`, `runtime`, `status`, …) |

Example:

```bash
curl -s http://127.0.0.1:4242/machines
curl -s http://127.0.0.1:4242/status/workstation-01
curl -s -X POST http://127.0.0.1:4242/doctor -H 'Content-Type: application/json' -d @doctor.json
```

## Python

```python
from maat_sentinel.ingest import ingest_doctor_json, ingest_presence
from maat_sentinel.models import PresenceRecord
from maat_sentinel.surface import unified_view

ingest_presence(PresenceRecord(
    machine_id="w1",
    runtime="maat-runtime",
    session_id=None,
    status="active",
    last_seen_at="2026-04-10T12:00:00Z",
))
print(unified_view("w1"))
```

## Immune envelope

Runtime events should include top-level **`machine_id`** (maat-runtime `maat-immune` v1.1+, env `MAAT_MACHINE_ID`).
