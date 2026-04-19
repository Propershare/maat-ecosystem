# Endpoints and decisions (wire contract)

**Purpose:** Plain tables for **Guard v1** and **maat-sentinel** HTTP — request/response shape, **canonical decision vocabulary**, failure behavior, and BYO notes. **No philosophy** — integration facts.

**Companion:** [`FIRST-RUN.md`](FIRST-RUN.md) (curl order), [`SYSTEM-CONNECTIONS.md`](SYSTEM-CONNECTIONS.md) (who calls whom).

---

## 1. Canonical decision vocabulary (read this first)

**Wire values** for Tehuti Guard v1 `POST /decision` and `POST /explain` are **exactly** (Python `DecisionKind`):

`allow` | `deny` | `review` | `quarantine` | `escalate`

**Doctrine / docs** sometimes say **“conditional”** meaning: *proceed only if extra gates pass*. On the wire today, that is **not** a separate string. Use this mapping:

| Doctrine / review doc term | Wire value in Guard v1 | Meaning |
|----------------------------|-------------------------|--------|
| **Allow** | `allow` | Proceed. |
| **Deny** | `deny` | Block. |
| **Conditional** (human-in-the-loop gate) | **`review`** (or **`quarantine`** when posture is breach) | **Hold** until policy says otherwise; **not** a silent allow. |
| **Quarantine** | `quarantine` | **Isolate / hold** — stronger than “needs review” in some posture paths. |
| **Escalate** | `escalate` | Human or higher authority required; adapters **must not** downgrade. |

**Rule:** New connectors **must not** emit or expect `conditional` on the wire until the API adds it. Map your UI labels to **`review` / `quarantine`** and document `matched_rules`.

---

## 2. `blocking_actions` (operational)

`blocking_actions` in the JSON response is a **list of strings** from Sentinel’s **`unified_view.blocking_actions`** (may be empty). Treat as **machine-readable hints** from posture (e.g. remediation steps). **Adapters** should not invent them; they **must** still enforce **`decision`** as the authority.

---

## 3. Tehuti Guard (Python decision API, lab) — `http://127.0.0.1:8013` default

| Endpoint | Caller | Purpose | Required fields | Response shape | Rate limit | Auth | Failure / idempotency |
|----------|--------|---------|-----------------|----------------|------------|------|------------------------|
| `GET /health` | Operator, load balancers | Liveness | — | `{ ok, service, version }` | **None** | **None** | **200** if process up. |
| `GET /policy-version` | Operator, CI | Policy string | — | `{ policy_version }` | **None** | **None** | **200** |
| `GET /rules` | Operator, Studio | Rule catalog (aligned with `evaluate()`) | — | JSON document | **None** | **None** | **200** |
| `POST /decision` | Adapters, Forge | **Operational** decision | JSON body → `DecisionRequest` (below) | Decision + `matched_rules`, `explanation_id`, `correlation_id`, `policy_version` | **None** | **None** | **Not** idempotent if Sentinel view changes between calls. **400** on bad JSON/envelope. |
| `POST /explain` | Operator, Studio | Diagnostics / same logic as decision | Same as `/decision` | Explain envelope + `correlation_id` | **None** | **None** | **Advisory** — do not execute from prose; use structured `decision`. |

**Timeouts / retries:** Not enforced inside the minimal `ThreadingHTTPServer` handler — **client must** set HTTP timeouts. **Retry** is safe only if your operation is idempotent **or** you use the same `correlation_id` for tracing.

### `POST /decision` — request body (single envelope)

```json
{
  "machine_id": "workstation-01",
  "actor": { "id": "cursor_staydangerous", "role": "agent" },
  "action": {
    "kind": "write",
    "resource": "/path/to/file",
    "risk": "low"
  }
}
```

- `correlation_id` optional in body; else header `X-Correlation-ID`; else server generates UUID.  
- `risk`: `low` | `medium` | `high` | `protected`  
- `kind`: e.g. `read`, `write`, `execute`, `deploy`, `delete`

### Example `200` response

```json
{
  "decision": "allow",
  "severity": "info",
  "reason": "Operational posture; low-risk action allowed",
  "tags": ["allow"],
  "blocking_actions": [],
  "matched_rules": ["operational_low_risk_allow"],
  "explanation_id": "sha256:…",
  "correlation_id": "uuid-or-client-supplied",
  "policy_version": "1",
  "sentinel_url": "http://127.0.0.1:4242"
}
```

Full detail and examples: [`tehuti-guard/guard/README.md`](../tehuti-guard/guard/README.md).

---

## 4. maat-sentinel HTTP — `http://127.0.0.1:4242` default

Guard calls **`GET /status/<machine_id>`** (via its Sentinel client) to build `unified_view`. Operators and other tools may use:

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/machines` | List machines |
| GET | `/alerts` | Alerts |
| GET | `/status/<machine_id>` | Unified view for machine |
| POST | `/doctor` | Ingest doctor JSON |
| POST | `/immune` | Ingest immune event(s) |
| POST | `/presence` | Presence heartbeat |

See [`maat-sentinel/README.md`](../maat-sentinel/README.md).

---

## 5. Gateway / OpenClaw (honest status)

| Question | Answer today |
|------------|----------------|
| Dedicated “Guard registration” endpoint on OpenClaw? | **Not documented** as a first-class handshake. Gateway uses **workspace** config (repo-level: [`README.md`](../README.md); see also `docs/GITMAAT-CONNECT.md`). |
| Gateway discovers Sentinel via Ka **8010** automatically for Guard? | **No** — Guard uses **`TEHUTI_GUARD_SENTINEL_URL`** (default `http://127.0.0.1:4242`). |
| First tool call → policy load? | **maat-immune** loads rules from **code** and env; **no** automatic HTTP Guard call on first tool. |

When integration lands, update this section with **exact** config keys.

---

## 6. BYO (bring your own)

| BYO | Supported? | Notes |
|-----|--------------|-----|
| **PostgreSQL** for governance | **Yes** when env enables memory sinks | `PGVECTOR_DB_URL` / workspace `.env`; rows need **`correlation_id`** for joins when both sides log. |
| **SQLite** for gitMaat | **Out of scope** for canonical gitMaat in this lab — **Postgres** is the documented default. |
| **Swap model feeding Sentinel** | **Yes** — ingest paths (`/doctor`, `/immune`) are the extension points. |
| **Custom MCP / tools** | **Yes** — normalize to **Guard envelope** for high-impact paths; local checks stay in adapters per [`TEHUTI-SENTINEL-GUARD-ADAPTER-CONTRACT.md`](TEHUTI-SENTINEL-GUARD-ADAPTER-CONTRACT.md). |

---

## Related

- [`TEHUTI-SENTINEL-GUARD-ADAPTER-CONTRACT.md`](TEHUTI-SENTINEL-GUARD-ADAPTER-CONTRACT.md) — what must hit `/decision`  
- [`MAAT-PRODUCT-MAP.md`](MAAT-PRODUCT-MAP.md) — ports  
