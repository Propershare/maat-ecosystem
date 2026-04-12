# MAAT Event Taxonomy

## Principle

Events are first-class citizens. Not logs. Not print statements.

Every significant action in the ecosystem emits a structured event.
Events are the **nervous system** of the ecology.

If it happened and no event was emitted, it didn't happen (to the system).

## Event Structure (maat:event:v1)

```json
{
  "id": "uuid",
  "type": "domain.action",
  "agent_id": "who did it",
  "timestamp": "ISO 8601",
  "session_id": "which session",
  "severity": "debug|info|warning|error|critical",
  "payload": {}
}
```

## Canonical Event Types

### Agent Lifecycle
| Event | When | Severity |
|-------|------|----------|
| `agent.registered` | New identity created | info |
| `agent.started` | Agent session begins | info |
| `agent.stopped` | Agent session ends | info |
| `agent.identity_updated` | Identity amended | warning |

### Memory
| Event | When | Severity |
|-------|------|----------|
| `memory.written` | Any memory write | info |
| `memory.retrieved` | Memory search/recall | debug |
| `memory.deleted` | Memory rollback | warning |
| `memory.consolidated` | Episodic → semantic | info |
| `memory.constitutional_amended` | Constitutional memory amended | critical |

### Task
| Event | When | Severity |
|-------|------|----------|
| `task.created` | New task | info |
| `task.in_progress` | Work started | info |
| `task.completed` | Successfully done | info |
| `task.failed` | Failed | error |
| `task.blocked` | Waiting on dependency | warning |
| `task.escalated` | Needs human | warning |

### Tool
| Event | When | Severity |
|-------|------|----------|
| `tool.called` | Tool successfully invoked | info |
| `tool.denied` | Policy blocked tool use | warning |
| `tool.failed` | Tool execution error | error |

### Policy
| Event | When | Severity |
|-------|------|----------|
| `policy.evaluated` | Any policy check | debug |
| `policy.violated` | Action denied by policy | warning |
| `policy.escalation_requested` | Escalation triggered | warning |
| `policy.loaded` | New policy document loaded | info |

### Learning
| Event | When | Severity |
|-------|------|----------|
| `learning.proposed` | Learning cycle proposed | info |
| `learning.approved` | Human/outer-ring approved | info |
| `learning.applied` | Learning applied to system | info |
| `learning.rolled_back` | Learning reversed | warning |
| `learning.cycle_complete` | Full learning cycle done | info |

### Adapter
| Event | When | Severity |
|-------|------|----------|
| `adapter.loaded` | Adapter initialized | info |
| `adapter.swapped` | Hot-swap occurred | warning |
| `adapter.failed` | Adapter error | error |

### Constitution
| Event | When | Severity |
|-------|------|----------|
| `constitution.amended` | Sacred contract changed | critical |
| `constitution.violation_detected` | Something broke a sacred rule | critical |

### Migration
| Event | When | Severity |
|-------|------|----------|
| `migration.started` | Export/import begun | info |
| `migration.completed` | Successfully migrated | info |
| `migration.failed` | Migration error | error |

### Human
| Event | When | Severity |
|-------|------|----------|
| `human.approval_requested` | Agent needs human sign-off | info |
| `human.approved` | Human approved action | info |
| `human.rejected` | Human rejected action | warning |
| `human.override` | Human overrode agent decision | warning |

## Rules

1. **Every domain gets a namespace.** No flat event names.
2. **Payload is domain-specific** but always a dict.
3. **Severity is meaningful.** debug=trace, info=normal, warning=attention, error=failure, critical=constitutional.
4. **Events are append-only.** Never delete events. The log is the truth.
5. **Events enable everything downstream.** Studio, replay, audit, learning, cooperation — all consume events.
6. **If you add a new event type, add it here first.** This document is the canonical taxonomy.
