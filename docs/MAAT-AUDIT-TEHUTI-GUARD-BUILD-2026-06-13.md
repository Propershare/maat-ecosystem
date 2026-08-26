# MAAT Audit — Tehuti Guard build & repo testing

**Date:** 2026-06-13
**Auditor agent:** `cursor_staydangerous` (P'TAH)
**Scope:** `tehuti-guard/` build health, agent buildability, and connection to the repo for testing.
**Correlation:** `tehuti-guard-build:20260613T143000Z`

Maat lens: **Truth** (what is actually true on disk/runtime), **Balance** (keep what works, fix only what is broken), **Order** (one canonical build path), **Justice** (correct attribution of the two products), **Self-Reflection** (logged learnings + next actions).

---

## 1. Truth — state before this PR

Evidence gathered by reading code and running it (not docs alone):

| Surface | Before | Evidence |
|---------|--------|----------|
| Python decision API code (`guard/`) | **Healthy** | `python -m unittest` → 9/9 OK; in-process server smoke `GET /health` 200, `POST /decision` → `review` (sentinel unreachable, by design). |
| TS helpers build (`src/`) | **BROKEN** | `pnpm build` → TS2307 `Cannot find module 'ldapjs'` + 7× implicit-`any` (TS7006). |
| TS helpers tests (`src/`) | **BROKEN** | `pnpm test` → `ERR_REQUIRE_ESM` loading `vitest.config.ts` (Vite 7 is ESM-only; Vitest loaded config via CJS `require`). |
| Live service `:8013` | **Not listening** | `ss -ltnp` shows 8010/8014/8022 up; 8013 and 4242 absent. No `systemd --user` units for guard/sentinel. |
| Discovery advertisement | **Advertised** | Ka `:8010/manifest` lists `organs.policy` → `http://192.168.4.21:8013`. |
| Repo CI for Guard | **Absent** | No `.github/workflows` at lab root; nothing ran Guard tests on PR. |

**Conclusion:** Guard's *logic* was sound; its *TS packaging* was red and there was *no automated proof* tied to the repo. Policy was advertised without a CI gate or a documented build path for agents.

---

## 2. Balance — what changed (minimal, preserve-first)

No rule logic, no decision semantics, no API surface was altered. Changes are packaging, docs, and CI only.

| Change | File | Why |
|--------|------|-----|
| Optional `ldapjs` via indirected dynamic import + explicit `any` on callbacks | `tehuti-guard/src/ldap-policy.ts` | Build green without forcing a heavy LDAP dependency; `ldapjs` stays an optional peer for live use. |
| Vitest config loaded as ESM | `tehuti-guard/vitest.config.ts` → `vitest.config.mts` | Fixes `ERR_REQUIRE_ESM` under Vite 7 / Vitest 3 without making the whole package `type: module` (which would break the CJS `dist/` output). |
| Canonical build+test script | `tehuti-guard/scripts/build-and-test.sh` | One deterministic command builds/tests **both** halves, fails fast. |
| Agent build guide | `tehuti-guard/AGENTS.md` | Agents now have a single source for "how to build/test/run Guard." |
| Repo CI | `.github/workflows/tehuti-guard-ci.yml` | Connects Guard to the repo: every PR touching `tehuti-guard/` runs Python (3.10–3.12) + TS (Node 20) build/test. |

---

## 3. Order — one canonical build path

```bash
tehuti-guard/scripts/build-and-test.sh        # both halves
tehuti-guard/scripts/build-and-test.sh --py   # Python decision API
tehuti-guard/scripts/build-and-test.sh --ts   # TS helpers
```

CI executes the same steps, so **green local == green PR**. Verified locally:

- Python: `Ran 9 tests ... OK`, `guard import OK 0.1.0`
- TS: `tsc` clean, `vitest run` → `8 passed (8)`
- Full script: `Tehuti Guard build + test: ALL GREEN`

---

## 4. Justice — keep the two products distinct

This audit does **not** touch the npm MCP proxy (`Propershare/tehuti-guard`). It governs only the lab tree:

- `guard/` → `tehuti-guard-api` (Python, `:8013`, `organs.policy`).
- root `package.json` → `@tehuti-lab/guard-ldap-helpers` (private TS), **not** publishable as `tehuti-guard` on npm.

See [`TEHUTI-GUARD-PRODUCTS.md`](TEHUTI-GUARD-PRODUCTS.md).

---

## 5. Self-Reflection — residual risk & next actions

Still open after this PR (tracked, not silently dropped):

1. **Runtime not wired.** Guard `:8013` and Sentinel `:4242` are not running as managed services. Discovery advertises policy without a live backend. → Add `systemd --user` units (or document `tehuti-guard-serve` + `scripts/start-sentinel-daemon.sh`) and a health check in `scripts/lab-runtime-check.sh`.
2. **Sentinel dependency.** Until Sentinel `:4242` is healthy for `machine_id`, live `POST /decision` returns `review`. This is correct fail-safe behavior; adapters must treat non-`allow` as hold for high-impact actions (see adapter contract).
3. **No HTTP-level integration test in CI.** CI covers unit + build. A future job could boot `tehuti-guard-serve` and run `scripts/guard_adapter_e2e_demo.py` against it.
4. **`pnpm install --frozen-lockfile`** was not verifiable in the sandbox (no registry egress); CI on the runner has network and is the real check.

---

## Verdict

**PASS with follow-ups.** Tehuti Guard is now **buildable by any agent via one command**, **green on both halves**, and **connected to the repo for testing via CI**. Remaining work is operational (run the service + Sentinel), tracked above.
