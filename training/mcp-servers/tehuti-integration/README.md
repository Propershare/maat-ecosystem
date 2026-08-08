# Tehuti-Integration

**Maat-Aligned Tool Documentation**

## Overview

Tehuti-Integration MCP Server

**Version**: 1.0  
**Total Tools**: 4

## Maat Principles Alignment

### Truth (Maat)
Integration with n8n, filesystem, databases

### Balance (Maat)
Balance automation with control

### Order (Maat)
Orchestrated workflow execution

### Justice (Maat)
Proper workflow attribution

### Self-Reflection (Maat)
Learn from integration patterns

## Available Tools

### Tehuti-Integration/List-Workflows

**Operation ID**: `tool_tehuti_integration_list_workflows_post`  
**Path**: `POST /tehuti-integration/list-workflows`

List available workflows

### Tehuti-Integration/Get-Workflow

**Operation ID**: `tool_tehuti_integration_get_workflow_post`  
**Path**: `POST /tehuti-integration/get-workflow`

Get workflow metadata by id

**Request Body**: See OpenAPI spec for schema details

### Tehuti-Integration/Trigger-Workflow

**Operation ID**: `tool_tehuti_integration_trigger_workflow_post`  
**Path**: `POST /tehuti-integration/trigger-workflow`

Trigger a workflow with parameters

**Request Body**: See OpenAPI spec for schema details

### Tehuti-Integration/Get-Execution

**Operation ID**: `tool_tehuti_integration_get_execution_post`  
**Path**: `POST /tehuti-integration/get-execution`

Get a workflow execution status/result

**Request Body**: See OpenAPI spec for schema details

## Use Cases

- n8n workflow management
- File operations
- Database queries

## Common Patterns

- List → Get → Execute

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
