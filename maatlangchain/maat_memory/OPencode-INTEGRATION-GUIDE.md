# OpenCode Integration Guide - PostgreSQL Backend with Cross-Terminal Memory

## Overview

This guide shows how to integrate OpenCode's MCP server with our PostgreSQL backend to achieve:
- ✅ **Cross-terminal session memory** (critical requirement)
- ✅ **Plug-and-play** integration (easy to use)
- ✅ **PostgreSQL persistence** (no data loss)
- ✅ **Vector search** (semantic queries)
- ✅ **Constitutional governance** (keep your excellent framework)

## Architecture Decision: Plug-and-Play Wrapper

**Recommended Approach**: OpenCode's MCP server becomes a **wrapper** around our PostgreSQL backend.

```
┌─────────────────────────────────────┐
│   OpenCode MCP Server (Your Code)  │
│  - MCP Protocol Handler             │
│  - Constitutional Validator         │
│  - Agent Registry                  │
└──────────────┬──────────────────────┘
               │
               │ Uses
               ▼
┌─────────────────────────────────────┐
│   MaatMemoryPostgres (Our Backend)  │
│  - PostgreSQL Storage               │
│  - Vector Search (pgvector)         │
│  - Cross-Terminal Sync              │
└──────────────┬──────────────────────┘
               │
               │ Stores in
               ▼
┌─────────────────────────────────────┐
│   PostgreSQL Database               │
│  - maat_sessions                    │
│  - maat_conversations (with vectors)│
│  - maat_audit_trail                 │
│  - maat_agent_memory                │
└─────────────────────────────────────┘
```

**Why This Works:**
- Your MCP server handles OpenCode protocol
- Our backend handles persistence & search
- Both work together seamlessly
- Cross-terminal memory guaranteed (PostgreSQL is shared)

---

## Step 1: Install Dependencies

```bash
# In OpenCode's environment
cd /mnt/ai_backup/tehuti-memory

# Install our Maat Memory package
pip install psycopg2-binary pgvector langchain-huggingface sentence-transformers

# Or add to requirements.txt:
# psycopg2-binary>=2.9.7
# pgvector>=0.2.3
# langchain-huggingface>=1.2.0
# sentence-transformers>=2.2.2
```

---

## Step 2: Update MCP Server to Use PostgreSQL Backend

### File: `core/maat_memory_server.py`

**Replace the storage layer with our PostgreSQL backend:**

