# Clawdbot Integration with Tehuti Lab Workflow

## 🎯 What is Clawdbot?

Clawdbot is a messaging-based AI assistant that runs 24/7 on your PC, connecting via:
- **WhatsApp**
- **Telegram** 
- **Discord**

It can perform actions, maintain memory, and integrate with workflows via webhooks and Gateway.

## 🔗 Integration Points

### 1. Webhook Integration (n8n → Clawdbot)

**Set up n8n webhook to receive messages from Clawdbot:**

1. Create n8n workflow with **Webhook** trigger node
2. Configure webhook URL (e.g., `http://your-n8n-instance:5678/webhook/clawdbot`)
3. Add **HTTP Request** node to send responses back to Clawdbot Gateway

**n8n Webhook Configuration:**
```json
{
  "name": "Clawdbot Webhook",
  "type": "n8n-nodes-base.webhook",
  "parameters": {
    "httpMethod": "POST",
    "path": "clawdbot",
    "responseMode": "responseNode"
  }
}
```

### 2. Gateway Integration (Clawdbot → n8n)

**Clawdbot Gateway can trigger n8n workflows:**

1. Configure Clawdbot Gateway to point to your n8n instance
2. Set up webhook endpoints in n8n
3. Use Clawdbot's `gateway` command to trigger workflows

**Example Gateway Configuration:**
```yaml
# In clawdbot config
gateway:
  url: "http://your-n8n-instance:5678"
  webhooks:
    - name: "gitmaat-query"
      path: "/webhook/gitmaat-query"
    - name: "workflow-trigger"
      path: "/webhook/workflow-trigger"
```

### 3. Memory Integration (Clawdbot ↔ gitMaat)

**Clawdbot uses `memory/YYYY-MM-DD.md` files. Connect to gitMaat:**

1. Create n8n workflow that:
   - Receives memory updates from Clawdbot
   - Logs to gitMaat via MaatLangChain
   - Queries gitMaat and formats for Clawdbot memory

2. Set up bidirectional sync:
   - Clawdbot memory → gitMaat (via webhook)
   - gitMaat → Clawdbot memory (via Gateway cron)

**Memory Sync Workflow:**
```
Clawdbot Memory File → Webhook → n8n → gitMaat Log
gitMaat Query → Cron Job → Gateway → Clawdbot Memory Update
```

## 📋 Setup Steps

### Step 1: Create n8n Webhook Endpoints

Create these workflows in n8n:

#### Workflow 1: Clawdbot Message Handler
- **Trigger**: Webhook (`/webhook/clawdbot`)
- **Action**: Process message, query gitMaat, return response
- **Response**: Send back to Clawdbot Gateway

#### Workflow 2: gitMaat Query Handler  
- **Trigger**: Webhook (`/webhook/gitmaat-query`)
- **Action**: Query gitMaat for tasks/changes/learnings
- **Response**: Format for Clawdbot memory file

#### Workflow 3: Memory Sync
- **Trigger**: Cron (every hour) OR Webhook from Clawdbot
- **Action**: Sync Clawdbot memory → gitMaat
- **Response**: Update Clawdbot memory file

### Step 2: Configure Clawdbot Gateway

On your PC where Clawdbot is installed:

```bash
# Configure Gateway
clawdbot gateway config set url "http://your-n8n-instance:5678"

# Set up webhook endpoints
clawdbot gateway webhook add gitmaat-query "http://your-n8n-instance:5678/webhook/gitmaat-query"
clawdbot gateway webhook add workflow-trigger "http://your-n8n-instance:5678/webhook/workflow-trigger"
```

### Step 3: Set Up Memory Directory

Create memory directory structure that Clawdbot can access:

```bash
# On your PC (where Clawdbot runs)
mkdir -p ~/clawdbot-memory
# Or if shared network drive:
mkdir -p /path/to/shared/memory
```

### Step 4: Configure Automation Hooks

**Cron Jobs (via Clawdbot Gateway):**

```bash
# Check gitMaat every 15 minutes
clawdbot cron add "*/15 * * * *" "gateway trigger gitmaat-query"

# Sync memory every hour
clawdbot cron add "0 * * * *" "gateway trigger memory-sync"
```

**Hooks (event-driven):**

```bash
# Hook: When message received → query gitMaat
clawdbot hooks add message-received "gateway trigger gitmaat-query"

# Hook: When task completed → log to gitMaat
clawdbot hooks add task-completed "gateway trigger log-to-gitmaat"
```

