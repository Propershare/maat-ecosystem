# MAAT Learning Doctrine

## Principle

**Learning must be reversible.**

If learning is not reversible, your system will become a self-corrupting mess.

## What Learning Is

Learning is controlled adaptation:

| Type | What Changes | Reversible |
|------|-------------|-----------|
| `memory_consolidation` | Episodic → semantic promotion | Yes |
| `prompt_refinement` | System prompts improved from experience | Yes |
| `tool_usage_refinement` | Better tool selection/parameter patterns | Yes |
| `fine_tune_metadata` | Data tagged for potential fine-tuning | Yes (metadata only) |
| `policy_update` | Policy rules added/modified | Yes |
| `rollback` | Undo any of the above | N/A |

## The Learning Loop

```
observe → propose → approve → apply → verify → (rollback if needed)
```

1. **Observe**: Agent notices pattern (repeated actions, common queries, errors)
2. **Propose**: Agent creates a learning record with before_snapshot
3. **Approve**: Human or outer-ring agent approves (based on loop_mode)
4. **Apply**: Change is made to memory/prompts/tools/policy
5. **Verify**: System checks that the change improved things
6. **Rollback**: If verification fails, restore before_snapshot

## Snapshots Are Mandatory

Every learning record must include:

```json
{
  "before_snapshot": { "what it was" },
  "after_snapshot": { "what it became" },
  "reversible": true,
  "rolled_back": false
}
```

No snapshot = no learning. Period.

## Learning + Human Loop Modes

| Mode | Learning Behavior |
|------|------------------|
| `in-the-loop` | Human approves every learning proposal |
| `on-the-loop` | Agent applies, human can review and rollback |
| `out-of-loop` | Agent applies autonomously within policy bounds |

**Default: `on-the-loop`.** Agent learns, human audits.

## What Learning Is NOT

- Not uncontrolled self-modification
- Not silent prompt drift
- Not accumulating bad patterns without review
- Not fine-tuning without consent
- Not changing constitutional memory (that's amendment, not learning)

## Consolidation Schedule

| Frequency | What Happens |
|-----------|-------------|
| Daily | Episodic → semantic candidates identified |
| Weekly | Prompt and tool usage patterns reviewed |
| Monthly | Full learning audit (what improved, what regressed) |

## The Safety Valve

If at any point the system's behavior degrades after learning:

1. Identify the learning record that caused it
2. Rollback using `before_snapshot`
3. Emit `learning.rolled_back` event
4. Flag the learning type for review

**Rolling back is not failure. Rolling back is the system working correctly.**
