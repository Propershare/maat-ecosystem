---
name: fivem
description: FiveM server context and operations. Use when the user asks about their FiveM server, resources, server.cfg, txAdmin, logs, or any files under the FiveM server root. The server root on this machine is /mnt/ai_backup.
---

# FiveM Server Skill (OpenClaw)

## Server root

The FiveM server files on this machine live under:

**`/mnt/ai_backup`**

Treat this path as the root for anything FiveM-related: resources, configs, server.cfg, txAdmin, logs, or scripts.

## When to use this skill

- User asks about the FiveM server, resources, or config.
- User wants to edit server.cfg, fxmanifest.lua, or other server files.
- User asks to list resources, check logs, or run commands in the server directory.
- User mentions txAdmin, server start/stop, or anything under the server root.

## Paths and tools

- **Server root:** `/mnt/ai_backup` (resolve subpaths from here, e.g. `/mnt/ai_backup/server.cfg`, `/mnt/ai_backup/resources/...`).
- Use the **read** tool to open files under `/mnt/ai_backup`.
- Use the **edit** or **write** tools for changes; prefer absolute paths like `/mnt/ai_backup/...`.
- Use the **exec** tool for shell commands (e.g. listing resources, checking processes) with working directory `/mnt/ai_backup` when relevant.

## Notes

- This workspace (`/home/suspect/.n8n`) is the coordination hub; the FiveM server itself is on `/mnt/ai_backup`.
- If the user says "my FiveM server" or "the server" in a FiveM context, assume they mean `/mnt/ai_backup` unless they specify another path.
