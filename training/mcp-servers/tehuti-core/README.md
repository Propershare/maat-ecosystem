# Tehuti Core

**Maat-Aligned Tool Documentation**

## Overview

Tehuti Core MCP Server

**Version**: 1.25.0  
**Total Tools**: 6

**CRITICAL**: This MCP server must be enabled in the client (OpenClaw primary on all machines; Open WebUI still in use) for the model to query gitMaat. The `tool_query_gitmaat_post` tool is essential for "QUERY gitMaat FIRST". In OpenClaw ensure Tehuti Core/gitMaat tools are enabled for the agent; in Open WebUI: Chat Settings → External Tools → Enable "Tehuti Core" (or `server:openapi:tehuti-core`).

## Maat Principles Alignment

### Truth (Maat)
Core system operations - terminal, code execution, file operations, gitMaat queries

### Balance (Maat)
Use for system-level operations. Balance security (sandboxed execution) with functionality

### Order (Maat)
Foundation layer - used by other tools. Execute commands, run Python, query gitMaat

### Justice (Maat)
Proper attribution to MaatCode powers. Respects workspace boundaries

### Self-Reflection (Maat)
Logs all operations to gitMaat. Learn from execution patterns

## Available Tools

### Execute Command

**Operation ID**: `tool_execute_command_post`  
**Path**: `POST /execute_command`

Execute a shell command in the terminal (MaatCode power).
    
    Args:
        command: The command to execute
        working_directory: Directory to run command in (default: workspace root)
        timeout: Command timeout in seconds (default: 30)
        shell: Use shell execution (default: True)
    
    Returns:
        Command output (stdout + stderr)

**Request Body**: See OpenAPI spec for schema details

### Run Python Code

**Operation ID**: `tool_run_python_code_post`  
**Path**: `POST /run_python_code`

Execute Python code in a safe context (MaatCode power).
    
    Args:
        code: Python code to execute
        working_directory: Directory to run code in (default: workspace root)
    
    Returns:
        Code execution output

**Request Body**: See OpenAPI spec for schema details

### Get System Info

**Operation ID**: `tool_get_system_info_post`  
**Path**: `POST /get_system_info`

Get system information (OS, Python version, workspace info).
    
    Returns:
        System information as formatted text

### List Directory

**Operation ID**: `tool_list_directory_post`  
**Path**: `POST /list_directory`

List directory contents.
    
    Args:
        path: Directory path (default: workspace root)
        show_hidden: Show hidden files (default: False)
    
    Returns:
        Directory listing

**Request Body**: See OpenAPI spec for schema details

### Read File

**Operation ID**: `tool_read_file_post`  
**Path**: `POST /read_file`

Read a file (with line limit for safety).
    
    Args:
        file_path: Path to file
        max_lines: Maximum lines to read (default: 1000)
    
    Returns:
        File contents

**Request Body**: See OpenAPI spec for schema details

### Query Gitmaat

**Operation ID**: `tool_query_gitmaat_post`  
**Path**: `POST /query_gitmaat`

Query gitMaat (Maat Memory) for tasks, changes, or learnings.
    
    Args:
        query_type: Type of query (tasks, changes, learnings, decisions)
        status: Filter by status (for tasks: pending, in_progress, completed)
        limit: Maximum results (default: 10)
    
    Returns:
        Query results as JSON

**Request Body**: See OpenAPI spec for schema details

## Use Cases

- Execute shell commands safely
- Run Python code in isolated context
- Query gitMaat for tasks, changes, learnings
- List directories and read files
- Get system information

## Common Patterns

- Command execution → Result processing
- Python code → Data transformation
- gitMaat query → Task coordination

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
