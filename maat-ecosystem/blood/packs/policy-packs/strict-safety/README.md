# Strict Safety Policy Pack

## What This Does

Locks down any MAAT agent to maximum safety:

- ❌ No network access (web search, HTTP, fetch)
- ❌ No external communication (email, SMS, webhooks)
- ⚠️ All execution requires human approval
- ⚠️ All file writes require human approval
- ⚠️ All learning requires human approval
- ✅ Reading is always allowed
- 📝 All memory operations are fully logged

## Install

Add to your `config.yaml`:

```yaml
policies:
  - path: maat-packs/policy-packs/strict-safety/policy.json
```

Or via CLI:

```bash
maat packs install strict-safety
```

## Uninstall

Remove from `config.yaml` policies list. Agent reverts to inherited default policies.

## When To Use

- Testing new agents before granting trust
- Running agents on sensitive data
- Compliance environments
- Anywhere you want maximum human oversight

## Inherits

This pack inherits from `maat-default-v1`. All default Three-Ring rules apply underneath.
Strict rules override where they match.