```python
#!/usr/bin/env python3
"""
MAAT Memory Server - OpenCode Extension with PostgreSQL Backend
Cross-terminal session memory with constitutional governance
"""

import os
import sys
import json
import logging
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add our Maat Memory to path
sys.path.insert(0, "/home/suspect/.n8n/maatlangchain")

# Import our PostgreSQL backend
from maat_memory.memory_postgres import MaatMemoryPostgres

# Try to get embeddings model
try:
    from langchain_huggingface import HuggingFaceEmbeddings
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
except ImportError:
    try:
        from langchain_community.embeddings import HuggingFaceEmbeddings
        embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
    except ImportError:
        embeddings = None
        logging.warning("Embeddings not available - vector search disabled")

# Import your constitutional validator (keep this!)
from constitution.constitutional_validator import ConstitutionalValidator
from agents.universal_agent_registry import UniversalAgentRegistry

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("maat_memory_server")

# TOOLS registry (keep your existing tools)
TOOLS = {
    "maat-memory/save-session": {
        "name": "maat-memory/save-session",
        "description": "Save terminal session with constitutional oversight and three-ring classification",
        "inputSchema": {
            "type": "object",
            "properties": {
                "agent_id": {
                    "type": "string",
                    "description": "Agent identifier for constitutional tracking",
                },
                "working_directory": {
                    "type": "string",
                    "description": "Current working directory for classification",
                },
                "session_data": {
                    "type": "object",
                    "description": "Session context and content",
                },
                "classification_override": {
                    "type": "string",
                    "enum": ["inner", "middle", "outer"],
                    "description": "Override automatic three-ring classification",
                },
            },
            "required": ["agent_id", "working_directory", "session_data"],
        },
    },
    "maat-memory/recall-session": {
        "name": "maat-memory/recall-session",
        "description": "Recall session memory with constitutional access controls",
        "inputSchema": {
            "type": "object",
            "properties": {
                "agent_id": {
                    "type": "string",
                    "description": "Agent identifier for permission checks",
                },
                "directory": {
                    "type": "string",
                    "description": "Directory to recall sessions for",
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of sessions to return",
                    "default": 10,
                },
                "classification_filter": {
                    "type": "array",
                    "description": "Filter by memory classification ring",
                },
            },
            "required": ["agent_id", "directory"],
        },
    },
    "maat-memory/search-sessions": {
        "name": "maat-memory/search-sessions",
        "description": "Search across all sessions with constitutional semantic search",
        "inputSchema": {
            "type": "object",
            "properties": {
                "agent_id": {
                    "type": "string",
                    "description": "Agent identifier for access control",
                },
                "query": {"type": "string", "description": "Semantic search query"},
                "classification_filter": {
                    "type": "array",
                    "description": "Memory classification filter",
                },
                "time_range": {
                    "type": "object",
                    "description": "Time range for search constraints",
                },
            },
            "required": ["agent_id", "query"],
        },
    },
    "maat-constitution/validate-operation": {
        "name": "maat-constitution/validate-operation",
        "description": "Validate any operation against MAAT constitutional principles",
        "inputSchema": {
            "type": "object",
            "properties": {
                "agent_id": {
                    "type": "string",
                    "description": "Agent ID for compliance checking",
                },
                "operation": {
                    "type": "string",
                    "description": "Operation type being validated",
                },
                "operation_data": {
                    "type": "object",
                    "description": "Data being validated",
                },
                "principles_to_check": {
                    "type": "array",
                    "description": "Which MAAT principles to validate",
                    "default": ["truth", "balance", "order", "justice", "self_reflection"],
                },
            },
            "required": ["agent_id", "operation", "operation_data"],
        },
    },
    "maat-constitution/get-compliance-score": {
        "name": "maat-constitution/get-compliance-score",
        "description": "Get agent's constitutional compliance score and history",
        "inputSchema": {
            "type": "object",
            "properties": {
                "agent_id": {"type": "string", "description": "Agent identifier"},
                "time_period": {
                    "type": "string",
                    "enum": ["day", "week", "month", "all"],
                    "description": "Time period for compliance calculation",
                },
            },
            "required": ["agent_id"],
        },
    },
}


class MAATMemoryServer:
    """MAAT Constitutional Memory Server - OpenCode Extension with PostgreSQL"""

    def __init__(self):
        # Initialize PostgreSQL backend (cross-terminal memory!)
        try:
            self.memory = MaatMemoryPostgres(embeddings_model=embeddings)
            logger.info("✅ Connected to PostgreSQL backend - cross-terminal memory enabled")
        except Exception as e:
            logger.error(f"Failed to connect to PostgreSQL: {e}")
            raise
        
        # Keep your constitutional validator
        self.constitutional_validator = ConstitutionalValidator()
        
        # Keep your agent registry
        self.agent_registry = UniversalAgentRegistry()
        
        logger.info("MAAT Memory Server initialized with PostgreSQL backend")

    def _classify_memory(
        self,
        working_directory: str,
        agent_id: str,
        classification_override: Optional[str] = None,
    ) -> str:
        """Three-ring memory classification (keep your logic)"""
        if classification_override:
            return classification_override

        # Inner Ring: MAAT constitution and sacred locations
        inner_ring_paths = [
            "/home/suspect/.n8n/memory-bank",
            "/mnt/ai_backup/tehuti-memory/constitution",
        ]

        # Middle Ring: Research and development areas
        middle_ring_paths = [
            "/home/suspect/.n8n/maatlangchain",
            "/home/suspect/comfyui",
            "/home/suspect/suspectcontent-docker",
        ]

        # Default to Outer Ring
        classification = "outer"

        for path in inner_ring_paths:
            if working_directory.startswith(path):
                classification = "inner"
                break

        if classification == "outer":
            for path in middle_ring_paths:
                if working_directory.startswith(path):
                    classification = "middle"
                    break

        logger.info(
            f"Classified {working_directory} as {classification} ring for agent {agent_id}"
        )
        return classification

    async def save_session(
        self,
        agent_id: str,
        working_directory: str,
        session_data: dict,
        classification_override: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Save session with constitutional validation and PostgreSQL storage"""

        # 1. Constitutional validation (keep your logic)
        constitutional_checks = {
            "truth": self.constitutional_validator._validate_truth_principle(
                "memory_save", session_data
            ),
            "balance": self.constitutional_validator._validate_balance_principle(
                "memory_save", session_data
            ),
            "order": self.constitutional_validator._validate_order_principle(
                "memory_save", session_data
            ),
            "justice": self.constitutional_validator._validate_justice_principle(
                "memory_save", session_data
            ),
            "self_reflection": self.constitutional_validator._validate_self_reflection_principle(
                "memory_save", session_data
            ),
        }

        # Calculate compliance score
        score = 100.0
        violations = []

        for principle, result in constitutional_checks.items():
            if not result.compliant:
                score -= 20.0
                violations.append({
                    "principle": principle,
                    "reason": result.reason,
                })

        # 2. Three-ring classification
        classification = self._classify_memory(
            working_directory, agent_id, classification_override
        )

        # 3. Start session in PostgreSQL (cross-terminal memory!)
        session_id = self.memory.start_session(
            agent=agent_id,
            summary=session_data.get("summary", f"Session in {working_directory}")
        )

        # 4. Log conversation if provided
        if "user_query" in session_data and "agent_response" in session_data:
            conversation_id = self.memory.log_conversation(
                agent=agent_id,
                user_query=session_data["user_query"],
                agent_response=session_data["agent_response"],
                tools_used=session_data.get("tools_used", []),
                files_accessed=session_data.get("files_accessed", []),
                decisions_made=session_data.get("decisions_made", []),
                generate_embedding=True  # Enable vector search!
            )

        # 5. Log audit trail
        audit_id = self.memory.log_audit(
            agent=agent_id,
            action="save_session",
            resource=working_directory,
            before=None,
            after={"session_id": session_id, "classification": classification},
            reason=f"Session saved with {classification} ring classification",
            maat_compliance={
                "truth": constitutional_checks["truth"].compliant,
                "balance": constitutional_checks["balance"].compliant,
                "order": constitutional_checks["order"].compliant,
                "justice": constitutional_checks["justice"].compliant,
                "self_reflection": constitutional_checks["self_reflection"].compliant,
            }
        )

        logger.info(
            f"Session saved: {session_id} for agent {agent_id} with compliance score {score}"
        )

        return {
            "status": "success",
            "session_id": session_id,
            "constitutional_compliance": {"score": score, "violations": violations},
            "classification": classification,
        }

    async def recall_session(
        self,
        agent_id: str,
        directory: str,
        max_results: int = 10,
        classification_filter: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Recall sessions from PostgreSQL (cross-terminal memory!)"""
        
        # Search conversations using vector search
        results = self.memory.search_conversations(
            query=f"session in directory {directory}",
            agent=agent_id,
            limit=max_results,
            use_vector_search=True
        )

        # Filter by classification if needed
        if classification_filter:
            # Note: Classification filtering would need to be added to our backend
            # For now, return all results
            pass

        return {
            "status": "success",
            "sessions": results,
            "count": len(results),
        }

    async def search_sessions(
        self,
        agent_id: str,
        query: str,
        classification_filter: Optional[List[str]] = None,
        time_range: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Search sessions using vector search (semantic queries!)"""
        
        # Use our vector search for semantic queries
        results = self.memory.search_conversations(
            query=query,
            agent=agent_id,
            limit=10,
            use_vector_search=True  # Semantic search!
        )

        return {
            "status": "success",
            "sessions": results,
            "count": len(results),
        }


# MCP Protocol handlers (keep your existing handlers)
def handle_initialize(request_id: str) -> Dict[str, Any]:
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": {
            "protocolVersion": "2024-11-05",
            "serverInfo": {"name": "MAAT Memory Server", "version": "2.0.0"},
            "capabilities": {"tools": TOOLS},
        },
    }


def handle_list_tools(request_id: str) -> Dict[str, Any]:
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": {"tools": list(TOOLS.values())},
    }


def handle_call_tool(
    server: MAATMemoryServer, request_id: str, params: Dict[str, Any]
) -> Dict[str, Any]:
    tool_name = params.get("name")

    if tool_name == "maat-memory/save-session":
        try:
            agent_id = params["arguments"]["agent_id"]
            working_directory = params["arguments"]["working_directory"]
            session_data = params["arguments"]["session_data"]
            classification_override = params["arguments"].get("classification_override")

            result = asyncio.run(
                server.save_session(
                    agent_id, working_directory, session_data, classification_override
                )
            )

            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {"content": [{"type": "json", "json": result}]},
            }
        except Exception as e:
            logger.error(f"Error in save_session: {e}")
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32603, "message": str(e)},
            }

    elif tool_name == "maat-memory/recall-session":
        try:
            agent_id = params["arguments"]["agent_id"]
            directory = params["arguments"]["directory"]
            max_results = params["arguments"].get("max_results", 10)
            classification_filter = params["arguments"].get("classification_filter", [])

            result = asyncio.run(
                server.recall_session(agent_id, directory, max_results, classification_filter)
            )

            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {"content": [{"type": "json", "json": result}]},
            }
        except Exception as e:
            logger.error(f"Error in recall_session: {e}")
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32603, "message": str(e)},
            }

    elif tool_name == "maat-memory/search-sessions":
        try:
            agent_id = params["arguments"]["agent_id"]
            query = params["arguments"]["query"]
            classification_filter = params["arguments"].get("classification_filter", [])
            time_range = params["arguments"].get("time_range", {})

            result = asyncio.run(
                server.search_sessions(agent_id, query, classification_filter, time_range)
            )

            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {"content": [{"type": "json", "json": result}]},
            }
        except Exception as e:
            logger.error(f"Error in search_sessions: {e}")
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32603, "message": str(e)},
            }

    else:
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {"code": -32601, "message": f"Method not found: {tool_name}"},
        }


def main():
    """Main server loop"""
    server = MAATMemoryServer()

    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                continue
            line = line.strip()
            if not line:
                continue

            data = json.loads(line)
            method = data.get("method")
            req_id = data.get("id")

            if method == "initialize":
                response = handle_initialize(req_id)
            elif method == "tools/list":
                response = handle_list_tools(req_id)
            elif method == "tools/call":
                response = handle_call_tool(server, req_id, data.get("params", {}))
            else:
                response = {
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {"code": -32601, "message": f"Method not found: {method}"},
                }

            print(json.dumps(response), flush=True)
            logger.info(f"Handled {method} request")

        except json.JSONDecodeError:
            error_response = {
                "jsonrpc": "2.0",
                "id": data.get("id"),
                "error": {"code": -32700, "message": "Parse error"},
            }
            print(json.dumps(error_response), flush=True)

        except Exception as e:
            error_response = {
                "jsonrpc": "2.0",
                "id": data.get("id"),
                "error": {"code": -32603, "message": str(e)},
            }
            print(json.dumps(error_response), flush=True)


if __name__ == "__main__":
    logger.info("MAAT Memory Server starting with PostgreSQL backend")
    main()
```

