# Raw chronicle (research layer)

**Rule:** Nothing here is automatically true—only recorded. Promote to [`../decisions/decisions_log.md`](../decisions/decisions_log.md) or the manuscript after the Ma’at check.

---

## Template

### YYYY-MM-DD

- **Source / context:** (conversation, PDF page, URL, lab observation)
- **Note:** (quote or paraphrase)
- **Open question:**

---

(Add entries below this line.)

---

### 2026-06-20 — Kilimanjaro essay on AI and mode-of-production transition

- **Source / context:** User pasted Dr. Tdka Kilimanjaro essay (Q&A follow-up on economics in the AI period); user "ase'" on analytical response; requested reading list, youth notes, dissertation tie-in.
- **Note:** Essay argues (1) societies have stage-specific "rules of motion," (2) AI/automation may produce structural not cyclical crisis for wage-labor capitalism, (3) ruling-class counterrevolution and minority scapegoating are historical patterns, (4) US racial division complicates class unity, (5) youth require researched truth not gimmicks.
- **Open question:** Authoritative UKMT edition/date for formal footnotes; whether Ch. 1 or Ch. 3 gets the single integrated paragraph in V1 prose.

---

### 2026-06-13 — Tehuti Guard build/test + governance audit (lab work)

- **Source / context:** Tehuti Lab agent sessions (Cursor agent `cursor_staydangerous`), repo `tehuti-guard/`, `maat-ecosystem/`. Captured from direct tool runs, not from chat assertion.
- **Note (verified):**
  - Python decision API (`tehuti-guard/guard/`) unit tests passed (`tests/test_rules.py`); in-process server smoke of `/decision` returned the fail-safe `review` when machine posture (Sentinel) was unavailable — i.e. it degraded to caution, not silent `allow`.
  - TS lab-helper package (`tehuti-guard/src/`, three-ring + LDAP) was **red** before fixes: `ldapjs` missing typings (TS2307), seven implicit-`any` errors, and a Vitest ESM load failure (`ERR_REQUIRE_ESM`). After fixes (indirect dynamic import + explicit `any` annotations in `ldap-policy.ts`; rename `vitest.config.ts` → `.mts`): `tsc` clean and 8/8 tests passing.
  - **Finding — "advertised-but-absent governance":** Ka Discovery `:8010/manifest` listed `organs.policy → :8013` while `:8013` was refusing connections and no `systemd` unit existed. The constitution was *published but unenforced*.
  - **Finding — silent contract drift:** `maat-runtime`'s `guard-client.ts` sends a flat `{actor, action, resource}` body, but the Guard API expects the nested envelope (`machine_id`, `actor{id,role}`, `action{kind,resource,risk}`). Such calls would 400 as `invalid_envelope` — a consumer *believing* it was governed while it was not.
  - Reproducible harness exists: `scripts/guard_adapter_e2e_demo.py` (envelope → `/decision` → enforce → JSONL with `correlation_id`).
  - CI added: `.github/workflows/tehuti-guard-ci.yml`; PR `Propershare/maat-ecosystem#1`.
  - Wire contract documented: `docs/TEHUTI-GUARD-WIRE-CONTRACT.md`.
- **Open question:** Is the green-vs-down inconsistency a deployment gap (no service manager) or a deeper ownership gap (no one accountable for keeping the gate live)? The dissertation should name this as a governance failure mode, not just a bug.

### 2026-06-06 — Tehuti Guard green end-to-end (gitMaat governance row)

- **Source / context:** `maat_governance_events` / gitMaat decision record, dated 2026-06-06.
- **Note (verified):** After Sentinel was started and presence posted, a Guard `/decision` call returned `allow` with rationale code `operational_low_risk_allow`. This is the **positive control** proving the gate works end-to-end when its dependencies are live.
- **Open question:** Capture exact request/response JSON for the evidence appendix (currently only the outcome is logged).

### 2026-06-13 — Maat Memory promoted from lab-local code to shared organ + client (lab work)

- **Source / context:** repos `maatlangchain/maat_memory/`, `maat-ecosystem/mcp-servers/maat-memory/`, new `maat-memory-client/`.
- **Note (verified):**
  - De-hardcoded `/home/suspect/.n8n` paths → env-driven resolution (`maatlangchain/maat_memory/paths.py`).
  - New self-installing Python client (`maat-memory-client/`): clean-venv install succeeded; auto-discovered the service at `http://192.168.4.21:8022` (env → Ka manifest → default); `doctor` self-diagnosis works; **graceful offline fallback** (no crash when service unreachable).
  - **Finding — auth/usability gap:** `:8022` MCP required a bearer key; client initially returned HTTP 401 until discovery was extended to read API keys from workspace `.env`.
  - Argument-mismatch bug fixed in `memory_log_conversation` / `memory_log_audit` MCP tools (server signature vs backend).
  - Wire contract + adoption docs: `docs/MAAT-MEMORY-WIRE-CONTRACT.md`, `docs/MAAT-MEMORY-ADOPTION.md`.
- **Open question:** Should memory writes also pass through Guard (publish/share actions) to fully realize "accountable memory under bounded authority"?

### 2026-06-15 — Live-probe attempt (HONESTY CAVEAT)

- **Source / context:** this session, attempted `curl`/urllib probes of `:8010 :8013 :8014 :8022 :4242`.
- **Note:** all returned DOWN/unreachable, **but the session was sandboxed with a loopback/network allowlist**. This is therefore **inconclusive** — NOT evidence the services are down. Do not cite the 2026-06-15 probe as a negative result. Re-probe outside the sandbox before any "current status" claim enters the manuscript.
- **Open question:** Resolved by later 2026-06-15 health sweep; see next entry and `../appendices/EVIDENCE-APPENDIX-2026-06-15.md`.

### 2026-06-15 — Un-sandboxed health sweep + exact Guard evidence

- **Source / context:** local HTTP probes from lab host; gitMaat / `maat_governance_events` query.
- **Note (verified):**
  - Current health sweep timestamp: `2026-06-15T14:29:51Z`.
  - Reachable: Ka Discovery `:8010`, Tehuti Core `:8014`, filesystem MCP `:8016`, Postgres MCP `:8017`, memory MCP `:8018`, ComfyUI MCP `:8019`, Maat Memory MCP `:8022`, OpenClaw gateway `:18790`, Ollama `:11434`.
  - Unreachable: Tehuti Guard `:8013`, maat-sentinel `:4242`.
  - Exact 2026-06-06 positive-control Guard row: `42c1c0d4-ce47-496c-b52f-66f51c5805d6`, timestamp `2026-06-06T14:52:03.698102+00:00`, decision `allow`, matched rule `operational_low_risk_allow`, correlation id `maat-security-stack:20260606T144720Z:3efa879b:guard-sentinel-smoke`.
  - Exact 2026-06-06 fail-safe row: `d8d4e16d-5537-4d15-a681-92a6aaa6184c`, decision `review`, matched rule `sentinel_unreachable_review`.
- **Open question:** Whether to start Guard/Sentinel now and capture a fresh green run after the documented 2026-06-15 policy/posture outage.
