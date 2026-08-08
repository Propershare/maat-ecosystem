# GUARD.md - Tehuti Guard Adoption Template

This build is protected by Tehuti Guard.

Agents: before any dangerous action, assume governance applies. Do not bypass local Guard checks, central Guard calls, or audit logging.

## What Is Gated

- Shell / command execution
- File writes and edits
- Package installs or dependency source changes
- Memory, RAG, lesson, or task-state writes
- Policy, auth, CI, deploy, network, or config mutations

## Two Layers

### 1. Local Guard - Always On

Local checks run inside this repo without network access. They must be fast and deterministic.

Local Guard blocks or warns on:

- sacred paths,
- high-risk commands,
- unapproved package installs,
- protected memory/policy/config mutations.

Local deterministic denies win even if the central Guard service is down.

### 2. Central Guard - Called When Available

High-impact or ambiguous actions should call:

```text
POST http://127.0.0.1:8013/decision
```

Use the envelope in `docs/TEHUTI-GUARD-WIRE-CONTRACT.md`.

The central service adds:

- machine posture from Sentinel,
- shared policy decisions,
- correlation ids,
- governance events,
- audit trail for later review.

## Decision Values

| Decision | Meaning |
|----------|---------|
| `allow` | Proceed and log. |
| `review` | Hold high-impact work; low-risk work may proceed only in `warn` mode and must log. |
| `quarantine` | Do not execute; preserve evidence. |
| `escalate` | Do not execute; alert operator. |
| `deny` | Do not execute. Never downgrade. |

## Default Mode For New Builds

Start new builds in:

```json
{
  "mode": "warn",
  "failClosed": false
}
```

Move to `enforce` only after the central service is managed, healthy, and covered by CI.

## Sacred Paths

Do not write to these unless the build has an explicit local exception and the action is logged:

- `**/.env`
- `**/.env.*`
- `**/.git/**`
- `**/auth.json`
- `**/SOUL.md`
- `**/MEMORY.md`
- `**/memory/**`
- policy / Guard / governance files

## Required Logs

Every gated action should produce an append-only audit event with:

- timestamp,
- agent id,
- action kind,
- resource,
- local decision,
- central decision if called,
- correlation id,
- reason.

## Agent Rule

If you are unsure whether an action is gated, treat it as gated. Propose first, then execute only after the local rules and central decision allow it.
