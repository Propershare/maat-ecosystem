# MAAT Studio

Observability and governance layer for the MAAT ecosystem.

## Components

### Dashboard (`dashboard/`)
Web-based view of agent status, memory, events, and policies.
Reads from the event log and identity store. No writes.

### Logs (`logs/`)
Structured log viewer for event streams.
Filters by agent, event type, severity, time range.

### Replay (`replay/`)
Replay past agent sessions from event log.
See exactly what happened, what decisions were made, what policies were evaluated.
Critical for auditing and learning.

### Governance (`governance/`)
Policy editor and audit trail.
View which policies are active, who changed them, and when.
Constitutional-level visibility.

## Status

Scaffolded. Dashboard implementation next.
