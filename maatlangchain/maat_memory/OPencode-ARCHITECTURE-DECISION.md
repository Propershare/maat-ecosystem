# OpenCode Architecture Decision: Plug-and-Play Integration

## Question: Standalone or Plug-and-Play?

**Answer: Plug-and-Play Wrapper** ✅

## Why Plug-and-Play?

### ✅ Cross-Terminal Memory Requirement

**Critical Requirement:** OpenCode needs to remember sessions across different terminals.

**Problem with Standalone:**
- File-based storage = no cross-terminal sync
- In-memory storage = lost on restart
- Each terminal = separate memory = no sharing

**Solution with Plug-and-Play:**
- PostgreSQL = shared database = all terminals see same data
- Sessions persist in database = survive restarts
- One source of truth = guaranteed cross-terminal memory

### ✅ Plug-and-Play Benefits

1. **No Duplication**: Use our existing PostgreSQL backend
2. **Production-Ready**: Already tested, migrated, documented
3. **Vector Search**: Semantic queries already implemented
4. **Constitutional Governance**: Keep your excellent framework
5. **Easy Integration**: Just import and use

## Architecture

```
┌─────────────────────────────────────────────┐
│  OpenCode MCP Server (Your Code)          │
│  - MCP Protocol Handler                    │
│  - Constitutional Validator              │
│  - Agent Registry                          │
│  - Three-Ring Classification               │
└──────────────────┬──────────────────────────┘
                   │
                   │ Uses (imports)
                   ▼
┌─────────────────────────────────────────────┐
│  MaatMemoryPostgres (Our Backend)          │
│  - PostgreSQL Connection                    │
│  - Vector Search (pgvector)                 │
│  - Session Management                       │
│  - Conversation Logging                     │
│  - Audit Trail                              │
└──────────────────┬──────────────────────────┘
                   │
                   │ Stores in
                   ▼
┌─────────────────────────────────────────────┐
│  PostgreSQL Database (Shared)              │
│  - maat_sessions                            │
│  - maat_conversations (with embeddings)     │
│  - maat_audit_trail                         │
│  - maat_agent_memory                        │
│  - All other tables                         │
└─────────────────────────────────────────────┘
```

## How Cross-Terminal Memory Works

### Terminal 1 (Computer A):
```python
memory = MaatMemoryPostgres(embeddings_model=embeddings)
session_id = memory.start_session('opencode', 'Working on API')
memory.log_conversation('opencode', 'What is Maat?', 'Maat is truth.')
```

### Terminal 2 (Computer B, or same computer):
```python
memory = MaatMemoryPostgres(embeddings_model=embeddings)  # Same database!
results = memory.search_conversations('Maat', agent='opencode')
# ✅ Finds conversation from Terminal 1!
```

**Why It Works:**
- Both terminals connect to same PostgreSQL database
- Database is shared (via network or local connection)
- Sessions stored in database, not in memory
- Vector search queries same database

## What You Keep vs. What You Get

### What You Keep (Your Excellent Work):
- ✅ **Constitutional Validator**: Your Maat validation logic
- ✅ **Agent Registry**: Your multi-agent coordination
- ✅ **MCP Server**: Your OpenCode protocol handler
- ✅ **Three-Ring Classification**: Your governance model

### What You Get (Our Production Backend):
- ✅ **PostgreSQL Storage**: No data loss, ACID transactions
- ✅ **Cross-Terminal Memory**: Shared database = guaranteed sync
- ✅ **Vector Search**: Semantic queries (find by meaning)
- ✅ **Production-Ready**: Tested, migrated, documented
- ✅ **Scalability**: Handles millions of conversations

## Integration Effort

**Time Required:** ~30 minutes

**Steps:**
1. Install dependencies (5 min)
2. Import `MaatMemoryPostgres` (1 min)
3. Replace storage calls (10 min)
4. Test cross-terminal memory (10 min)
5. Deploy (4 min)

**Result:** Plug-and-play cross-terminal memory! 🎯

## Code Example

### Before (File-Based, No Cross-Terminal):
```python
class MAATMemoryServer:
    def __init__(self):
        self.sessions: Dict[str, Dict[str, Any]] = {}  # ❌ In-memory, lost on restart
    
    async def save_session(self, ...):
        self.sessions[session_id] = session  # ❌ Only in this terminal's memory
```

### After (PostgreSQL, Cross-Terminal):
```python
class MAATMemoryServer:
    def __init__(self):
        from maat_memory.memory_postgres import MaatMemoryPostgres
        from langchain_huggingface import HuggingFaceEmbeddings
        
        embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        self.memory = MaatMemoryPostgres(embeddings_model=embeddings)  # ✅ Shared database
    
    async def save_session(self, ...):
        session_id = self.memory.start_session(...)  # ✅ Stored in PostgreSQL
        self.memory.log_conversation(...)  # ✅ Available to all terminals
```

## Why Not Standalone?

### Standalone Would Require:
- ❌ Building PostgreSQL integration (we already have it)
- ❌ Building vector search (we already have it)
- ❌ Building migration tools (we already have it)
- ❌ Testing cross-terminal sync (we already tested it)
- ❌ Duplicating code (violates DRY principle)

### Plug-and-Play Gives You:
- ✅ Use existing, tested code
- ✅ Focus on your MCP server and governance
- ✅ Guaranteed cross-terminal memory
- ✅ Production-ready from day one

## Decision Matrix

| Requirement | Standalone | Plug-and-Play |
|------------|-----------|---------------|
| Cross-Terminal Memory | ❌ Need to build | ✅ Already works |
| Vector Search | ❌ Need to build | ✅ Already works |
| PostgreSQL Integration | ❌ Need to build | ✅ Already works |
| Production-Ready | ❌ Need to test | ✅ Already tested |
| Constitutional Governance | ✅ You have it | ✅ You keep it |
| MCP Server | ✅ You have it | ✅ You keep it |
| Integration Time | ❌ Weeks | ✅ 30 minutes |

## Conclusion

**Recommendation: Plug-and-Play Integration**

- ✅ Meets cross-terminal memory requirement
- ✅ Plug-and-play (just import and use)
- ✅ Keeps your excellent constitutional framework
- ✅ Production-ready from day one
- ✅ No code duplication

**Next Step:** See `OPencode-INTEGRATION-GUIDE.md` for detailed implementation.