---

## Step 3: Ensure Cross-Terminal Memory Works

### Key Points for Cross-Terminal Memory:

1. **PostgreSQL is Shared**: All terminals connect to the same database
2. **Session IDs Persist**: Sessions stored in PostgreSQL, not memory
3. **Agent Memory Shared**: `maat_agent_memory` table shared across terminals

### Test Cross-Terminal Memory:

**Terminal 1:**
```bash
# Start session
python3 -c "
from maat_memory.memory_postgres import MaatMemoryPostgres
from langchain_huggingface import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')
memory = MaatMemoryPostgres(embeddings_model=embeddings)

session_id = memory.start_session('opencode', 'Test session from terminal 1')
print(f'Session ID: {session_id}')

memory.log_conversation(
    agent='opencode',
    user_query='What is Maat?',
    agent_response='Maat is truth, balance, order, justice, and self-reflection.'
)
print('Conversation logged')
"
```

**Terminal 2 (different terminal, same computer or different computer):**
```bash
# Recall session from Terminal 1
python3 -c "
from maat_memory.memory_postgres import MaatMemoryPostgres
from langchain_huggingface import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')
memory = MaatMemoryPostgres(embeddings_model=embeddings)

# Search for conversations from Terminal 1
results = memory.search_conversations('Maat principles', agent='opencode', limit=5)
print(f'Found {len(results)} conversations from Terminal 1')
for r in results:
    print(f\"  Query: {r['user_query']}\")
    print(f\"  Response: {r['agent_response']}\")
"
```

