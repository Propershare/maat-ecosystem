# System Shepherd

Blueprint for a **lab-local orchestration layer**: observe services, route work, and keep multi-step engineering runs coherent—without requiring a live subagent session when the spawn API is unavailable.

## Layout

| Path | Role |
|------|------|
| `.channels/` | Channel adapter specs and config (one logical surface per integration; see `.channels/README.md`) |
| `.cursor/skills/system-shepherd/` | Cursor skill entrypoint (agent instructions) |

## Principles

- **Scaffold first** — filesystem and contracts before automation.
- **Explicit channels** — no silent coupling; each channel documents inputs, auth, and failure modes.
- **Iterative refinement** — this tree is the starting point; behavior grows in small commits.

## See also

- `AGENTS.md` (lab root) — workspace identity and session ritual.
