#!/usr/bin/env python3
"""
Tehuti Core MCP Server - MaatCode Powers
Provides terminal execution, code running, and system management capabilities
"""

import asyncio
import subprocess
import sys
import os
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from mcp.server.fastmcp import FastMCP

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("tehuti_core.log"),
        logging.StreamHandler(sys.stderr),
    ],
)
logger = logging.getLogger("tehuti_core")

# Initialize FastMCP server
mcp = FastMCP("Tehuti Core")

# Workspace root detection
WORKSPACE_ROOT = None
for path in [Path.cwd()] + list(Path.cwd().parents):
    if (path / "maatlangchain").exists() or (path / ".cursorrules").exists():
        WORKSPACE_ROOT = path
        break

if not WORKSPACE_ROOT:
    WORKSPACE_ROOT = Path.home() / ".n8n"

logger.info(f"Workspace root: {WORKSPACE_ROOT}")

# Load database URL from environment (for gitMaat)
# Check same locations as maat_memory/__init__.py so MCP and agents see the same config
PGVECTOR_DB_URL = os.getenv("PGVECTOR_DB_URL")
if not PGVECTOR_DB_URL:
    for env_file in [
        WORKSPACE_ROOT / ".env",
        WORKSPACE_ROOT / "maatlangchain" / ".env",
        WORKSPACE_ROOT / "tehuti-lab-webui" / ".env",
        WORKSPACE_ROOT / "open-webui" / ".env",
    ]:
        if env_file.exists():
            try:
                with open(env_file) as f:
                    for line in f:
                        if line.startswith("PGVECTOR_DB_URL="):
                            PGVECTOR_DB_URL = line.split("=", 1)[1].strip().strip('"').strip("'")
                            break
                if PGVECTOR_DB_URL:
                    break
            except Exception:
                pass

if PGVECTOR_DB_URL:
    os.environ["PGVECTOR_DB_URL"] = PGVECTOR_DB_URL
    logger.info("✅ Database URL loaded from environment")
else:
    logger.warning("⚠️  PGVECTOR_DB_URL not found - gitMaat queries will fail")


@mcp.tool()
async def execute_command(
    command: str,
    working_directory: Optional[str] = None,
    timeout: int = 30,
    shell: bool = True
) -> str:
    """
    Execute a shell command in the terminal (MaatCode power).
    
    Args:
        command: The command to execute
        working_directory: Directory to run command in (default: workspace root)
        timeout: Command timeout in seconds (default: 30)
        shell: Use shell execution (default: True)
    
    Returns:
        Command output (stdout + stderr)
    """
    try:
        # Set working directory
        cwd = Path(working_directory) if working_directory else WORKSPACE_ROOT
        cwd = cwd.resolve()
        
        # Security: Prevent dangerous commands
        dangerous_commands = ["rm -rf /", "format", "mkfs", "dd if="]
        if any(danger in command.lower() for danger in dangerous_commands):
            return f"❌ Blocked potentially dangerous command: {command}"
        
        logger.info(f"Executing: {command} in {cwd}")
        
        # Execute command
        process = await asyncio.create_subprocess_shell(
            command,
            cwd=str(cwd),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            shell=shell
        )
        
        try:
            stdout, _ = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout
            )
            output = stdout.decode('utf-8', errors='replace')
            return_code = process.returncode
            
            result = f"Exit code: {return_code}\n\n{output}"
            if return_code != 0:
                result = f"⚠️ Command failed (exit {return_code})\n\n{result}"
            
            return result
            
        except asyncio.TimeoutError:
            process.kill()
            await process.wait()
            return f"⏱️ Command timed out after {timeout} seconds"
            
    except Exception as e:
        logger.exception(f"Error executing command: {e}")
        return f"❌ Error: {str(e)}"


@mcp.tool()
async def run_python_code(
    code: str,
    working_directory: Optional[str] = None
) -> str:
    """
    Execute Python code in a safe context (MaatCode power).
    
    Args:
        code: Python code to execute
        working_directory: Directory to run code in (default: workspace root)
    
    Returns:
        Code execution output
    """
    try:
        cwd = Path(working_directory) if working_directory else WORKSPACE_ROOT
        cwd = cwd.resolve()
        
        # Create temporary Python file
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, dir=cwd) as f:
            f.write(code)
            temp_file = f.name
        
        try:
            # Execute Python file
            result = await execute_command(
                f"python3 {temp_file}",
                working_directory=str(cwd),
                timeout=60
            )
            return result
        finally:
            # Clean up temp file
            try:
                os.unlink(temp_file)
            except:
                pass
                
    except Exception as e:
        logger.exception(f"Error running Python code: {e}")
        return f"❌ Error: {str(e)}"