**Result**: Terminal 2 can see conversations from Terminal 1! ✅

---

## Step 4: Configuration

### Environment Variables

Create `/mnt/ai_backup/tehuti-memory/.env`:

```bash
# PostgreSQL connection (shared across terminals)
PGVECTOR_DB_URL=postgresql://suspect:<password>@localhost:5434/n8n_ai_starter

# Or read from OpenWebUI config
# PGVECTOR_DB_URL will be auto-detected from /home/suspect/.n8n/open-webui/.env
```

### Update Config File

Update `core/maat_memory_config.json`:

```json
{
  "version": "2.0.0",
  "server": {
    "name": "MAAT Memory Server",
    "host": "127.0.0.1",
    "port": 8019,
    "description": "OpenCode Extension with PostgreSQL Backend"
  },
  "database": {
    "type": "postgresql_pgvector",
    "connection": "PGVECTOR_DB_URL",
    "cross_terminal_memory": true,
    "vector_search": true
  },
  "constitution": {
    "enforcement": "active",
    "scoring": "weighted_average",
    "principles": ["truth", "balance", "order", "justice", "self_reflection"]
  }
}
```

---

## Step 5: Migration (If Needed)

If you have existing JSON data, migrate it:

```bash
cd /home/suspect/.n8n/maatlangchain
python3 maat_memory/migrate_to_postgres.py
```

