# Tehuti-Research

**Maat-Aligned Tool Documentation**

## Overview

Tehuti-Research MCP Server

**Version**: 1.0  
**Total Tools**: 3

## Maat Principles Alignment

### Truth (Maat)
Research methodologies and analysis tools

### Balance (Maat)
Balance exploration with systematic methodology

### Order (Maat)
Structured research workflows

### Justice (Maat)
Proper citation and attribution

### Self-Reflection (Maat)
Learn from research patterns

## Available Tools

### Tehuti-Research/List-Methodologies

**Operation ID**: `tool_tehuti_research_list_methodologies_post`  
**Path**: `POST /tehuti-research/list-methodologies`

List available research methodologies

### Tehuti-Research/Get-Methodology

**Operation ID**: `tool_tehuti_research_get_methodology_post`  
**Path**: `POST /tehuti-research/get-methodology`

Get a methodology by id

**Request Body**: See OpenAPI spec for schema details

### Tehuti-Research/Get-Analysis-Tool

**Operation ID**: `tool_tehuti_research_get_analysis_tool_post`  
**Path**: `POST /tehuti-research/get-analysis-tool`

Get an analysis tool by type and id

**Request Body**: See OpenAPI spec for schema details

## Use Cases

- Research methodologies
- Analysis tools

## Common Patterns

- Methodology → Analysis → Results

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