@mcp.tool()
async def get_system_info() -> str:
    """
    Get system information (OS, Python version, workspace info).
    
    Returns:
        System information as formatted text
    """
    try:
        import platform
        
        info = {
            "OS": platform.system(),
            "OS Version": platform.release(),
            "Python Version": sys.version,
            "Workspace Root": str(WORKSPACE_ROOT),
            "Current Directory": str(Path.cwd()),
        }
        
        # Add gitMaat info if available
        try:
            sys.path.insert(0, str(WORKSPACE_ROOT / "maatlangchain"))
            from maat_memory import MaatMemory
            if PGVECTOR_DB_URL:
                memory = MaatMemory()
                info["gitMaat"] = "Available (connected)"
            else:
                info["gitMaat"] = "Available (no DB URL)"
        except Exception as e:
            info["gitMaat"] = f"Not available: {str(e)[:50]}"
        
        return json.dumps(info, indent=2)
        
    except Exception as e:
        logger.exception(f"Error getting system info: {e}")
        return f"❌ Error: {str(e)}"


@mcp.tool()
async def list_directory(
    path: Optional[str] = None,
    show_hidden: bool = False
) -> str:
    """
    Get a detailed listing of all files and directories in a specified path. Results clearly distinguish between files and directories with [FILE] and [DIR] prefixes. This tool is essential for understanding directory structure and finding specific files within a directory. Only works within allowed directories.
    
    Args:
        path: Directory path (default: workspace root)
        show_hidden: Show hidden files (default: False)
    
    Returns:
        Directory listing with [FILE] and [DIR] prefixes
    """
    try:
        target = Path(path) if path else WORKSPACE_ROOT
        target = target.resolve()
        
        # Security: Prevent access outside workspace
        if not str(target).startswith(str(WORKSPACE_ROOT)):
            return f"❌ Access denied: Path outside workspace"
        
        if not target.exists():
            return f"❌ Path does not exist: {target}"
        
        if not target.is_dir():
            return f"❌ Not a directory: {target}"
        
        items = []
        for item in target.iterdir():
            if not show_hidden and item.name.startswith('.'):
                continue
            
            item_type = "[DIR]" if item.is_dir() else "[FILE]"
            items.append(f"{item_type} {item.name}")
        
        return "\n".join(sorted(items)) if items else "Directory is empty"
        
    except Exception as e:
        logger.exception(f"Error listing directory: {e}")
        return f"❌ Error: {str(e)}"


@mcp.tool()
async def read_file(
    file_path: str,
    max_lines: Optional[int] = None
) -> str:
    """
    Read a file (with line limit for safety).
    
    Args:
        file_path: Path to file
        max_lines: Maximum lines to read (default: 1000)
    
    Returns:
        File contents
    """
    try:
        file = Path(file_path).resolve()
        
        # Security: Prevent reading outside workspace
        if not str(file).startswith(str(WORKSPACE_ROOT)):
            return f"❌ Access denied: File outside workspace"
        
        if not file.exists():
            return f"❌ File does not exist: {file}"
        
        if not file.is_file():
            return f"❌ Not a file: {file}"
        
        max_lines = max_lines or 1000
        lines = []
        with open(file, 'r', encoding='utf-8', errors='replace') as f:
            for i, line in enumerate(f):
                if i >= max_lines:
                    lines.append(f"\n... (truncated, showing first {max_lines} lines)")
                    break
                lines.append(line.rstrip())
        
        return "\n".join(lines)
        
    except Exception as e:
        logger.exception(f"Error reading file: {e}")
        return f"❌ Error: {str(e)}"


