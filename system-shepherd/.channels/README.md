# Channels (`.channels/`)

Place **channel adapter definitions** here: one subdirectory or file group per logical channel (e.g. `openclaw`, `gitmaat`, `mcp`, `cron`).

## Contract (draft)

Each channel SHOULD declare:

- **id** — stable identifier (lowercase, hyphenated).
- **purpose** — what this channel is allowed to do.
- **inputs** — config paths, env vars, or secrets references (not secret values).
- **health** — how to verify the channel is usable (read-only checks).
- **failure** — what to do when the channel is down (degrade, queue, or skip).

Add concrete manifests (YAML or JSON) as the framework is implemented.