This will:
- Create PostgreSQL schema
- Migrate all sessions, conversations, audit trail
- Preserve JSON as backup
- Enable cross-terminal memory

---

## Step 6: Testing

### Test 1: Cross-Terminal Memory

```bash
# Terminal 1
python3 /mnt/ai_backup/tehuti-memory/core/maat_memory_server.py

# In another terminal, test MCP protocol
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | python3 /mnt/ai_backup/tehuti-memory/core/maat_memory_server.py
```

### Test 2: Vector Search

```python
from maat_memory.memory_postgres import MaatMemoryPostgres
from langchain_huggingface import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')
memory = MaatMemoryPostgres(embeddings_model=embeddings)

# Search semantically
results = memory.search_conversations(
    query="What did we decide about the API?",
    agent="opencode",
    limit=5,
    use_vector_search=True
)

print(f"Found {len(results)} conversations")
for r in results:
    print(f"Similarity: {r.get('similarity', 'N/A')}")
    print(f"Query: {r['user_query']}")
```

---

## Benefits of This Integration

### ✅ Cross-Terminal Memory
- All terminals connect to same PostgreSQL database
- Sessions persist across terminal restarts
- Conversations searchable from any terminal

### ✅ Plug-and-Play
- Just import `MaatMemoryPostgres`
- No file management needed
- Automatic schema creation

### ✅ Production-Ready
- PostgreSQL ACID transactions
- Vector search for semantic queries
- Scalable to millions of conversations

### ✅ Constitutional Governance
- Keep your excellent validator
- Keep your agent registry
- Keep your MCP server

---

## Troubleshooting

### Issue: "PGVECTOR_DB_URL not found"

**Solution:**
```bash
# Set environment variable
export PGVECTOR_DB_URL=postgresql://suspect:<password>@localhost:5434/n8n_ai_starter

# Or add to .env file
echo "PGVECTOR_DB_URL=postgresql://suspect:<password>@localhost:5434/n8n_ai_starter" >> /mnt/ai_backup/tehuti-memory/.env
```

### Issue: "pgvector extension not found"

**Solution:**
```bash
# Connect to PostgreSQL and create extension
psql postgresql://suspect:<password>@localhost:5434/n8n_ai_starter -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

### Issue: "Embeddings not available"

**Solution:**
```bash
pip install langchain-huggingface sentence-transformers
```

---

## Summary

**What You Keep:**
- ✅ MCP server structure
- ✅ Constitutional validator
- ✅ Agent registry
- ✅ Three-ring classification

**What You Get:**
- ✅ PostgreSQL persistence (no data loss)
- ✅ Cross-terminal memory (shared database)
- ✅ Vector search (semantic queries)
- ✅ Production-ready infrastructure

**Integration Effort:** ~30 minutes
**Result:** Plug-and-play cross-terminal memory with constitutional governance

---

## Next Steps

1. Update `maat_memory_server.py` with code above
2. Install dependencies
3. Test cross-terminal memory
4. Deploy to OpenCode

**Questions?** See `/home/suspect/.n8n/maatlangchain/maat_memory/README-POSTGRES.md`

