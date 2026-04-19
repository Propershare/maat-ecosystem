# Runtime hookup (full lab spine)

This ties together the connectivity freeze, gitMaat, and operator surfaces. **No secrets** belong in this repo—use `.env` and `~/.openclaw/openclaw.json` on the host only.

**Maturity:** This page is **lab-oriented**: **smoke checks**, **manual curl paths**, and **reference demos**. It does **not** claim production SLOs, hardened channel integration, or “everything wired end-to-end” unless a line explicitly says so.

## You are connected when

| Surface | Connected means | See |
|--------|-----------------|-----|
| **Telegram** | Telegram → OpenClaw gateway; channel policy matches your allowlist | Repo overview: [`README.md`](../README.md). Local-only operator notes may exist in `AGENTS.md` on disk. |
| **Cursor** | This lab root is the opened workspace; MCP points at live organs (discovery / memory) | `docs/GITMAAT-CONNECT.md`, Cursor **Settings → MCP** |
| **OpenClaw** | `agents.defaults.workspace` is this lab root; gateway process up (default **18790**) | Repo overview: [`README.md`](../README.md) (and `docs/GITMAAT-CONNECT.md`). Local-only operator notes may exist in `AGENTS.md` on disk. |
| **MCP / Ka spine** | **8010** manifest, **8014** Tehuti Core, **8022** Maat Memory MCP respond | [`docs/MAAT-ECOSYSTEM-CONNECTIVITY-FREEZE.md`](MAAT-ECOSYSTEM-CONNECTIVITY-FREEZE.md) §3 |
| **Postgres / gitMaat** | `PGVECTOR_DB_URL` (or equivalent) is loaded where scripts and MCP run; DB reachable | [`docs/GITMAAT-CONNECT.md`](GITMAAT-CONNECT.md) |

Stack layers (what “full system” is): same diagram and narrative as the freeze doc—[`docs/MAAT-ECOSYSTEM-CONNECTIVITY-FREEZE.md`](MAAT-ECOSYSTEM-CONNECTIVITY-FREEZE.md).

## Run the check (smoke)

**Smoke check** — From the lab root (after `source .env` if you want **Postgres** `pg_isready` when `PGVECTOR_DB_URL` or `PGHOST` is set):

```bash
./scripts/lab-runtime-check.sh
# or from another machine that can reach the LAN IP:
LAB_HOST=192.168.4.21 ./scripts/lab-runtime-check.sh
```

The script reports **PASS/FAIL** for discovery (8010), Tehuti Core (8014), Maat Memory MCP (8022), and optional Guard (8013), Sentinel (4242), gateway (18790), and Postgres. **Critical** failures are 8010 + 8014 + 8022; exit code **2** if any of those fail.

**Smoke check (Guard, when 8013 is up):** If `GET /health` on **8013** returns **2xx**, the script also sends a **low-risk** `POST /decision` (same envelope class as [`FIRST-RUN.md`](FIRST-RUN.md) §2) with header **`X-Correlation-ID`**, then asserts **HTTP 200**, a non-empty string **`decision`**, and **`correlation_id`** echoed to that value (requires **`python3`** on the host). Set **`LAB_SKIP_GUARD_DECISION=1`** to skip this smoke test. Optional **`LAB_GUARD_CORRELATION_ID`** fixes the correlation string for your own log joins while testing. This is **operator smoke**, not a production monitoring probe.

## OpenClaw → organs (HTTP MCP)

**Integration maturity:** OpenClaw does **not** automatically call **8014** / **8022**; you wire **mcporter** (or equivalent HTTP MCP) as **operator configuration**. That is **documented wiring**, not a guaranteed production-hardened integration unless you add ops controls (auth, network policy, retries) yourself. Same pattern as [`docs/GITMAAT-CONNECT.md`](GITMAAT-CONNECT.md)—do **not** paste `KA_API_KEY` into the repo. Step-by-step context: freeze **§3** and [`openclaw/skills/mcporter/SKILL.md`](../openclaw/skills/mcporter/SKILL.md).

## Cursor MCP

Use **Cursor Settings → MCP**. Prefer Ka discovery **8010** `/manifest` for live `organs.*.endpoint` URLs, or fixed LAN URLs consistent with [`docs/GITMAAT-CONNECT.md`](GITMAAT-CONNECT.md).

## Guard `POST /decision`: smoke check vs lab demo (reference)

**Smoke check:** [`scripts/lab-runtime-check.sh`](../scripts/lab-runtime-check.sh) proves **`POST /decision` returns 200** with **`correlation_id`** echo and a **`decision`** field when Guard is reachable—**lab/operator smoke** while Sentinel/Guard are running.

**Lab demo (reference script, Ma’at audit §6):** [`scripts/guard_adapter_e2e_demo.py`](../scripts/guard_adapter_e2e_demo.py) implements **envelope → `POST /decision` → enforce (`allow` only proceeds) → append JSONL** under **`logs/guard_adapter_e2e.jsonl`** with the same **`correlation_id`** as the request and response (joinable with Guard logs / optional `maat_governance_events` when `TEHUTI_GUARD_MEMORY=1`). This is **not** a production tool-caller—it is **repeatable lab proof** of the constitutional loop.

```bash
# Terminal 1: Guard (and ideally Sentinel on 4242)
cd tehuti-guard/guard && pip install -e . && tehuti-guard-serve --host 127.0.0.1 --port 8013

# Terminal 2: demo (from lab root)
python3 scripts/guard_adapter_e2e_demo.py
python3 scripts/guard_adapter_e2e_demo.py --dry-run   # envelope only, no HTTP
```

**Production integration (not included here):** Wire the same pattern from a **real channel adapter** (OpenClaw tool hook, IDE, etc.) with your own ops story; contracts: [`docs/ENDPOINTS-AND-DECISIONS.md`](ENDPOINTS-AND-DECISIONS.md), [`docs/TEHUTI-SENTINEL-GUARD-ADAPTER-CONTRACT.md`](TEHUTI-SENTINEL-GUARD-ADAPTER-CONTRACT.md). Tracked checklist: [`docs/MAAT-AUDIT-ACTION-PLAN.md`](MAAT-AUDIT-ACTION-PLAN.md).

## See also

- [`docs/LAB-CANONICAL-TREE-AND-STACK.md`](LAB-CANONICAL-TREE-AND-STACK.md) — canonical **folder tree**, **symlinks**, and **tech stack** for GitHub / operators.