@mcp.tool()
async def query_gitmaat(
    query_type: str = "tasks",
    status: Optional[str] = None,
    limit: int = 10
) -> str:
    """
    Query gitMaat (Maat Memory) for tasks, changes, or learnings.
    
    Args:
        query_type: Type of query (tasks, changes, learnings, decisions)
        status: Filter by status (for tasks: pending, in_progress, completed)
        limit: Maximum results (default: 10)
    
    Returns:
        Query results as JSON
    """
    try:
        if not PGVECTOR_DB_URL:
            return "❌ Database URL not configured. Set PGVECTOR_DB_URL environment variable."
        
        sys.path.insert(0, str(WORKSPACE_ROOT / "maatlangchain"))
        try:
            from maat_memory import MaatMemory, get_unique_agent_id
        except ImportError as e:
            if "psycopg2" in str(e):
                return "❌ psycopg2 not installed. Install with: pip install psycopg2-binary\n\nNote: When running in WebUI context, this should be available in the venv."
            raise
        
        memory = MaatMemory()
        agent_id = get_unique_agent_id("tehuti_core")
        
        if query_type == "tasks":
            results = memory.get_tasks(status=status, limit=limit)
        elif query_type == "changes":
            results = memory.get_recent_changes(limit=limit)
        elif query_type == "learnings":
            results = memory.get_learnings(limit=limit)
        elif query_type == "decisions":
            results = memory.get_decisions(limit=limit)
        else:
            return f"❌ Unknown query type: {query_type}. Use: tasks, changes, learnings, or decisions"
        
        if not results:
            return f"ℹ️  No {query_type} found"
        
        return json.dumps(results, indent=2, default=str)
        
    except Exception as e:
        logger.exception(f"Error querying gitMaat: {e}")
        return f"❌ Error querying gitMaat: {str(e)}\n\nMake sure PGVECTOR_DB_URL is set and PostgreSQL is accessible."


def _gitmaat_memory():
    """Shared MaatMemory init for write tools."""
    if not PGVECTOR_DB_URL:
        raise RuntimeError("PGVECTOR_DB_URL not configured")
    sys.path.insert(0, str(WORKSPACE_ROOT / "maatlangchain"))
    from maat_memory import MaatMemory, get_unique_agent_id

    return MaatMemory(), get_unique_agent_id("opencode")


@mcp.tool()
async def log_gitmaat_task(
    title: str,
    description: str,
    status: str = "pending",
    priority: str = "medium",
    related_files_json: Optional[str] = None,
) -> str:
    """
    Log a task to gitMaat (Maat Memory / PostgreSQL). Use after creating actionable work.

    Args:
        title: Short task title
        description: Details and acceptance hints
        status: pending | in_progress | completed (default pending)
        priority: low | medium | high
        related_files_json: Optional JSON array of file paths, e.g. '["src/foo.py"]'
    """
    try:
        memory, agent_id = _gitmaat_memory()
        related = None
        if related_files_json:
            related = json.loads(related_files_json)
            if not isinstance(related, list):
                return "❌ related_files_json must be a JSON array of strings"
        task_id = memory.log_task(
            agent_id,
            title,
            description,
            status=status,
            priority=priority,
            related_files=related,
        )
        return json.dumps({"ok": True, "task_id": task_id, "agent": agent_id}, indent=2)
    except Exception as e:
        logger.exception(f"log_gitmaat_task: {e}")
        return f"❌ {e}"


@mcp.tool()
async def log_gitmaat_change(
    file_path: str,
    change_type: str,
    summary: str,
    reason: str,
    diff_preview: Optional[str] = None,
) -> str:
    """
    Record a file change in gitMaat (create | update | delete | refactor, etc.).

    Args:
        file_path: Repo-relative or absolute path under workspace
        change_type: e.g. create, update, delete, refactor
        summary: One-line summary
        reason: Why the change was made
        diff_preview: Optional short diff or excerpt
    """
    try:
        memory, agent_id = _gitmaat_memory()
        cid = memory.log_change(
            agent_id,
            file_path,
            change_type,
            summary,
            reason,
            diff_preview=diff_preview,
        )
        return json.dumps({"ok": True, "change_id": cid, "agent": agent_id}, indent=2)
    except Exception as e:
        logger.exception(f"log_gitmaat_change: {e}")
        return f"❌ {e}"


@mcp.tool()
async def log_gitmaat_decision(
    context: str,
    decision_made: str,
    rationale: str,
    options_considered_json: Optional[str] = None,
) -> str:
    """
    Log an architectural or process decision to gitMaat.

    Args:
        context: What was being decided
        decision_made: The choice
        rationale: Why
        options_considered_json: Optional JSON array of strings
    """
    try:
        memory, agent_id = _gitmaat_memory()
        opts = None
        if options_considered_json:
            opts = json.loads(options_considered_json)
            if not isinstance(opts, list):
                return "❌ options_considered_json must be a JSON array"
        did = memory.log_decision(
            agent_id,
            context,
            decision_made,
            rationale,
            options_considered=opts,
        )
        return json.dumps({"ok": True, "decision_id": did, "agent": agent_id}, indent=2)
    except Exception as e:
        logger.exception(f"log_gitmaat_decision: {e}")
        return f"❌ {e}"


