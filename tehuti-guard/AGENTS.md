# AGENTS.md — Tehuti Guard (build, test, run)

This folder is **two products in one directory**. Know which one you are touching before you build.

| Part | Path | Package | What it is |
|------|------|---------|------------|
| **Decision API** | `guard/` | `tehuti-guard-api` (PyPI-style) | Python HTTP policy service — `POST /decision`, `POST /explain`, `GET /health|/policy-version|/rules` on **:8013**. Consumes maat-sentinel `unified_view`. **This is the `organs.policy` service** in Ka discovery. |
| **Lab helpers** | `src/` | `@tehuti-lab/guard-ldap-helpers` (private) | TypeScript three-ring / LDAP policy helpers (`enforceLDAPPolicy`, `isResourceAccessible`). **Not** the npm MCP proxy (that is `Propershare/tehuti-guard`). |

See [`README.md`](README.md) and [`../docs/TEHUTI-GUARD-PRODUCTS.md`](../docs/TEHUTI-GUARD-PRODUCTS.md) for the npm-vs-lab distinction.

## One command (preferred)

```bash
tehuti-guard/scripts/build-and-test.sh        # builds + tests BOTH halves, fails fast
tehuti-guard/scripts/build-and-test.sh --py   # Python decision API only
tehuti-guard/scripts/build-and-test.sh --ts   # TypeScript helpers only
```

CI runs exactly this (see [`.github/workflows/tehuti-guard-ci.yml`](../.github/workflows/tehuti-guard-ci.yml) at the lab root), so a green local run means a green PR.

## Manual build/test

### Python decision API (`guard/`)

```bash
cd tehuti-guard/guard
python3 -m pip install -e .
PYTHONPATH="$PWD" python3 -m unittest discover -s tests -v   # rule tests, no network
```

Rule tests do **not** require Sentinel. Requires Python >= 3.10 (stdlib only — no third-party runtime deps).

### TypeScript helpers (`src/`)

```bash
cd tehuti-guard
pnpm install        # Node >= 20, pnpm 9
pnpm build          # tsc -> dist/
pnpm test           # vitest run
```

`ldapjs` is an **optional** peer (only needed for live `queryLDAPUserGroups`). The build does not require it; the dynamic import degrades gracefully when it is absent.

## Run the service (local)

```bash
cd tehuti-guard/guard && pip install -e .
tehuti-guard-serve --host 127.0.0.1 --port 8013
# verify:
curl -s http://127.0.0.1:8013/health
```

With maat-sentinel down, `POST /decision` returns `review` (`sentinel_unreachable_review`) by design — that is correct fail-safe posture, not a bug. Start Sentinel on `:4242` for live `allow` decisions:

```bash
TEHUTI_GUARD_SENTINEL_URL=http://127.0.0.1:4242 tehuti-guard-serve --port 8013
```

End-to-end adapter proof (lab root, Guard on 8013):

```bash
python3 scripts/guard_adapter_e2e_demo.py
```

## Rules of the road for agents

- **Never weaken a `decision`.** If Guard returns `deny`/`escalate`, adapters must not downgrade it. See [`../docs/TEHUTI-SENTINEL-GUARD-ADAPTER-CONTRACT.md`](../docs/TEHUTI-SENTINEL-GUARD-ADAPTER-CONTRACT.md).
- **Keep the two packages separate.** Do not publish the lab root `package.json` as `tehuti-guard` on npm.
- **Keep `GET /rules` aligned with `evaluate()`** in `guard/tehuti_guard/rules.py` — the rule catalog is contract surface.
- **Run `build-and-test.sh` before committing** anything under this folder.
