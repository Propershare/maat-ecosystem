# MAAT Policy — Full Reference

## Three-Ring Default Rules

| Ring | Allowed Actions |
|------|----------------|
| `inner-ring` | read, memory.read |
| `middle-ring` | read, propose, memory.read, memory.write |
| `outer-ring` | everything |

Unknown agents → `inner-ring` (fail-closed).

## Custom Policy Document

```json
{
  "id": "tehuti-lab-policy-v1",
  "name": "Tehuti Lab Policy",
  "version": "1",
  "rules": [
    {
      "id": "deny-rm-rf",
      "description": "Never allow recursive force delete",
      "when": { "action": "execute", "resource_pattern": "rm -rf*" },
      "then": "deny",
      "reason": "Potentially destructive"
    },
    {
      "id": "escalate-exfil",
      "description": "Escalate any potential secret exfiltration",
      "when": { "action": "execute", "resource_pattern": "curl*$SECRET*" },
      "then": "escalate",
      "reason": "Potential secret exfiltration"
    },
    {
      "id": "allow-owner-all",
      "description": "Owner has full access",
      "when": { "agent_id": "tehuti", "ring": "outer-ring" },
      "then": "allow",
      "reason": "Owner policy"
    }
  ]
}
```

## Load Policy

```python
from maat_core.kernel.policy import PolicyEngine
import json

policy = PolicyEngine()
with open("my-policy.json") as f:
    policy.load_policy(json.load(f))

result = policy.evaluate("tehuti", "execute", "rm -rf /tmp")
```

## Human Loop Modes

| Mode | Meaning |
|------|---------|
| `in-the-loop` | Human approves every sensitive action |
| `on-the-loop` | Human can audit/intervene, agent acts |
| `out-of-loop` | Agent acts autonomously within policy bounds |
