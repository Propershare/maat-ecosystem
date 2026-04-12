# First run — Guard + Sentinel (5-minute sanity path)

**Purpose:** A **stranger** can **prove** plumbing before trusting high-impact routes: health → sample `/decision` → **correlation id** echoed → optional logs join.

**Before commands:** If you want **plain-language placement** first (no stack jargon), read [`INITIATION.md`](INITIATION.md).

**Prerequisites:** Python venv with `tehuti-guard` and `maat-sentinel` installed (`pip install -e ./tehuti-guard/guard`, `pip install -e ./maat-sentinel`), or your equivalent.

---

## 1. What gets initialized on “first call”

| Component | First-call behavior |
|-----------|---------------------|
| **maat-sentinel** | Creates/uses state under `MAAT_SENTINEL_STATE_DIR` (default `~/.maat/sentinel/`). HTTP `/status/<id>` may return empty/minimal view until ingest. |
| **Tehuti Guard** | No database required. **Correlation id:** if you omit it, Guard **generates** a UUID and **echoes** it on the response. |
| **OpenClaw gateway** | **Does not** auto-configure Guard URLs for tool calls. **maat-immune** is **local** unless you add HTTP client wiring. |

There is **no** special registration handshake between OpenClaw and Guard in the **stock** tree — document your fork if you add one.

---

## 2. Order of operations (recommended)

1. **Start Sentinel** (4242):

   ```bash
   maat-sentinel serve --host 127.0.0.1 --port 4242
   ```

2. **Start Guard** (8013), pointing at Sentinel (default is already `http://127.0.0.1:4242`):

   ```bash
   export TEHUTI_GUARD_SENTINEL_URL=http://127.0.0.1:4242
   tehuti-guard-serve --host 127.0.0.1 --port 8013
   ```

3. **Health check**

   ```bash
   curl -s http://127.0.0.1:8013/health
   curl -s http://127.0.0.1:4242/machines
   ```

4. **Sample `/decision`** (low-risk envelope to get an **`allow`** or **`review`** depending on posture):

   ```bash
   curl -s -X POST http://127.0.0.1:8013/decision \
     -H 'Content-Type: application/json' \
     -H 'X-Correlation-ID: first-run-test-001' \
     -d '{
       "machine_id": "workstation-01",
       "actor": {"id": "test", "role": "agent"},
       "action": {"kind": "read", "resource": "/tmp/x", "risk": "low"}
     }'
   ```

5. **Confirm:** Response JSON includes **`correlation_id": "first-run-test-001"`** (or your body field) and a **`decision`** string from the [canonical set](ENDPOINTS-AND-DECISIONS.md#1-canonical-decision-vocabulary-read-this-first).

6. **Optional: explain** (same body, diagnostic)

   ```bash
   curl -s -X POST http://127.0.0.1:8013/explain \
     -H 'Content-Type: application/json' \
     -d @- <<'EOF'
   {
     "machine_id": "workstation-01",
     "actor": {"id": "test", "role": "agent"},
     "action": {"kind": "read", "resource": "/tmp/x", "risk": "low"}
   }
   EOF
   ```

   **`explanation_id`** should match **`POST /decision`** for the same envelope + policy + matched rules (see `tehuti-guard/guard/README.md`).

7. **Sentinel down test** (optional): stop Sentinel, repeat `/decision` — expect **`review`** and **`sentinel_unreachable`** style reason (see [`tehuti-guard/guard/README.md`](../tehuti-guard/guard/README.md)).

---

## 3. What “working” looks like

- **`GET /health`** returns `ok: true` on Guard.  
- **`POST /decision`** returns **`200`** with `decision`, `matched_rules`, `correlation_id`, `policy_version`.  
- **Same `correlation_id`** you sent is **echoed** (or generated once).  
- **Forge** (if used): `POST /decision` preflight succeeds when policy allows — see [`maat-forge/README.md`](../maat-forge/README.md).

---

## 4. Only then enable high-impact routes

After the loop above:

1. Wire **one** adapter path to **normalize** tool calls into the envelope and call **`POST /decision`**.  
2. Enforce **`decision`** without downgrade — see [`TEHUTI-SENTINEL-GUARD-ADAPTER-CONTRACT.md`](TEHUTI-SENTINEL-GUARD-ADAPTER-CONTRACT.md) §6.  
3. Turn on **`TEHUTI_GUARD_MEMORY=1`** only when Postgres is ready so joins hit **governance** rows.

---

## Related

- [`SETUP-WITH-AGENT.md`](SETUP-WITH-AGENT.md) — **human-first**: what to tell the agent, initiation questions, copy-paste prompts  
- [`SYSTEM-CONNECTIONS.md`](SYSTEM-CONNECTIONS.md)  
- [`ENDPOINTS-AND-DECISIONS.md`](ENDPOINTS-AND-DECISIONS.md)  
