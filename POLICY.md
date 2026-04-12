# MAAT Policy Doctrine

## What Policy Is

Policy is the **machine-readable moral and operational constitution**.

Not guardrails. Not vibes. Not prompt instructions.

Policy is structured, evaluable, auditable rules that determine what agents can and cannot do.

## The 5 Outcomes

Every policy evaluation produces exactly one of:

| Outcome | Meaning |
|---------|---------|
| `allow` | Action permitted. Proceed. |
| `deny` | Action forbidden. Stop. Log violation. |
| `escalate` | Action requires human or higher-ring approval before proceeding. |
| `require_approval` | Like escalate, but blocks until explicit approval received. |
| `log` | Action permitted, but logged for audit. Continue evaluating. |

## Evaluation Order

1. Rules are evaluated in document order within each policy
2. First matching rule wins (except `log`, which continues evaluation)
3. Multiple policies stack — evaluated in load order
4. If no rule matches: **fail-closed** (deny by default)
5. `log` rules never terminate evaluation — they annotate

## Three-Ring Governance

| Ring | Authority | Default Actions |
|------|-----------|----------------|
| `inner-ring` | Observe only | read, memory.read |
| `middle-ring` | Participate | read, propose, memory.read, memory.write |
| `outer-ring` | Full authority | everything |

Unknown agents → `inner-ring`. Always fail-closed.

## Policy Inheritance

Policies can inherit from other policies:

```json
{
  "id": "strict-safety-v1",
  "inherits": ["maat-default-v1"],
  "rules": [...]
}
```

Child rules are evaluated first. If no match, parent rules apply.

## What Makes Good Policy

1. **Explicit over implicit.** If a rule matters, write it down.
2. **Reason is required.** Every rule must explain why.
3. **Test with edge cases.** What if agent_id is unknown? What if action is new?
4. **Fail-closed.** Unknown = deny. Always.
5. **Escalation paths must exist.** Deny without escalation is a dead end.
6. **Review periodically.** Policies ossify. Schedule reviews.

## Policy vs Prompts

| | Policy | Prompts |
|--|--------|---------|
| Format | Structured JSON | Natural language |
| Evaluable | Machine-evaluable | Model-interpreted |
| Auditable | Deterministic | Non-deterministic |
| Versioned | Yes, by design | Usually not |
| Survives model swap | Yes | Maybe |

**Prompts are sand. Policies are stone.**

Use prompts for guidance and personality.
Use policies for rules and boundaries.
