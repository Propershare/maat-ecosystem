# MaatLangChain Pipeline MCP Server

## 🎯 Purpose

MaatLangChain Pipeline connects Tehuti Core with MaatLangChain RAG/agents for long workflows orchestrated by n8n.

## 🛠️ Tools Available

1. **`search_knowledge_base`** - Search MaatLangChain knowledge base using RAG
2. **`rag_query`** - Full RAG query with LLM integration
3. **`execute_pipeline_step`** - Execute a single pipeline step
4. **`execute_research_pipeline`** - Execute full research pipeline (gitMaat + RAG + Tehuti Core)
5. **`trigger_n8n_workflow`** - Trigger n8n workflows for orchestration

## 🔗 Integration

- **Tehuti Core** (Port 8014) - Filesystem/terminal operations
- **MaatLangChain RAG** - Knowledge base search and document generation
- **gitMaat** - Coordination and memory
- **n8n** (via Tehuti Integration) - Workflow orchestration

## 🚀 Running the Server

### Standalone Test
```bash
cd /home/suspect/.n8n/mcp-servers/maatlangchain-pipeline
python3 maatlangchain_pipeline_server.py
```

### With mcpo (for WebUI integration)
```bash
uv tool uvx mcpo --host 127.0.0.1 --port 8026 -- python3 /home/suspect/.n8n/mcp-servers/maatlangchain-pipeline/maatlangchain_pipeline_server.py
```

## 🔒 Requirements

- `PGVECTOR_DB_URL` environment variable set
- MaatLangChain dependencies installed
- Tehuti Core running on port 8014
- PostgreSQL with pgvector extension

## 🏛️ Maat Principles

- **Truth**: Accurate RAG results, verified sources
- **Balance**: Combines multiple tools (RAG, gitMaat, Tehuti Core)
- **Order**: Structured pipeline execution
- **Justice**: Proper attribution of sources
- **Self-Reflection**: Logs all pipeline executions to gitMaat


## 🎯 Purpose

MaatLangChain Pipeline MCP Server exposes RAG, agents, and knowledge base capabilities as tools for WebUI. It connects to Tehuti Core for filesystem/terminal operations and integrates with n8n workflows for long-running tasks.

## 🛠️ Tools Available

1. **`search_knowledge_base`** - Search MaatLangChain knowledge base using RAG
2. **`query_gitmaat_advanced`** - Advanced gitMaat queries with semantic search
3. **`execute_research_pipeline`** - Execute full research pipeline (MaatLangChain + Tehuti Core)
4. **`trigger_n8n_workflow`** - Trigger n8n workflows (connects to Tehuti Integration)
5. **`create_pipeline_task`** - Create tasks in gitMaat for pipeline execution
6. **`get_pipeline_status`** - Get status of pipeline tasks

## 🚀 Running the Server

### Standalone Test
```bash
cd /home/suspect/.n8n/mcp-servers/maatlangchain-pipeline
python3 maatlangchain_pipeline_server.py
```

### With MCP Inspector (for testing)
```bash
mcp-inspector stdio python3 /home/suspect/.n8n/mcp-servers/maatlangchain-pipeline/maatlangchain_pipeline_server.py
```

### Via mcpo (for WebUI integration)
```bash
uv tool uvx mcpo --host 127.0.0.1 --port 8020 -- python3 /home/suspect/.n8n/mcp-servers/maatlangchain-pipeline/maatlangchain_pipeline_server.py
```

## 🔗 Integration

- **Tehuti Core**: Uses for filesystem/terminal operations
- **Tehuti Integration**: Uses for n8n workflow triggering
- **gitMaat**: Uses for coordination and task management
- **MaatLangChain RAG**: Uses for knowledge base search

## 🏛️ Maat Principles

- **Truth**: Accurate RAG search, proper gitMaat queries
- **Balance**: Combines multiple tools (RAG, n8n, gitMaat)
- **Order**: Structured pipeline execution
- **Justice**: Proper task coordination via gitMaat
- **Self-Reflection**: Logs all pipeline executions

## 📝 Next Steps

1. Test server standalone
2. Register in Open WebUI (port 8020)
3. Test tool execution from WebUI
4. Create n8n workflows that use pipeline tools

