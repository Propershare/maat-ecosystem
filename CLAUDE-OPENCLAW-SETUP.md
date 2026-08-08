# Claude - OpenClaw Agent Integration Guide

## Overview
Integrate Claude AI as a registered agent in the OpenClaw gateway ecosystem for StayDangerous lab.

## Status
- ✅ SOUL.md created
- ✅ USER.md created  
- ✅ HEARTBEAT.md created
- ✅ Daily memory filed
- ⏳ Gateway registration (manual step required)

## Step-by-Step Integration

### 1. Edit OpenClaw Config

**File:** `~/.openclaw/openclaw.json`

Add Claude agent under `agents` section:

```json
{
  "agents": {
    "claude-cursor": {
      "name": "Claude",
      "type": "ide-integrated",
      "workspace": "/home/suspect/.n8n",
      "capabilities": [
        "file-edit",
        "terminal",
        "discord-bot",
        "ollama-query"
      ],
      "context": {
        "soul": "SOUL.md",
        "user": "USER.md",
        "heartbeat": "HEARTBEAT.md"
      },
      "memory": {
        "daily": "memory/YYYY-MM-DD.md",
        "longterm": "MEMORY.md",
        "gitmaat": {
          "enabled": true,
          "schema": "maat_memory"
        }
      },
      "integrations": {
        "raku": {
          "service": "raku-bot.service",
          "log": "/home/suspect/.n8n/staydangerous-fivem-skill/raku.log"
        },
        "ollama": {
          "url": "http://localhost:11434",
          "model": "tehuti-scholar:v10"
        },
        "tehuti-guard": {
          "url": "http://localhost:8013",
          "endpoint": "/decision"
        }
      },
      "heartbeat": {
        "enabled": true,
        "interval": "30m",
        "checks": [
          "raku-status",
          "fivem-status", 
          "ollama-health",
          "disk-space"
        ]
      }
    }
  }
}
```

### 2. Restart Gateway

```bash
systemctl --user restart openclaw
curl -s http://localhost:18790/agents | jq '.claude-cursor'
# Should return agent config
```

### 3. Verify Heartbeat State Directory

```bash
mkdir -p /home/suspect/.n8n/.heartbeat
chmod 750 /home/suspect/.n8n/.heartbeat
```

### 4. Test Integration

**From OpenClaw CLI:**
```bash
# Check agent status
openclaw agents:status claude-cursor

# Trigger heartbeat
openclaw agents:heartbeat claude-cursor

# Dispatch task
openclaw agents:dispatch claude-cursor \
  --task "check fivem server status" \
  --output json
```

**Direct HTTP:**
```bash
curl -X POST http://localhost:18790/agents/claude-cursor/heartbeat \
  -H "Content-Type: application/json" \
  -d '{"checks": ["raku", "fivem"]}'
```

## Agent Capabilities

| Capability | Description | Risk Level |
|------------|-------------|------------|
| `file-edit` | Edit files in workspace | High |
| `terminal` | Execute shell commands | High |
| `discord-bot` | Operate Raku bot | Medium |
| `ollama-query` | Query local LLM | Low |

**Policy Enforcement:**
- High-risk: Require human approval or Tehuti Guard
- Medium-risk: Log to gitMaat, proceed
- Low-risk: Auto-execute

## Archivist Format (gitMaat)

When logging actions:

```json
{
  "timestamp": "2026-06-05T16:30:00Z",
  "agent_id": "claude-cursor",
  "session_id": "uuid-from-session-index",
  "event_type": "file_edit|status_check|incident",
  "human_request": true,
  "operation": {
    "type": "edit",
    "file": "config.lua",
    "backup_created": true,
    "preserved_original": true
  },
  "context": {
    "before": "original code hash",
    "after": "new code hash", 
    "reason": "fix nil Config error"
  },
  "outcome": {
    "success": true,
    "validation": "passed"
  }
}
```

## Session Index Participation

When joining multi-agent work:

1. **Register:** POST `/session-index/register`
2. **Heartbeat:** PUT `/session-index/heartbeat/{session_id}`
3. **Update:** PATCH `/session-index/status/{session_id}`
4. **Close:** POST `/session-index/close/{session_id}`

See `docs/SESSION-INDEX-SERVICE.md` for full spec.

## Troubleshooting

### Gateway Can't Find Agent
```bash
# Check config syntax
jsonlint ~/.openclaw/openclaw.json

# Verify file permissions
ls -la ~/.openclaw/

# Restart gateway
systemctl --user restart openclaw
```

### Heartbeat Fails
```bash
# Check state directory
ls -la /home/suspect/.n8n/.heartbeat/

# Review logs
journalctl --user -u openclaw -f
```

### Tehuti Guard Rejects Actions
- Verify guard is running: `curl http://localhost:8013/health`
- Check policy: `cat ~/tehuti-guard/guard/policy.yaml`
- Ensure agent ID matches registered name

## Next Steps

1. [ ] Edit ~/.openclaw/openclaw.json
2. [ ] Restart gateway
3. [ ] Test heartbeat from OpenClaw CLI
4. [ ] Verify gitMaat write access
5. [ ] Join swarm session and log to Session Index

## Contact

OpenClaw gateway: http://localhost:18790
Maat ecosystem docs: docs/ runtime spine

---
**Status:** Ready for gateway registration
**Created:** 2026-06-05
**Agent:** Claude
