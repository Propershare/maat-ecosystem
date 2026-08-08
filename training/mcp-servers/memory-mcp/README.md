# memory-server

**Maat-Aligned Tool Documentation**

## Overview

memory-server MCP Server

**Version**: 0.6.3  
**Total Tools**: 9

## Maat Principles Alignment

### Truth (Maat)
Memory management and retrieval

### Balance (Maat)
Balance memory storage with retrieval efficiency

### Order (Maat)
Organized memory structure

### Justice (Maat)
Proper memory attribution

### Self-Reflection (Maat)
Learn from memory patterns

## Available Tools

### Create Entities

**Operation ID**: `tool_create_entities_post`  
**Path**: `POST /create_entities`

Create multiple new entities in the knowledge graph

**Request Body**: See OpenAPI spec for schema details

### Create Relations

**Operation ID**: `tool_create_relations_post`  
**Path**: `POST /create_relations`

Create multiple new relations between entities in the knowledge graph. Relations should be in active voice

**Request Body**: See OpenAPI spec for schema details

### Add Observations

**Operation ID**: `tool_add_observations_post`  
**Path**: `POST /add_observations`

Add new observations to existing entities in the knowledge graph

**Request Body**: See OpenAPI spec for schema details

### Delete Entities

**Operation ID**: `tool_delete_entities_post`  
**Path**: `POST /delete_entities`

Delete multiple entities and their associated relations from the knowledge graph

**Request Body**: See OpenAPI spec for schema details

### Delete Observations

**Operation ID**: `tool_delete_observations_post`  
**Path**: `POST /delete_observations`

Delete specific observations from entities in the knowledge graph

**Request Body**: See OpenAPI spec for schema details

### Delete Relations

**Operation ID**: `tool_delete_relations_post`  
**Path**: `POST /delete_relations`

Delete multiple relations from the knowledge graph

**Request Body**: See OpenAPI spec for schema details

### Read Graph

**Operation ID**: `tool_read_graph_post`  
**Path**: `POST /read_graph`

Read the entire knowledge graph

### Search Nodes

**Operation ID**: `tool_search_nodes_post`  
**Path**: `POST /search_nodes`

Search for nodes in the knowledge graph based on a query

**Request Body**: See OpenAPI spec for schema details

### Open Nodes

**Operation ID**: `tool_open_nodes_post`  
**Path**: `POST /open_nodes`

Open specific nodes in the knowledge graph by their names

**Request Body**: See OpenAPI spec for schema details

## Use Cases

- Store memories
- Retrieve memories
- Search memories

## Common Patterns

- Store → Retrieve → Use

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