## 🛠️ Tool Connections

### Web Search
Clawdbot already has web search enabled. Connect to your workflows:
- Use webhook to trigger n8n research workflows
- Results flow back to Clawdbot via Gateway

### Mobile Notifications
- Configure Clawdbot to send notifications
- Trigger n8n workflows that send push notifications
- Use Gateway webhooks for bidirectional communication

### Slack Integration
- Clawdbot → Gateway → n8n → Slack webhook
- n8n → Slack → Clawdbot (via Gateway)

### GitHub Integration
- Clawdbot commands → Gateway → n8n → GitHub API
- GitHub webhooks → n8n → Gateway → Clawdbot notifications

### Notion Integration
- Clawdbot → Gateway → n8n → Notion API
- Notion updates → n8n → Gateway → Clawdbot memory sync

## 🤖 Agent Domains

Define narrow, goal-oriented agents in Clawdbot:

### 1. Maat-Bench Tracker
**Scope**: Track MaatBench progress and results
**Commands**: 
- "Check MaatBench status"
- "Show latest MaatBench results"
- "Update MaatBench progress"

**Workflow**: Clawdbot → Gateway → n8n → gitMaat query → Format response

### 2. Somatic Reminder Bot
**Scope**: Personal wellness reminders
**Commands**:
- "Set somatic reminder for X"
- "Check my reminders"
- "Complete reminder X"

**Workflow**: Clawdbot → Gateway → n8n → Schedule cron → Send reminder

### 3. Research Librarian
**Scope**: Knowledge base queries, RAG searches
**Commands**:
- "Search knowledge base for X"
- "Query gitMaat for Y"
- "Research topic Z"

**Workflow**: Clawdbot → Gateway → n8n → MaatLangChain RAG → Format results

### 4. Workflow Coordinator
**Scope**: n8n workflow management via gitMaat
**Commands**:
- "Show pending tasks"
- "Trigger workflow X"
- "Check workflow status"

**Workflow**: Clawdbot → Gateway → n8n → gitMaat/Workflow API → Response

## 📝 Memory File Structure

Clawdbot uses `memory/YYYY-MM-DD.md` format. Sync with gitMaat:

**Example memory file structure:**
```markdown
# Memory - 2026-01-28

## Tasks from gitMaat
- [ ] Task 1: Description
- [ ] Task 2: Description

## Recent Changes
- Change 1: Description
- Change 2: Description

## Learnings
- Learning 1: Description
- Learning 2: Description

## Decisions
- Decision 1: Context and rationale
- Decision 2: Context and rationale
```

**Sync Process:**
1. Clawdbot memory update → Webhook → n8n → Log to gitMaat
2. gitMaat query → Cron → Gateway → Update Clawdbot memory file

## 🔄 Update Preferences

Configure how Clawdbot communicates:

### Reply Frequency
- **Brief confirmations**: For routine tasks ("Task completed", "Query done")
- **Full digests**: For complex changes (detailed summaries)
- **Only when new**: Don't reply to every "Yo", only when actionable

### Configuration
Set in Clawdbot config or via memory file:
```yaml
updates:
  frequency: "only-when-new"
  style: "brief-confirmations"
  full-digests: ["complex-changes", "research-results"]
```

## 🚀 Next Steps

1. **Create n8n workflows** for webhook endpoints
2. **Configure Clawdbot Gateway** on your PC
3. **Set up memory sync** between Clawdbot and gitMaat
4. **Configure automation hooks** and cron jobs
5. **Test integration** with simple commands
6. **Define agent domains** for specific use cases

## 📚 Resources

- **Clawdbot Docs**: https://docs.clawd.bot
- **Gateway Docs**: https://docs.clawd.bot/cli/gateway
- **Webhooks**: https://docs.clawd.bot/automation/webhook
- **Hooks**: https://docs.clawd.bot/hooks
- **Memory**: https://docs.clawd.bot/cli/memory
- **n8n Webhooks**: https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.webhook/

## 🎯 Integration Checklist

- [ ] n8n webhook endpoints created
- [ ] Clawdbot Gateway configured
- [ ] Memory directory set up
- [ ] Memory sync workflow created
- [ ] Automation hooks configured
- [ ] Cron jobs set up
- [ ] Agent domains defined
- [ ] Tool connections configured (Slack, GitHub, Notion)
- [ ] Test integration end-to-end