@mcp.tool()
async def log_gitmaat_learning(
    topic: str,
    insight: str,
    source: str,
    confidence: float = 0.7,
) -> str:
    """
    Log a learning or Sankofa-style insight to gitMaat.

    Args:
        topic: Short label
        insight: What to remember
        source: Where it came from (session, doc, failure, etc.)
        confidence: 0.0–1.0
    """
    try:
        memory, agent_id = _gitmaat_memory()
        lid = memory.log_learning(
            agent_id,
            topic,
            insight,
            source,
            confidence=confidence,
        )
        return json.dumps({"ok": True, "learning_id": lid, "agent": agent_id}, indent=2)
    except Exception as e:
        logger.exception(f"log_gitmaat_learning: {e}")
        return f"❌ {e}"


@mcp.tool()
async def write_file(
    path: str,
    content: str
) -> str:
    """
    Create a new file or completely overwrite an existing file with new content. Use with caution as it will overwrite existing files without warning. Handles text content with proper encoding. Only works within allowed directories.
    
    Args:
        path: File path to write
        content: Content to write to the file
    
    Returns:
        Success message
    """
    try:
        file = Path(path).resolve()
        
        # Security: Prevent writing outside workspace
        if not str(file).startswith(str(WORKSPACE_ROOT)):
            return f"❌ Access denied: Path outside workspace"
        
        # Create parent directories if needed
        file.parent.mkdir(parents=True, exist_ok=True)
        
        # Write file with UTF-8 encoding
        file.write_text(content, encoding='utf-8')
        
        return f"✅ File written successfully: {file}"
        
    except Exception as e:
        logger.exception(f"Error writing file: {e}")
        return f"❌ Error: {str(e)}"


@mcp.tool()
async def edit_file(
    path: str,
    edits: List[Dict[str, str]],
    dry_run: bool = False
) -> str:
    """
    Make line-based edits to a text file. Each edit replaces exact line sequences with new content. Returns a git-style diff showing the changes made. Only works within allowed directories.
    
    Args:
        path: File path to edit
        edits: List of edit objects with 'oldText' and 'newText' keys
        dry_run: Preview changes using git-style diff format (default: False)
    
    Returns:
        Git-style diff of changes made
    """
    try:
        file = Path(path).resolve()
        
        # Security: Prevent editing outside workspace
        if not str(file).startswith(str(WORKSPACE_ROOT)):
            return f"❌ Access denied: Path outside workspace"
        
        if not file.exists():
            return f"❌ File does not exist: {file}"
        
        if not file.is_file():
            return f"❌ Not a file: {file}"
        
        # Read current content
        current_content = file.read_text(encoding='utf-8')
        new_content = current_content
        diffs = []
        
        # Apply each edit
        for edit in edits:
            old_text = edit.get('oldText', '')
            new_text = edit.get('newText', '')
            
            if old_text not in new_content:
                return f"❌ Edit failed: 'oldText' not found in file\n\nLooking for:\n{old_text[:200]}"
            
            # Create diff
            old_lines = old_text.split('\n')
            new_lines = new_text.split('\n')
            
            # Find line numbers
            content_lines = current_content.split('\n')
            for i, line in enumerate(content_lines):
                if old_text in '\n'.join(content_lines[i:i+len(old_lines)]):
                    line_num = i + 1
                    diffs.append(f"@@ -{line_num},{len(old_lines)} +{line_num},{len(new_lines)} @@")
                    for old_line in old_lines:
                        diffs.append(f"-{old_line}")
                    for new_line in new_lines:
                        diffs.append(f"+{new_line}")
                    break
            
            # Apply edit
            new_content = new_content.replace(old_text, new_text, 1)
        
        if dry_run:
            return f"Preview of changes (dry run):\n\n" + "\n".join(diffs)
        
        # Write changes
        file.write_text(new_content, encoding='utf-8')
        
        return f"✅ File edited successfully:\n\n" + "\n".join(diffs)
        
    except Exception as e:
        logger.exception(f"Error editing file: {e}")
        return f"❌ Error: {str(e)}"


