# Clawdbot AI Employee Setup - COMPLETE ✅

## Setup Summary

All components have been successfully configured and deployed!

### ✅ Completed Steps

1. **Workflow Created**: `/home/suspect/.n8n/n8n-workflows/ai-employee-workflow.json`
   - Webhook endpoint: `http://sba.suspecttv.com:5678/webhook/ai-employee`
   - Workflow ID: `VXs9N0eKb1KZPxyZ`
   - Status: **ACTIVE** ✅

2. **Logging Script Created**: `/home/suspect/.n8n/scripts/log-to-gitmaat.py`
   - Successfully logs tasks to gitMaat
   - Tested and working ✅

3. **Workflow Imported & Activated**: 
   - Imported via n8n API
   - Activated and ready to receive requests ✅

## How It Works

### Flow:
```
WhatsApp → Clawdbot → Gateway → n8n Webhook → AI Employee Workflow
                                                      ↓
                                    Parse Task → Query gitMaat → Ollama Planning
                                                      ↓
                                    Execute Task → Log to gitMaat → Format Response
                                                      ↓
                                    Response → Clawdbot → WhatsApp
```

### Components:

1. **Webhook Endpoint**: `http://sba.suspecttv.com:5678/webhook/ai-employee`
   - Receives POST requests from Clawdbot
   - Accepts JSON: `{"task": "your task", "from": "user_id"}`

2. **Ollama Integration**: Uses local model `tehuti-lab-llama3.1-8b-maat`
   - Plans task execution based on Maat principles
   - Zero API costs (local model)

3. **gitMaat Integration**: 
   - Queries gitMaat for context before execution
   - Logs all task executions
   - Tracks learnings and changes

4. **Task Execution**: 
   - System status checks
   - gitMaat queries
   - Safe command execution

## Clawdbot Configuration Needed

On your PC where Clawdbot runs, configure:

### 1. Hooks Configuration
Edit `~/.clawdbot/clawdbot.json`:

```json
{
  "hooks": {
    "mappings": {
      "ai-employee": {
        "url": "http://sba.suspecttv.com:5678/webhook/ai-employee",
        "method": "POST",
        "headers": {
          "Content-Type": "application/json"
        }
      }
    }
  }
}
```

### 2. Memory File
Create `~/clawdbot-memory/$(date +%Y-%m-%d).md`:

```markdown
# Clawdbot Memory - Maat Principles

## Maat Principles (LAW)
- Always query gitMaat first before executing tasks (MANDATORY LAW)
- Follow Maat principles: Truth, Balance, Order, Justice, Self-Reflection
- Learn from past work (Sankofa principle)
- Log all task executions to gitMaat
- Use local Ollama models to minimize costs

## Integration Points
- n8n: http://sba.suspecttv.com:5678
- Webhook: http://sba.suspecttv.com:5678/webhook/ai-employee
- Server: 192.168.4.21 (sba.suspecttv.com)
```

## Testing

### Test Webhook Directly:
```bash
curl -X POST "http://sba.suspecttv.com:5678/webhook/ai-employee" \
  -H "Content-Type: application/json" \
  -d '{"task": "Check system status", "from": "test"}'
```

### Test via WhatsApp:
Send to Clawdbot: "Check system status"

Expected flow:
1. Clawdbot receives message
2. Routes to `ai-employee` hook
3. n8n workflow processes task
4. Returns formatted response
5. Clawdbot sends back to WhatsApp

## Available Commands

### System Commands:
- "Check system status" - System health check
- "Show system info" - System information

### gitMaat Commands:
- "Query gitMaat for tasks" - Show pending tasks
- "Show recent changes" - Recent gitMaat changes
- "Show learnings" - Recent learnings

### General Commands:
- "List files" - Safe directory listing
- "Current date" - System date/time

## Cost Breakdown

- ✅ **Local Ollama Models**: $0 (runs on server)
- ✅ **Clawdbot**: $0 (self-hosted)
- ✅ **n8n**: $0 (self-hosted)
- ✅ **WhatsApp**: $0 (via Clawdbot)
- ✅ **Total Monthly Cost**: **$0**

## Next Steps

1. **Configure Clawdbot hooks** (see above)
2. **Test via WhatsApp** - Send "Check system status"
3. **Monitor workflow** - Check n8n UI for execution logs
4. **Check gitMaat** - Verify tasks are being logged

## Troubleshooting

### Webhook Not Responding:
- Check n8n workflow is active: `http://sba.suspecttv.com:5678`
- Verify webhook path: `/webhook/ai-employee`
- Check n8n execution logs

### gitMaat Logging Fails:
- Verify PostgreSQL connection
- Check `PGVECTOR_DB_URL` environment variable
- Test script: `python3 /home/suspect/.n8n/scripts/log-to-gitmaat.py "test" "result" "completed"`

### Ollama Not Responding:
- Check Ollama is running: `curl http://localhost:11434/api/tags`
- Verify model exists: `ollama list`
- Check model name matches: `tehuti-lab-llama3.1-8b-maat`

## Files Created

- `/home/suspect/.n8n/n8n-workflows/ai-employee-workflow.json` - Main workflow
- `/home/suspect/.n8n/scripts/log-to-gitmaat.py` - Logging script
- `/home/suspect/.n8n/CLAWDBOT-SETUP-COMPLETE.md` - This file

## Workflow Details

- **Name**: AI Employee - Task Handler
- **ID**: VXs9N0eKb1KZPxyZ
- **Status**: Active
- **Webhook Path**: `/webhook/ai-employee`
- **Nodes**: 8 (Webhook → Parse → Ollama → Execute → Log → Format → Respond)

---

**Setup completed on**: 2026-01-29
**Ready for use**: ✅ YES
