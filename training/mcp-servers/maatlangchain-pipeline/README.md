# MaatLangChain Pipeline API

**Maat-Aligned Tool Documentation**

## Overview

RAG, agents, and knowledge base pipeline - connects to Tehuti Core and n8n workflows

**Version**: 1.0.0  
**Total Tools**: 7

## Maat Principles Alignment

### Truth (Maat)
RAG, agents, and knowledge base operations

### Balance (Maat)
Balance retrieval accuracy with response speed

### Order (Maat)
Structured RAG pipeline

### Justice (Maat)
Proper source attribution

### Self-Reflection (Maat)
Learn from RAG patterns

## Available Tools

### Search Knowledge Base

**Operation ID**: `search_knowledge_base_tools_search_knowledge_base_post`  
**Path**: `POST /tools/search_knowledge_base`

Search MaatLangChain knowledge base using RAG.

**Request Body**: See OpenAPI spec for schema details

### Query Gitmaat Advanced

**Operation ID**: `query_gitmaat_advanced_tools_query_gitmaat_advanced_post`  
**Path**: `POST /tools/query_gitmaat_advanced`

Advanced gitMaat query with semantic search support.

**Request Body**: See OpenAPI spec for schema details

### Execute Research Pipeline

**Operation ID**: `execute_research_pipeline_tools_execute_research_pipeline_post`  
**Path**: `POST /tools/execute_research_pipeline`

Execute full research pipeline using MaatLangChain + Tehuti Core.

**Request Body**: See OpenAPI spec for schema details

### Create Pipeline Task

**Operation ID**: `create_pipeline_task_tools_create_pipeline_task_post`  
**Path**: `POST /tools/create_pipeline_task`

Create a task in gitMaat for pipeline execution.

**Request Body**: See OpenAPI spec for schema details

### Trigger N8N Workflow

**Operation ID**: `trigger_n8n_workflow_tools_trigger_n8n_workflow_post`  
**Path**: `POST /tools/trigger_n8n_workflow`

Trigger an n8n workflow (connects to Tehuti Integration).

**Request Body**: See OpenAPI spec for schema details

### Openapi

**Operation ID**: `openapi_openapi_json_get`  
**Path**: `GET /openapi.json`

Return OpenAPI spec for WebUI integration.

### Health

**Operation ID**: `health_health_get`  
**Path**: `GET /health`

Health check endpoint.

## Use Cases

- RAG queries
- Agent operations
- Knowledge base management

## Common Patterns

- Query → Retrieve → Process → Return

## Tool Selection Decision Tree

1. **Identify the task domain**
   - System operations → `tehuti-core`
   - Workflow automation → `n8n-mcp`
   - File operations → `filesystem-mcp`
   - Database queries → `postgres-mcp`
   - Image generation → `comfyui-intelligent`
   - Audio generation → `tehuti-audio`
   - RAG/Knowledge → `maatlangchain-pipeline`

2. **Check tool availability**
   - Verify tool is accessible (port check)
   - Check OpenAPI spec for available operations

3. **Select appropriate tool**
   - Match user intent to tool capability
   - Consider tool chaining for complex tasks

4. **Execute with Maat principles**
   - Truth: Accurate parameters
   - Balance: Appropriate tool selection
   - Order: Systematic execution
   - Justice: Proper attribution
   - Self-Reflection: Learn from results

## Error Handling

Common errors and solutions:

- **Connection Error**: Check if MCP server is running on expected port
- **Parameter Error**: Verify parameter types match OpenAPI spec
- **Timeout Error**: Increase timeout or optimize operation
- **Permission Error**: Check file/database permissions

## Best Practices

1. Always validate parameters before tool execution
2. Use appropriate timeouts for long-running operations
3. Log tool usage to gitMaat for learning
4. Chain tools systematically for complex tasks
5. Handle errors gracefully with informative messages

## Related Tools

See `training/schemas/tool-relationships.json` for tool dependency information.

---
**Maat Alignment**: This documentation follows Maat principles of Truth, Balance, Order, Justice, and Self-Reflection.