@mcp.tool()
async def create_directory(
    path: str
) -> str:
    """
    Create a new directory or ensure a directory exists. Can create multiple nested directories in one operation. If the directory already exists, this operation will succeed silently. Perfect for setting up directory structures for projects or ensuring required paths exist. Only works within allowed directories.
    
    Args:
        path: Directory path to create
    
    Returns:
        Success message
    """
    try:
        dir_path = Path(path).resolve()
        
        # Security: Prevent creating outside workspace
        if not str(dir_path).startswith(str(WORKSPACE_ROOT)):
            return f"❌ Access denied: Path outside workspace"
        
        # Create directory (and parents if needed)
        dir_path.mkdir(parents=True, exist_ok=True)
        
        return f"✅ Directory created (or already exists): {dir_path}"
        
    except Exception as e:
        logger.exception(f"Error creating directory: {e}")
        return f"❌ Error: {str(e)}"


@mcp.tool()
async def read_text_file(
    path: str,
    head: Optional[int] = None,
    tail: Optional[int] = None
) -> str:
    """
    Read the complete contents of a file from the file system as text. Handles various text encodings and provides detailed error messages if the file cannot be read. Use this tool when you need to examine the contents of a single file. Use the 'head' parameter to read only the first N lines of a file, or the 'tail' parameter to read only the last N lines of a file. Operates on the file as text regardless of extension. Only works within allowed directories.
    
    Args:
        path: File path to read
        head: Read only the first N lines (optional)
        tail: Read only the last N lines (optional)
    
    Returns:
        File contents
    """
    try:
        file = Path(path).resolve()
        
        # Security: Prevent reading outside workspace
        if not str(file).startswith(str(WORKSPACE_ROOT)):
            return f"❌ Access denied: Path outside workspace"
        
        if not file.exists():
            return f"❌ File does not exist: {file}"
        
        if not file.is_file():
            return f"❌ Not a file: {file}"
        
        # Try different encodings
        encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
        content = None
        
        for encoding in encodings:
            try:
                content = file.read_text(encoding=encoding)
                break
            except UnicodeDecodeError:
                continue
        
        if content is None:
            return f"❌ Could not decode file with any supported encoding"
        
        # Handle head/tail
        lines = content.split('\n')
        
        if head is not None:
            lines = lines[:head]
        elif tail is not None:
            lines = lines[-tail:]
        
        return '\n'.join(lines)
        
    except Exception as e:
        logger.exception(f"Error reading text file: {e}")
        return f"❌ Error: {str(e)}"


@mcp.tool()
async def read_media_file(
    path: str
) -> str:
    """
    Read an image or audio file. Returns the base64 encoded data and MIME type. Only works within allowed directories.
    
    Args:
        path: File path to read
    
    Returns:
        JSON with base64 data and MIME type
    """
    try:
        import base64
        import mimetypes
        
        file = Path(path).resolve()
        
        # Security: Prevent reading outside workspace
        if not str(file).startswith(str(WORKSPACE_ROOT)):
            return f"❌ Access denied: Path outside workspace"
        
        if not file.exists():
            return f"❌ File does not exist: {file}"
        
        if not file.is_file():
            return f"❌ Not a file: {file}"
        
        # Read file as binary
        file_data = file.read_bytes()
        
        # Encode to base64
        base64_data = base64.b64encode(file_data).decode('utf-8')
        
        # Detect MIME type
        mime_type, _ = mimetypes.guess_type(str(file))
        if not mime_type:
            # Fallback based on extension
            ext = file.suffix.lower()
            mime_map = {
                '.png': 'image/png',
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.gif': 'image/gif',
                '.webp': 'image/webp',
                '.mp3': 'audio/mpeg',
                '.wav': 'audio/wav',
                '.ogg': 'audio/ogg',
            }
            mime_type = mime_map.get(ext, 'application/octet-stream')
        
        result = {
            "type": "image" if mime_type.startswith("image/") else "audio" if mime_type.startswith("audio/") else "unknown",
            "data": base64_data,
            "mimeType": mime_type
        }
        
        return json.dumps([result], indent=2)
        
    except Exception as e:
        logger.exception(f"Error reading media file: {e}")
        return f"❌ Error: {str(e)}"


