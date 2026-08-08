# Tehuti Guard Adoption Guide

**Purpose:** Give agents and maintainers one repeatable way to add Tehuti Guard protection to any Tehuti Lab build.

This guide uses a hybrid model:

- **Local Guard in every build:** small SDK/config/template that runs offline.
- **Central Guard service:** optional `POST /decision` call for posture-aware decisions and audit.

Do not copy the full `tehuti-guard/` implementation into every repo. Use templates and shared clients.

## Required Files In Each Build

Each build should include:

```text
GUARD.md
maat.guard.json
```

Start from:

```text
docs/templates/GUARD.md
docs/templates/maat.guard.json
```

## Required Behavior

Every build should enforce or log these action classes:

| Action Class | Local Check | Central Guard Call |
|--------------|-------------|--------------------|
| `read` | Usually allow | No |
| `write` / `edit` | Sacred-path block | When medium/high/protected |
| `execute` | High-risk command block | Yes |
| `install` | Optional allowlist | Yes |
| `memory_write` | Protected store check | Yes |
| `policy_change` | Protected store check | Yes |
| `deploy` | High-risk operation | Yes |
| `delete` | Destructive operation | Yes |
| `propose` | Schema/log only | No |

Local deterministic blocks must win before a central call.

## Default Mode

New builds should start with:

```json
{
  "mode": "warn",
  "failClosed": false
}
```

Use `enforce` and `failClosed: true` only after the central service is managed, monitored, and covered by integration tests.

## Wire Contract

All central calls must use:

```text
docs/TEHUTI-GUARD-WIRE-CONTRACT.md
```

Do not invent a new request shape per repo. SDKs may expose simple local APIs, but they must translate to the canonical nested envelope before calling `/decision`.

## Recommended Integration Steps

1. Copy `docs/templates/GUARD.md` to the target repo root.
2. Copy `docs/templates/maat.guard.json` to the target repo root.
3. Add or import a small Guard client for the runtime language.
4. Apply local checks before tool execution, file writes, installs, and memory writes.
5. Call central Guard for high-impact or ambiguous actions.
6. Append local audit events regardless of central service availability.
7. Add CI that validates config shape and runs local Guard tests.
8. Dogfood in `warn` mode before enabling hard enforcement.

## Monetizable Product Boundary

The open/free layer should be:

- templates,
- SDKs,
- local denylist/allowlist logic,
- wire contract.

The paid/monthly layer should be:

- hosted Guard API,
- audit retention,
- dashboards,
- compliance exports,
- maintained policy packs,
- fleet/multi-machine correlation,
- alerts and review queues.

This keeps adoption easy while leaving a durable subscription surface.

## Current Lab Follow-ups

The lab should next:

1. Fix existing client drift in `maat-runtime` by translating flat local requests into the canonical nested envelope.
2. Add a Python Guard client for scripts and adapters.
3. Add config validation for `maat.guard.json`.
4. Decide whether `openclaw` should read `maat.guard.json` directly or share a package.
5. Run `tehuti-guard-serve` and Sentinel as managed services before switching central calls from `warn` to `enforce`.

## Related

- `docs/MAAT-AUDIT-DO-WE-NEED-GUARD-IN-BUILDS-2026-06-13.md`
- `docs/TEHUTI-GUARD-WIRE-CONTRACT.md`
- `docs/TEHUTI-SENTINEL-GUARD-ADAPTER-CONTRACT.md`
- `tehuti-guard/AGENTS.md`
