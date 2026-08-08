# Tehuti-Curriculum

**Maat-Aligned Tool Documentation**

## Overview

Tehuti-Curriculum MCP Server

**Version**: 1.0  
**Total Tools**: 3

## Maat Principles Alignment

### Truth (Maat)
Curriculum and learning path management

### Balance (Maat)
Balance structured learning with flexibility

### Order (Maat)
Organized curriculum structure

### Justice (Maat)
Proper attribution of learning resources

### Self-Reflection (Maat)
Track learning progress and adapt

## Available Tools

### Tehuti-Curriculum/Generate-Curriculum

**Operation ID**: `tool_tehuti_curriculum_generate_curriculum_post`  
**Path**: `POST /tehuti-curriculum/generate-curriculum`

Generate a curriculum based on learning objectives, target audience, and duration

**Request Body**: See OpenAPI spec for schema details

### Tehuti-Curriculum/List-Templates

**Operation ID**: `tool_tehuti_curriculum_list_templates_post`  
**Path**: `POST /tehuti-curriculum/list-templates`

List available curriculum templates

### Tehuti-Curriculum/Get-Template

**Operation ID**: `tool_tehuti_curriculum_get_template_post`  
**Path**: `POST /tehuti-curriculum/get-template`

Get a curriculum template by ID

**Request Body**: See OpenAPI spec for schema details

## Use Cases

- Manage curriculum
- Track learning paths

## Common Patterns

- List → Get → Apply

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
