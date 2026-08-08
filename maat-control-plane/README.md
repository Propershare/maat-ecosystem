# MAAT Control Plane (Python)

**Version:** 0.3.1 — **`maat doctor`** is a real **machine truth reader**; **`maat governance`** queries durable governance history; other subcommands remain stubs.

**Doctrine:** [`docs/MAAT-LAB-CONTROL-PLANE.md`](../docs/MAAT-LAB-CONTROL-PLANE.md) · performance: [`docs/MAAT-LIGHTWEIGHT-INTELLIGENCE.md`](../docs/MAAT-LIGHTWEIGHT-INTELLIGENCE.md)

## Install

```bash
pip install -e ./maat-control-plane
maat --version
```

## `maat doctor`

Inspects identity, manifest/profile load, sacred/managed/volatile/user paths, gateway (OpenClaw config + permissions + workspace vs lab), runtime dir, endpoints (memory MCP / Tehuti / Sentinel / Ka discovery — absent by design unless set), stack (Python/Node/Ollama), DB/Redis, and dangerous env vars. Emits:

- **Human** summary (default): pass / warn / fail per check + suggested actions  
- **JSON** (`--json`): `schema: maat-control-plane/doctor-report/v2.1` — adds `pass_count` / `warn_count` / `fail_count` / `constitutional_count`, `machine_trust_posture` (`trusted` \| `degraded` \| `unsafe` \| `constitutional_breach`), `blocking_actions` (short imperative list), plus per-check `severity`, `constitutional`, `recommended_action`, `install_mode`, `reconciliation`  

Exit code **1** if `overall_status` is `fail` (e.g. missing sacred path, `MAAT_IMMUNE_ALLOW_SACRED=1`).

### Discovery

- **Lab root:** `MAAT_LAB_ROOT`, or walk up from cwd until `maat-ecosystem/` exists  
- **Manifest:** `MAAT_MACHINE_MANIFEST`, or first of `~/.maat/config/machine.{yaml,yml,json}`, `/etc/maat/machine.{yaml,json}`  
- **Profile:** `MAAT_PROFILE`, or `~/.maat/config/profile.{yaml,yml,json}`  

### Manifest `endpoints` (optional)

If `machine.yaml` includes `endpoints`, doctor probes TCP for each configured service (defaults in parentheses):

```yaml
endpoints:
  memory_mcp: "127.0.0.1:8022"   # Maat Memory MCP
  tehuti_core: 8014              # Tehuti Core (localhost)
  sentinel: null                 # absent by design
  ka_discovery: "http://127.0.0.1:8010"
```

Override per run with: `MAAT_DOCTOR_MEMORY_MCP`, `MAAT_DOCTOR_TEHUTI`, `MAAT_DOCTOR_SENTINEL`, `MAAT_DOCTOR_KA_DISCOVERY` (URL or `host:port`).

### Path classes (optional)

`managed_paths`, `volatile_paths`, and `user_paths` in the manifest override defaults (`<lab>/maat-runtime`, `~/.maat/cache`, `~/.maat/config`).

### Install mode

`install_mode` (or `machine_kind` / `node_kind`) and `role` drive contextual checks — e.g. **`sentinel_policy_server`** warns when `install_mode` / `role` implies a server-class host but Sentinel code is missing under the lab root.

### Reconciliation

If the manifest lists **`protected_services`**, **`managed_services`**, or **`remote_services`**, the JSON report includes a **`reconciliation`** table: expected vs observed (gateway config, guard repo, sentinel, `maat-runtime`, remote stubs).

### Environment (optional)

| Variable | Effect |
|----------|--------|
| `MAAT_DOCTOR_SKIP_OLLAMA=1` | Skip Ollama HTTP check |
| `MAAT_DOCTOR_*` | See endpoint overrides above |

### Example

```bash
export MAAT_LAB_ROOT=/path/to/tehuti-lab
maat doctor
maat doctor --json | jq .overall_status
```

## `maat governance`

Reads **`maat_governance_events`** (PostgreSQL) — rows from Tehuti Guard, Forge, Sentinel when memory logging is enabled. Requires **`PGVECTOR_DB_URL`** and **`MAAT_WORKSPACE_ROOT`** (or run from the lab tree so `maatlangchain/` is discoverable). Uses **`psycopg2`** via `maat_memory` (install from `maatlangchain` / your env).

```bash
export PGVECTOR_DB_URL=...
export MAAT_WORKSPACE_ROOT=/path/to/lab   # e.g. ~/.n8n

maat governance recent
maat governance recent --limit 50 --json
maat governance machine workstation-01
maat governance correlation corr-xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

Human output prints a compact table plus counts by `source_service` and `record_type` in the result set. **`correlation`** returns rows **oldest first** (lifecycle order).

## Other commands

| Command | Status |
|---------|--------|
| `maat setup` | Stub |
| `maat repair` | JSON skeleton report |
| `maat enroll` | Stub |

## Dependencies

- **PyYAML** — for YAML manifests/profiles
- **PostgreSQL + psycopg2 + maat_memory** — only for `maat governance` (optional)
