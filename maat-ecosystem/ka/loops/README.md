# Ka Loops — Embedded Evolution

The Ka organ runs continuous loops that keep the body alive and evolving.

## Active Loops

### Evolution Loop (`../evolve.yaml`)
```
SENSE → STORE → PATTERN → PROMOTE → APPLY → MEASURE → DECAY
```
The body gets smarter over time. Raw experience becomes patterns, patterns become learnings, learnings inform decisions. Unused learnings decay. Successful ones strengthen.

### Pulse Loop (`../pulse.yaml`)
```
CHECK → DETECT → HEAL → ESCALATE → LOG
```
The immune system. Checks every organ on a heartbeat. Heals silently when it can. Escalates what it can't fix. Logs pain for pattern detection.

## Adding a Loop

1. Create a YAML config in `ka/` (e.g., `ka/consolidate.yaml`)
2. Define stages, intervals, and thresholds
3. The Ka daemon picks it up on next restart

Loops are declarative. The Ka daemon reads the config and runs the stages. No code needed for simple loops — just YAML.

## Loop Principles

- **Loops are gentle** — they improve, they don't overwrite
- **Loops are reversible** — every promotion can be rolled back
- **Loops are observable** — every stage logs what it did
- **Loops decay gracefully** — unused learnings fade, they don't delete
