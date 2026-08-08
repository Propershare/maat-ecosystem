---
name: gitmaat-bootstrap
description: "Inject GITMAAT-CONTEXT.md into agent bootstrap so every turn sees current tasks and recent activity (Maat: query first)."
metadata:
  {
    "openclaw": {
      "emoji": "🪶",
      "events": ["agent:bootstrap"],
      "install": [{ "id": "workspace", "kind": "bundled", "label": "Tehuti Lab workspace" }]
    }
  }
---

# gitmaat-bootstrap

Injects **GITMAAT-CONTEXT.md** into the agent bootstrap file list before each run. Tehuti (and any agent using this workspace) then sees current gitMaat tasks and recent changes without calling a tool — Maat "query first" is in context by default.

## What it does

- On every agent run, before the system prompt is built, the hook runs.
- If `GITMAAT-CONTEXT.md` exists in the workspace root, it is prepended to the bootstrap files.
- The agent receives it as part of their context (with SOUL, USER, AGENTS, etc.).

## Requirements

- `hooks.internal.enabled: true` in OpenClaw config (`~/.openclaw/openclaw.json`).
- Workspace root must contain or generate `GITMAAT-CONTEXT.md` (e.g. via `python maatlangchain/scripts/query_gitmaat.py --out GITMAAT-CONTEXT.md`).

## Enable

In `~/.openclaw/openclaw.json`:

```json
{
  "hooks": {
    "internal": {
      "enabled": true
    }
  }
}
```

Restart the gateway after enabling. No per-hook config required; the hook is enabled when internal hooks are on and the file exists.
