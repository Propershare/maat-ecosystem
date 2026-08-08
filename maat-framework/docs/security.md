# Security — Three-Ring Governance

## Overview

Every agent action passes through `maat.guard` before execution.
The system is **fail-closed**: if anything goes wrong, access is denied.

## The Three Rings

```
┌─────────────────────────────────────────┐
│             OUTER RING                  │
│   Actions: read, write, execute, propose│
│   Who: owner, admin agents              │
│                                         │
│   ┌─────────────────────────────────┐   │
│   │         MIDDLE RING             │   │
│   │   Actions: read, propose        │   │
│   │   Who: trusted agents           │   │
│   │                                 │   │
│   │   ┌─────────────────────────┐   │   │
│   │   │      INNER RING         │   │   │
│   │   │   Actions: read         │   │   │
│   │   │   Who: guests, public   │   │   │
│   │   └─────────────────────────┘   │   │
│   └─────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

## Usage

### Check access

```python
from maat.guard import check_access

result = check_access("my-agent", "execute", "/bin/backup.sh")
if result.allowed:
    run_it()
else:
    print(f"Denied: {result.reason}")
```

### Register agents

```python
from maat.guard import register_agent

register_agent("tehuti", "outer-ring")        # Full access
register_agent("research-bot", "middle-ring")  # Read + propose
register_agent("public-api", "inner-ring")     # Read only
```

### Scan commands

```python
from maat.guard import scan_command

result = scan_command("rm -rf / --no-preserve-root")
# result.safe = False
# result.warnings = ["Recursive force-delete on broad path"]
```

## What Gets Scanned

| Pattern | Risk | Action |
|---------|------|--------|
| `rm -rf /` | Data destruction | Block |
| `chmod 777` | Permission escalation | Block |
| `curl ... \| bash` | Remote code execution | Block |
| `dd of=/dev/sda` | Disk wipe | Block |
| `curl $SECRET_KEY` | Secret exfiltration | Block |
| Fork bomb `:(){ :\|:& }` | System crash | Block |
| Overwrite `/etc/passwd` | Auth bypass | Block |

## Default Agent Registry

| Agent | Ring | Notes |
|-------|------|-------|
| `owner` | outer-ring | Default entry. Full access. |

All other agents default to **inner-ring** (read-only) until explicitly registered.

## LDAP Integration (Optional)

For multi-user deployments, the guard can read roles from LDAP:

```yaml
# In ~/.maat/config.yaml
security:
  governance: "three-ring"
  ldap:
    host: "127.0.0.1"
    port: 389
    base: "dc=tehuti,dc=lab"
    group_mapping:
      admins: "outer-ring"
      agents: "middle-ring"
      guests: "inner-ring"
```

This is optional. Single-user setups don't need LDAP.

## Design Decisions

- **Fail-closed** — Unknown agents get minimum access, not maximum
- **Simple model** — Three levels, not a complex RBAC matrix
- **Regex scanning** — Fast, covers common threats, not exhaustive
- **Defense in depth** — Guard is one layer; Ollama sandboxing and OS-level permissions add more