@mcp.tool()
async def read_multiple_files(
    paths: List[str]
) -> str:
    """
    Read the contents of multiple files simultaneously. This is more efficient than reading files one by one when you need to analyze or compare multiple files. Each file's content is returned with its path as a reference. Failed reads for individual files won't stop the entire operation. Only works within allowed directories.
    
    Args:
        paths: Array of file paths to read
    
    Returns:
        JSON with file paths and contents
    """
    try:
        results = []
        
        for path in paths:
            file = Path(path).resolve()
            
            # Security: Prevent reading outside workspace
            if not str(file).startswith(str(WORKSPACE_ROOT)):
                results.append({
                    "path": path,
                    "content": f"❌ Access denied: Path outside workspace",
                    "error": True
                })
                continue
            
            if not file.exists():
                results.append({
                    "path": path,
                    "content": f"❌ File does not exist",
                    "error": True
                })
                continue
            
            if not file.is_file():
                results.append({
                    "path": path,
                    "content": f"❌ Not a file",
                    "error": True
                })
                continue
            
            try:
                # Try UTF-8 first, fallback to latin-1
                try:
                    content = file.read_text(encoding='utf-8')
                except UnicodeDecodeError:
                    content = file.read_text(encoding='latin-1')
                
                results.append({
                    "path": path,
                    "content": content,
                    "error": False
                })
            except Exception as e:
                results.append({
                    "path": path,
                    "content": f"❌ Error reading file: {str(e)}",
                    "error": True
                })
        
        # Format output similar to filesystem-mcp
        output_lines = []
        for result in results:
            output_lines.append(f"File: {result['path']}")
            if result.get('error'):
                output_lines.append(f"Error: {result['content']}")
            else:
                output_lines.append(f"Content:\n{result['content']}")
            output_lines.append("")
        
        return "\n".join(output_lines)
        
    except Exception as e:
        logger.exception(f"Error reading multiple files: {e}")
        return f"❌ Error: {str(e)}"


@mcp.tool()
async def list_directory_with_sizes(
    path: Optional[str] = None,
    sort_by: str = "name"
) -> str:
    """
    Get a detailed listing of all files and directories in a specified path, including sizes. Results clearly distinguish between files and directories with [FILE] and [DIR] prefixes. This tool is useful for understanding directory structure and finding specific files within a directory. Only works within allowed directories.
    
    Args:
        path: Directory path (default: workspace root)
        sort_by: Sort entries by 'name' or 'size' (default: 'name')
    
    Returns:
        Directory listing with sizes
    """
    try:
        target = Path(path) if path else WORKSPACE_ROOT
        target = target.resolve()
        
        # Security: Prevent access outside workspace
        if not str(target).startswith(str(WORKSPACE_ROOT)):
            return f"❌ Access denied: Path outside workspace"
        
        if not target.exists():
            return f"❌ Path does not exist: {target}"
        
        if not target.is_dir():
            return f"❌ Not a directory: {target}"
        
        items = []
        for item in target.iterdir():
            item_type = "[DIR]" if item.is_dir() else "[FILE]"
            
            if item.is_file():
                try:
                    size = item.stat().st_size
                    size_str = f"{size} bytes"
                    if size > 1024:
                        size_str = f"{size / 1024:.2f} KB"
                    if size > 1024 * 1024:
                        size_str = f"{size / (1024 * 1024):.2f} MB"
                    items.append((item_type, item.name, size))
                except:
                    items.append((item_type, item.name, 0))
            else:
                items.append((item_type, item.name, 0))
        
        # Sort
        if sort_by == "size":
            items.sort(key=lambda x: (x[2], x[1]), reverse=True)
        else:
            items.sort(key=lambda x: x[1])
        
        # Format output
        output_lines = []
        for item_type, name, size in items:
            if size > 0:
                size_str = f"{size} bytes"
                if size > 1024:
                    size_str = f"{size / 1024:.2f} KB"
                if size > 1024 * 1024:
                    size_str = f"{size / (1024 * 1024):.2f} MB"
                output_lines.append(f"{item_type} {name} ({size_str})")
            else:
                output_lines.append(f"{item_type} {name}")
        
        return "\n".join(output_lines) if output_lines else "Directory is empty"
        
    except Exception as e:
        logger.exception(f"Error listing directory with sizes: {e}")
        return f"❌ Error: {str(e)}"


