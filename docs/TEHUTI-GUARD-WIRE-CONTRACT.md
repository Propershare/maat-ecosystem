# Tehuti Guard Wire Contract

**Status:** Canonical v1 contract for lab builds  
**Purpose:** Every build that calls Tehuti Guard must use the same request envelope, response interpretation, and failure posture.

This contract is the boundary between local adapters/SDKs and the central Tehuti Guard decision API.

## Endpoint

```text
POST /decision
Content-Type: application/json
```

Default lab URL:

```text
http://127.0.0.1:8013/decision
```

## Request Envelope

All clients must send this nested envelope:

```json
{
  "machine_id": "staydangerous",
  "actor": {
    "id": "maat-runtime@staydangerous",
    "role": "agent"
  },
  "action": {
    "kind": "execute",
    "resource": "bash:pnpm build",
    "risk": "medium"
  },
  "correlation_id": "guard:2026-06-13T15:00:00Z:example",
  "forge_meta": {
    "session_id": "optional-session",
    "task_id": "optional-task"
  }
}
```

### Required Fields

| Field | Type | Meaning |
|-------|------|---------|
| `machine_id` | string | Machine or runtime posture key used by Sentinel. |
| `actor.id` | string | Agent, service, or human id. |
| `actor.role` | string | `agent`, `operator`, `service`, or a build-specific role. |
| `action.kind` | string | One of the canonical action kinds below. |
| `action.resource` | string | Path, command, package name, memory key, tool id, or logical resource. |
| `action.risk` | string | One of `low`, `medium`, `high`, `protected`. |

### Optional Fields

| Field | Type | Meaning |
|-------|------|---------|
| `correlation_id` | string | Join key for local logs, Guard response, gitMaat, and later audit. If omitted, Guard may generate one. |
| `forge_meta.session_id` | string | Session index / agent session id. |
| `forge_meta.task_id` | string | gitMaat or build task id. |

## Canonical Action Kinds

| Kind | Use For |
|------|---------|
| `read` | File reads, grep/search, list operations. |
| `write` | File edits, config writes, generated artifacts. |
| `execute` | Shell commands, tool execution, scripts. |
| `install` | Package manager operations or dependency source changes. |
| `memory_write` | Durable memory, gitMaat, RAG ingest, promotion of lessons. |
| `policy_change` | Guard, Maat, auth, CI, or governance mutations. |
| `deploy` | Release, restart, service exposure, production operations. |
| `delete` | Destructive filesystem or data operations. |
| `propose` | Proposal-only changes that do not mutate the target surface. |

Clients may add domain-specific kinds, but SDKs should normalize to these first.

## Risk Mapping

| Risk | Meaning |
|------|---------|
| `low` | Read-only or local deterministic safe action. |
| `medium` | Ordinary write/edit/install that is reversible and not sensitive. |
| `high` | Shell, deploy, privileged write, cross-repo action, network exposure, memory mutation. |
| `protected` | Secrets, identity, policy, sacred paths, canon, durable governance, or irreversible data. |

## Response

Guard returns structured JSON:

```json
{
  "decision": "review",
  "severity": "warning",
  "reason": "Sentinel unified view unavailable - cannot align posture",
  "tags": ["sentinel_unreachable"],
  "blocking_actions": ["Check TEHUTI_GUARD_SENTINEL_URL and that maat-sentinel serve is running"],
  "matched_rules": ["sentinel_unreachable_review"],
  "explanation_id": "sha256:...",
  "correlation_id": "guard:2026-06-13T15:00:00Z:example",
  "policy_version": "1",
  "sentinel_url": "http://127.0.0.1:4242"
}
```

## Decision Semantics

| Decision | Client Behavior |
|----------|-----------------|
| `allow` | Proceed. Log the decision. |
| `review` | Hold high-impact work. Low-risk local work may proceed only in `warn` mode and must log. |
| `quarantine` | Do not execute. Preserve evidence and request review. |
| `escalate` | Do not execute. Alert operator / higher authority. |
| `deny` | Do not execute. Never downgrade. |

Clients must never treat `reason` text as authority. The structured `decision` field is the authority.

## Failure Posture

Local deterministic denies always win, even if central Guard is unavailable.

Recommended build defaults while dogfooding:

```json
{
  "mode": "warn",
  "failClosed": false
}
```

Use `enforce` + `failClosed` only when:

- Guard `:8013` has a managed service,
- Sentinel posture is healthy where required,
- CI tests the request envelope,
- operators accept the chance that a down Guard blocks gated work.

## Anti-Drift Rule

Do not send flat requests like:

```json
{ "actor": "agent", "action": "write", "resource": "file" }
```

That shape is not the Guard v1 contract. SDKs may accept flat local inputs, but must translate them into the nested envelope before calling `/decision`.

## Related

- `tehuti-guard/guard/README.md`
- `docs/TEHUTI-SENTINEL-GUARD-ADAPTER-CONTRACT.md`
- `docs/GUARD-ADOPTION.md`
