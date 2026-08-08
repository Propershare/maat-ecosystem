# Cursor + OpenClaw — back-to-back Tehuti Guard test

**Goal:** Same **lab root** (`/home/suspect/.n8n`), two surfaces verifying the same policy code: Cursor edits and runs tests locally; OpenClaw re-runs the same command and records the outcome in `memory/`.

**Prereq:** `openclaw.json` → `agents.defaults.workspace` = `/home/suspect/.n8n`. Restart the OpenClaw gateway after changing it.

---

## Roles

| Surface | Role |
|---------|------|
| **Cursor** | Open `tehuti-guard/src/`, change `three-ring.ts` / `ldap-policy.ts`, run `pnpm test` in `tehuti-guard/`, fix types. |
| **OpenClaw** | From a **main** session (not a public group), run the same verification command via bash tool; append a one-line result to `memory/YYYY-MM-DD.md`. |

**Integration contract (human-level):** [`TEHUTI-GUARD-INTEGRATION-MATRIX.md`](TEHUTI-GUARD-INTEGRATION-MATRIX.md) — Guard answers allow/deny **before** mutating paths or executing tools.

---

## One round (back-to-back)

**1. Cursor**

```bash
cd /home/suspect/.n8n/tehuti-guard && pnpm install && pnpm test
```

**2. OpenClaw** (same host)

```bash
cd /home/suspect/.n8n/tehuti-guard && pnpm test
```

**3. Archivist line** (either surface, in `memory/YYYY-MM-DD.md`)

```text
[tehuti-guard] pnpm test PASS — commit <hash> — Cursor+OpenClaw pair check
```

---

## If tests fail

- Read Vitest output; fix `src/*.ts` or `src/guard.test.ts`.
- Re-run **both** surfaces so they stay in lockstep.

---

## Legacy `~/.openclaw/workspace`

After moving workspace to `.n8n`, old paths (e.g. nested clones) are **not** in the default OpenClaw file sandbox. Relocate into the repo or reference by absolute path in tool config.

---

*Linked from root `AGENTS.md` — keep this playbook updated when the test command changes.*
