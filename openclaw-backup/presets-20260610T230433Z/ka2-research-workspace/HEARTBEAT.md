# HEARTBEAT — KA2 Research agent

On each heartbeat poll:

1. Read this file and [`AGENTS.md`](AGENTS.md) if needed for context.
2. If gitMaat / Maat Memory is reachable, check **pending / in-progress** tasks for this agent id (`cursor_*` per `.cursorrules`).
3. If nothing needs attention, reply **`HEARTBEAT_OK`**.

Do not invent tasks from old chats; task source of truth is **gitMaat** and `lab/docs/MAAT-AUDIT-ACTION-PLAN.md` for human-facing checklists.
