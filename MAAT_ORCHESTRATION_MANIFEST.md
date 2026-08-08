# MAAT Orchestration Manifest

## Purpose

This document defines the intended orchestration layer for the MAAT stack. It is a bounded implementation charter for agentic execution, not a replacement for MAAT contracts, MAAT Sentinel, or any constitutional policy layer.

## Core Position

- **LangGraph** is the orchestration engine.
- **MAAT contracts** are the source of truth.
- **Tehuti Sentinel / Guard** remain the constitutional authority.
- **Adapters** perform external integration and execution.

## Non-Negotiable Boundaries

1. Orchestration must not redefine canonical schemas.
2. Orchestration must not invent new memory, task, event, or policy contracts.
3. Orchestration must not bypass Guard, Sentinel, or provenance requirements.
4. Orchestration must remain reversible, inspectable, and interruptible.
5. Orchestration must preserve identity and traceability across all actions.

## Architecture Split

### LangGraph
Responsibilities:
- durable workflow execution
- branching and retries
- checkpoints and resume
- human-in-the-loop interruption
- multi-step agent coordination

LangGraph does **not** own truth. It executes process.

### MAAT Sentinel / Contracts
Responsibilities:
- canonical policy decisions
- contract validation
- authority boundaries
- provenance requirements
- structured truth for memory, task, and event records

These define what is allowed and what is real.

### Adapters
Responsibilities:
- database writes
- external API calls
- tool execution
- transport and integration layers

Adapters translate between the orchestration layer and the world outside MAAT.

## Canonical Flow

Request -> LangGraph flow -> MAAT contract check -> Guard / Sentinel decision -> Adapter execution -> structured log / memory / event write

## Required Identity Fields

Every meaningful action should carry, where applicable:
- `agent_id`
- `device_id`
- `session_id`
- `task_id`
- `correlation_id`
- `timestamp`
- `origin_service`

## Required Event Discipline

Events must be canonical, structured, and traceable.

Examples of acceptable lifecycle names:
- `task.started`
- `task.delegated`
- `task.completed`
- `task.failed`
- `memory.read`
- `memory.written`
- `policy.allowed`
- `policy.denied`
- `session.heartbeat`

No event name drift. No local aliases without explicit mapping.

## Required Memory Discipline

- Memory writes must be structured.
- Provenance must be preserved.
- Ad hoc prose dumps are not acceptable as canonical memory.
- Summaries are allowed only when stored in a structured field with origin and context.

## Required Guard Discipline

- Any sensitive action must pass through Guard or an equivalent policy boundary.
- Denials must be recorded canonically.
- Silent bypass is not allowed.

## Rebuild Strategy

Start with a single graph:

1. request intake
2. classify risk
3. decide local rule vs Guard escalation
4. interrupt for review if needed
5. execute tool or adapter action
6. write structured event and memory records

Only after this works should we expand into multi-agent or hierarchical graphs.

## Success Criteria

The orchestration layer is successful if it is:
- traceable
- governed
- interruptible
- replayable
- contract-compliant
- provenance-safe
- easy to audit

## Final Rule

LangGraph may orchestrate execution.
It may not become the constitution.