@mcp.tool()
async def directory_tree(
    path: Optional[str] = None,
    exclude_patterns: Optional[List[str]] = None
) -> str:
    """
    Get a recursive tree view of files and directories as a JSON structure. Each entry includes 'name', 'type' (file/directory), and 'children' for directories. Files have no children array, while directories always have a children array (which may be empty). The output is formatted with 2-space indentation for readability. Only works within allowed directories.
    
    Args:
        path: Directory path (default: workspace root)
        exclude_patterns: List of glob patterns to exclude (optional)
    
    Returns:
        JSON tree structure
    """
    try:
        from fnmatch import fnmatch
        
        target = Path(path) if path else WORKSPACE_ROOT
        target = target.resolve()
        
        # Security: Prevent access outside workspace
        if not str(target).startswith(str(WORKSPACE_ROOT)):
            return f"❌ Access denied: Path outside workspace"
        
        if not target.exists():
            return f"❌ Path does not exist: {target}"
        
        if not target.is_dir():
            return f"❌ Not a directory: {target}"
        
        exclude_patterns = exclude_patterns or []
        
        def build_tree(p: Path) -> Dict:
            """Recursively build tree structure"""
            name = p.name
            item_type = "directory" if p.is_dir() else "file"
            
            result = {
                "name": name,
                "type": item_type
            }
            
            if p.is_dir():
                children = []
                try:
                    for child in p.iterdir():
                        # Check exclude patterns
                        should_exclude = False
                        for pattern in exclude_patterns:
                            if fnmatch(child.name, pattern) or fnmatch(str(child.relative_to(target)), pattern):
                                should_exclude = True
                                break
                        
                        if not should_exclude:
                            children.append(build_tree(child))
                except PermissionError:
                    pass
                
                result["children"] = sorted(children, key=lambda x: (x["type"] == "directory", x["name"]))
            else:
                # Files have no children
                pass
            
            return result
        
        tree = build_tree(target)
        return json.dumps(tree, indent=2)
        
    except Exception as e:
        logger.exception(f"Error building directory tree: {e}")
        return f"❌ Error: {str(e)}"


@mcp.tool()
async def move_file(
    source: str,
    destination: str
) -> str:
    """
    Move or rename files and directories. Can move files between directories and rename them in a single operation. If the destination exists, the operation will fail. Works across different directories and can be used for simple renaming within the same directory. Both source and destination must be within allowed directories.
    
    Args:
        source: Source file or directory path
        destination: Destination file or directory path
    
    Returns:
        Success message
    """
    try:
        src = Path(source).resolve()
        dst = Path(destination).resolve()
        
        # Security: Prevent moving outside workspace
        if not str(src).startswith(str(WORKSPACE_ROOT)):
            return f"❌ Access denied: Source path outside workspace"
        
        if not str(dst).startswith(str(WORKSPACE_ROOT)):
            return f"❌ Access denied: Destination path outside workspace"
        
        if not src.exists():
            return f"❌ Source does not exist: {src}"
        
        if dst.exists():
            return f"❌ Destination already exists: {dst}"
        
        # Create parent directory if needed
        dst.parent.mkdir(parents=True, exist_ok=True)
        
        # Move file/directory
        src.rename(dst)
        
        return f"✅ Moved successfully: {src} -> {dst}"
        
    except Exception as e:
        logger.exception(f"Error moving file: {e}")
        return f"❌ Error: {str(e)}"


@mcp.tool()
async def search_files(
    path: Optional[str] = None,
    pattern: str = "*",
    exclude_patterns: Optional[List[str]] = None
) -> str:
    """
    Recursively search for files and directories matching a pattern. The patterns should be glob-style patterns that match paths relative to the working directory. Use pattern like '*.ext' to match files in current directory, and '**/*.ext' to match files in all subdirectories. Returns full paths to all matching items. Great for finding files when you don't know their exact location. Only searches within allowed directories.
    
    Args:
        path: Directory to search in (default: workspace root)
        pattern: Glob pattern to match (e.g., '*.py', '**/*.json')
        exclude_patterns: List of glob patterns to exclude (optional)
    
    Returns:
        List of matching file paths
    """
    try:
        from fnmatch import fnmatch
        
        target = Path(path) if path else WORKSPACE_ROOT
        target = target.resolve()
        
        # Security: Prevent searching outside workspace
        if not str(target).startswith(str(WORKSPACE_ROOT)):
            return f"❌ Access denied: Path outside workspace"
        
        if not target.exists():
            return f"❌ Path does not exist: {target}"
        
        if not target.is_dir():
            return f"❌ Not a directory: {target}"
        
        exclude_patterns = exclude_patterns or []
        matches = []
        
        # Handle ** pattern (recursive)
        if '**' in pattern:
            # Recursive search
            for root, dirs, files in os.walk(target):
                root_path = Path(root)
                
                # Check all items in this directory
                for item in list(dirs) + files:
                    item_path = root_path / item
                    rel_path = item_path.relative_to(target)
                    
                    # Check exclude patterns
                    should_exclude = False
                    for excl_pattern in exclude_patterns:
                        if fnmatch(item, excl_pattern) or fnmatch(str(rel_path), excl_pattern):
                            should_exclude = True
                            break
                    
                    if should_exclude:
                        continue
                    
                    # Check match pattern
                    if fnmatch(item, pattern.replace('**/', '').replace('**', '*')) or fnmatch(str(rel_path), pattern):
                        matches.append(str(item_path))
        else:
            # Non-recursive search
            for item in target.rglob(pattern):
                # Check exclude patterns
                should_exclude = False
                rel_path = item.relative_to(target)
                for excl_pattern in exclude_patterns:
                    if fnmatch(item.name, excl_pattern) or fnmatch(str(rel_path), excl_pattern):
                        should_exclude = True
                        break
                
                if not should_exclude:
                    matches.append(str(item))
        
        return "\n".join(sorted(matches)) if matches else "No matches found"
        
    except Exception as e:
        logger.exception(f"Error searching files: {e}")
        return f"❌ Error: {str(e)}"


