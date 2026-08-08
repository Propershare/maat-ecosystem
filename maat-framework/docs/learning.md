# Learning — How Memory Works

## Two Types of Learning

### 1. RAG Memory (Always On)

Every conversation is logged to gitMaat (PostgreSQL + pgvector).
Before responding, the agent queries for relevant past interactions.

```
User: "What did we decide about the API?"
    → query_memory("API decision") 
    → Finds: 3 days ago you discussed REST vs GraphQL
    → Agent responds with context: "We decided on REST because..."
```

This gives you 90% of "learning" with zero fine-tuning.

### 2. Fine-Tuning (Optional, Periodic)

For teaching the model **new behaviors** (not just facts):

```bash
maat learn --train
```

This:
1. Extracts quality interaction pairs from gitMaat
2. Filters out mundane ops (ls, git status)
3. Formats as LoRA training data
4. Runs fine-tuning via Unsloth
5. Converts to GGUF
6. Registers in Ollama

**When to fine-tune:**
- You want the model to adopt your communication style
- You need it to learn new tool-calling patterns
- Domain-specific knowledge that RAG can't cover well

**When NOT to fine-tune:**
- Just to "make it smarter" — RAG does this already
- On raw chat logs — too noisy, model learns bad habits
- Every day — weekly or monthly is plenty

## Database Tables

| Table | What It Stores | Used For |
|-------|---------------|----------|
| `maat_conversations` | Every user↔agent exchange | RAG context retrieval |
| `maat_tasks` | Tasks created/completed | Progress tracking |
| `maat_decisions` | Significant decisions + rationale | Decision history |
| `maat_learnings` | Insights and lessons learned | Knowledge base |
| `maat_changes` | Code/config/infra changes | Change log |
| `maat_sessions` | Session metadata | Session tracking |
| `maat_audit_trail` | All actions + Maat compliance | Security audit |

## Memory Query

```python
from maat.learn import query_memory

# Search by text similarity
results = query_memory("deployment strategy", limit=5)
for r in results:
    print(f"{r['agent']}: {r['user_query'][:80]}")

# Filter by agent
results = query_memory("auth", agent="tehuti", limit=3)
```

## Logging

```python
from maat.learn import log_task, log_decision, log_learning, log_change

# Log a task
log_task("Deploy v2.1", "Push to production with new auth", agent="tehuti")

# Log a decision
log_decision(
    context="Choosing between REST and GraphQL for the API",
    decision="REST",
    rationale="Simpler, team knows it, good enough for our scale",
    agent="tehuti"
)

# Log a learning
log_learning(
    category="architecture",
    description="Flat file memory doesn't scale past 100KB",
    context="MEMORY.md hit 280k chars and broke token limits",
    agent="tehuti"
)

# Log a change
log_change(
    change_type="code",
    description="Replaced flat-file memory with gitMaat queries",
    files=["maat/learn.py", "maat/agent.py"],
    agent="tehuti"
)
```

## Evolution Loop

```
Week 1: Use the agent normally
         → Conversations logged to gitMaat
         → Agent uses RAG for context

Week 2: Run `maat learn --train`
         → Quality pairs extracted
         → LoRA fine-tuning on your interactions
         → Improved model deployed

Week 3: Agent now has your communication patterns
         baked into the model weights
         + continues learning via RAG

Repeat monthly.
```

The model gets better at being YOUR assistant, not just any assistant.
