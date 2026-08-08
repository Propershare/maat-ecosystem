# secure-filesystem-server

**Maat-Aligned Tool Documentation**

## Overview

secure-filesystem-server MCP Server

**Version**: 0.2.0  
**Total Tools**: 14

## Maat Principles Alignment

### Truth (Maat)
Secure filesystem operations with access control

### Balance (Maat)
Balance file access with security

### Order (Maat)
Organized file operations

### Justice (Maat)
Respect file permissions and ownership

### Self-Reflection (Maat)
Learn from file operation patterns

## Available Tools

### Read File

**Operation ID**: `tool_read_file_post`  
**Path**: `POST /read_file`

Read the complete contents of a file as text. DEPRECATED: Use read_text_file instead.

**Request Body**: See OpenAPI spec for schema details

### Read Text File

**Operation ID**: `tool_read_text_file_post`  
**Path**: `POST /read_text_file`

Read the complete contents of a file from the file system as text. Handles various text encodings and provides detailed error messages if the file cannot be read. Use this tool when you need to examine the contents of a single file. Use the 'head' parameter to read only the first N lines of a file, or the 'tail' parameter to read only the last N lines of a file. Operates on the file as text regardless of extension. Only works within allowed directories.

**Request Body**: See OpenAPI spec for schema details

### Read Media File

**Operation ID**: `tool_read_media_file_post`  
**Path**: `POST /read_media_file`

Read an image or audio file. Returns the base64 encoded data and MIME type. Only works within allowed directories.

**Request Body**: See OpenAPI spec for schema details

### Read Multiple Files

**Operation ID**: `tool_read_multiple_files_post`  
**Path**: `POST /read_multiple_files`

Read the contents of multiple files simultaneously. This is more efficient than reading files one by one when you need to analyze or compare multiple files. Each file's content is returned with its path as a reference. Failed reads for individual files won't stop the entire operation. Only works within allowed directories.

**Request Body**: See OpenAPI spec for schema details

### Write File

**Operation ID**: `tool_write_file_post`  
**Path**: `POST /write_file`

Create a new file or completely overwrite an existing file with new content. Use with caution as it will overwrite existing files without warning. Handles text content with proper encoding. Only works within allowed directories.

**Request Body**: See OpenAPI spec for schema details

### Edit File

**Operation ID**: `tool_edit_file_post`  
**Path**: `POST /edit_file`

Make line-based edits to a text file. Each edit replaces exact line sequences with new content. Returns a git-style diff showing the changes made. Only works within allowed directories.

**Request Body**: See OpenAPI spec for schema details

### Create Directory

**Operation ID**: `tool_create_directory_post`  
**Path**: `POST /create_directory`

Create a new directory or ensure a directory exists. Can create multiple nested directories in one operation. If the directory already exists, this operation will succeed silently. Perfect for setting up directory structures for projects or ensuring required paths exist. Only works within allowed directories.

**Request Body**: See OpenAPI spec for schema details

### List Directory

**Operation ID**: `tool_list_directory_post`  
**Path**: `POST /list_directory`

Get a detailed listing of all files and directories in a specified path. Results clearly distinguish between files and directories with [FILE] and [DIR] prefixes. This tool is essential for understanding directory structure and finding specific files within a directory. Only works within allowed directories.

**Request Body**: See OpenAPI spec for schema details

### List Directory With Sizes

**Operation ID**: `tool_list_directory_with_sizes_post`  
**Path**: `POST /list_directory_with_sizes`

Get a detailed listing of all files and directories in a specified path, including sizes. Results clearly distinguish between files and directories with [FILE] and [DIR] prefixes. This tool is useful for understanding directory structure and finding specific files within a directory. Only works within allowed directories.

**Request Body**: See OpenAPI spec for schema details

### Directory Tree

**Operation ID**: `tool_directory_tree_post`  
**Path**: `POST /directory_tree`

Get a recursive tree view of files and directories as a JSON structure. Each entry includes 'name', 'type' (file/directory), and 'children' for directories. Files have no children array, while directories always have a children array (which may be empty). The output is formatted with 2-space indentation for readability. Only works within allowed directories.

**Request Body**: See OpenAPI spec for schema details

### Move File

**Operation ID**: `tool_move_file_post`  
**Path**: `POST /move_file`

Move or rename files and directories. Can move files between directories and rename them in a single operation. If the destination exists, the operation will fail. Works across different directories and can be used for simple renaming within the same directory. Both source and destination must be within allowed directories.

**Request Body**: See OpenAPI spec for schema details

### Search Files

**Operation ID**: `tool_search_files_post`  
**Path**: `POST /search_files`

Recursively search for files and directories matching a pattern. The patterns should be glob-style patterns that match paths relative to the working directory. Use pattern like '*.ext' to match files in current directory, and '**/*.ext' to match files in all subdirectories. Returns full paths to all matching items. Great for finding files when you don't know their exact location. Only searches within allowed directories.

**Request Body**: See OpenAPI spec for schema details

### Get File Info

**Operation ID**: `tool_get_file_info_post`  
**Path**: `POST /get_file_info`

Retrieve detailed metadata about a file or directory. Returns comprehensive information including size, creation time, last modified time, permissions, and type. This tool is perfect for understanding file characteristics without reading the actual content. Only works within allowed directories.

**Request Body**: See OpenAPI spec for schema details

### List Allowed Directories

**Operation ID**: `tool_list_allowed_directories_post`  
**Path**: `POST /list_allowed_directories`

Returns the list of directories that this server is allowed to access. Subdirectories within these allowed directories are also accessible. Use this to understand which directories and their nested paths are available before trying to access files.

## Use Cases

- Read/write files securely
- List directories
- Get file metadata
- Search files

## Common Patterns

- List → Read → Process → Write

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