@mcp.tool()
async def get_file_info(
    path: str
) -> str:
    """
    Retrieve detailed metadata about a file or directory. Returns comprehensive information including size, creation time, last modified time, permissions, and type. This tool is perfect for understanding file characteristics without reading the actual content. Only works within allowed directories.
    
    Args:
        path: File or directory path
    
    Returns:
        File metadata as JSON
    """
    try:
        import stat
        from datetime import datetime
        
        file = Path(path).resolve()
        
        # Security: Prevent access outside workspace
        if not str(file).startswith(str(WORKSPACE_ROOT)):
            return f"❌ Access denied: Path outside workspace"
        
        if not file.exists():
            return f"❌ Path does not exist: {file}"
        
        stat_info = file.stat()
        
        info = {
            "path": str(file),
            "name": file.name,
            "type": "directory" if file.is_dir() else "file",
            "size": stat_info.st_size if file.is_file() else 0,
            "created": datetime.fromtimestamp(stat_info.st_ctime).isoformat(),
            "modified": datetime.fromtimestamp(stat_info.st_mtime).isoformat(),
            "permissions": oct(stat_info.st_mode)[-3:],
            "readable": os.access(file, os.R_OK),
            "writable": os.access(file, os.W_OK),
            "executable": os.access(file, os.X_OK),
        }
        
        return json.dumps(info, indent=2)
        
    except Exception as e:
        logger.exception(f"Error getting file info: {e}")
        return f"❌ Error: {str(e)}"


@mcp.tool()
async def list_allowed_directories() -> str:
    """
    Returns the list of directories that this server is allowed to access. Subdirectories within these allowed directories are also accessible. Use this to understand which directories and their nested paths are available before trying to access files.
    
    Returns:
        List of allowed directories
    """
    return f"Allowed directory: {WORKSPACE_ROOT}"


@mcp.tool()
async def query_florida_trust_law(
    query: str,
    top_k: int = 5,
    threshold: float = 0.3,
    as_json: bool = False,
) -> str:
    """
    Query the Florida Trust Law RAG corpus.
    Searches the vector index over Florida trust/probate law documents.
    Returns relevant statutes, case law, and rules.
    
    Args:
        query: The search query about Florida trust/probate law.
        top_k: Number of results to return (default: 5).
        threshold: Minimum similarity threshold (default: 0.3).
        as_json: Output as JSON (default: False, formatted text).
    
    Returns:
        Search results with similarity scores and source references.
    """
    try:
        import subprocess
        script = str(WORKSPACE_ROOT / "data" / "retrieval_packs" / "fl-trust-law" / "scripts" / "query_rag.py")
        cmd = ["python3", script, query, "--top-k", str(top_k)]
        if threshold != 0.3:
            cmd += ["--threshold", str(threshold)]
        if as_json:
            cmd.append("--json")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,
            cwd=str(WORKSPACE_ROOT / "data" / "retrieval_packs" / "fl-trust-law")
        )
        
        if result.returncode != 0:
            return f"Error querying Florida Trust Law RAG: {result.stderr}"
        
        return result.stdout
        
    except subprocess.TimeoutExpired:
        return "❌ Query timed out after 60 seconds."
    except Exception as e:
        logger.exception(f"Error in query_florida_trust_law: {e}")
        return f"❌ Error: {str(e)}"


if __name__ == "__main__":
    # Run server (FastMCP handles stdio automatically)
    mcp.run()
