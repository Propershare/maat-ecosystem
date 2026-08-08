# HEARTBEAT.md - Claude Agent

**Agent:** Claude AI (Multi-modal, FiveM specialist)
**Purpose:** Proactive monitoring and maintenance for StayDangerous infrastructure

## Heartbeat Prompt
```
Read HEARTBEAT.md and execute checks for today.
Update heartbeat-state.json with timestamps.
Log findings to memory/YYYY-MM-DD.md.
If critical issues: alert human immediately.
Otherwise: HEARTBEAT_OK with brief status.
```

## Every 30 Minutes (Lightweight)
### Status Checks
- [ ] **Raku Bot:** `systemctl --user is-active raku-bot.service`
- [ ] **FiveM Server:** `curl -s http://192.168.4.21:30120/info.json | head -1`
- [ ] **Ollama/Tehuti:** `curl -s http://localhost:11434/api/tags | grep tehuti-scholar`
- [ ] **txAdmin:** `curl -s -o /dev/null -w "%{http_code}" http://192.168.4.21:40120`
- [ ] **Disk Space:** `df -h /mnt/ai_backup/staydangerous1 | tail -1`

### Expected Results
- Raku: `active` ✅
- FiveM: Valid JSON + 200 status ✅
- Tehuti: `tehuti-scholar:v10` loaded ✅
- txAdmin: HTTP 200 ✅
- Disk: < 90% used ✅

### If Any FAIL
1. Log to memory/YYYY-MM-DD.md with ERROR tag
2. Attempt basic recovery (restart service, check logs)
3. If recovery fails → ALERT human via preferred channel

## Every 6 Hours (Deep Dive)
### Memory Curation
1. Read last 3 memory files (`memory/YYYY-MM-DD.md`)
2. Extract significant events, decisions, lessons
3. Update **MEMORY.md** (long-term) with distilled learnings
4. Remove outdated info from MEMORY.md

### Activity Review
- Check `raku.log` for errors in last 6h
- Review gitMaat for recent high-activity events
- Verify backup integrity (if scheduled)

## On Event (Triggered)
### File Changes
When modifying server files:
- Create backup before edit
- Log change to MEMORY.md with:
  - Timestamp, file changed, reason
  - Revert instructions
  - Related context

### Critical Operations
Before executing high-risk commands:
- Check with human if uncertain
- Document intention in memory
- Verify Tehuti Guard if present

## Handoff State (When Yielding)
Update in heartbeat-state.json:
```json
{
  "agent": "claude",
  "last_heartbeat": "ISO timestamp",
  "current_task": "brief description",
  "status": "active|paused|waiting_human",
  "findings": ["list of issues found"]
}
```

## Archivist Format
When logging to gitMaat, use JSON:
```json
{
  "timestamp": "2026-06-05T16:30:00Z",
  "agent": "claude",
  "event_type": "status_check|file_edit|incident",
  "details": {
    "raku_status": "active",
    "fivem_status": "online",
    "tehuti_loaded": true,
    "alerts": []
  },
  "next_action": "none|alert_human|auto_remediation"
}
```

## Response Rules
- **All Green:** Reply `HEARTBEAT_OK` + 2-sentence summary
- **Minor Issues:** Log to memory, attempt fix, report in next heartbeat
- **Critical Alerts:** Immediate notification + recommended action

## Last Updated
2026-06-05 - Initial heartbeat protocol for Claude agent
