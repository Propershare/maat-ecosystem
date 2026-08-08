"""
MaatCode MCP Server for WebUI Integration
Maat: Order - Unified tool access via MCP protocol
"""

import asyncio
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add maatlangchain to path
workspace_root = Path(__file__).parent.parent
maatlangchain_path = workspace_root / "maatlangchain"
if str(maatlangchain_path) not in sys.path:
    sys.path.insert(0, str(maatlangchain_path))

from mcp.server import Server
from mcp.types import Tool, TextContent
from maat_memory import MaatMemory, get_unique_agent_id
from maat_memory.project_discovery import discover_project
from maat_memory.standards import MaatStandards

log = logging.getLogger(__name__)

# Initialize MCP server
server = Server("maatcode")

# Initialize Maat Memory
memory = MaatMemory()
agent_id = get_unique_agent_id("maatcode_mcp")


@server.list_tools()
async def list_tools() -> List[Tool]:
    """List all available MaatCode tools."""
    return [
        Tool(
            name="get_tasks",
            description="Query tasks from gitMaat (Maat Memory database). Returns pending tasks for coordination.",
            inputSchema={
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "enum": ["pending", "in_progress", "completed", "cancelled"],
                        "description": "Task status filter",
                        "default": "pending"
                    },
                    "limit": {
                        "type": "number",
                        "description": "Maximum number of tasks to return",
                        "default": 10
                    },
                    "agent": {
                        "type": "string",
                        "description": "Filter by agent ID (optional)"
                    }
                }
            }
        ),
        Tool(
            name="log_change",
            description="Log a file change to gitMaat. Use this to track all modifications.",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the file that changed"
                    },
                    "change_type": {
                        "type": "string",
                        "enum": ["create", "update", "delete"],
                        "description": "Type of change"
                    },
                    "description": {
                        "type": "string",
                        "description": "Description of the change"
                    },
                    "reason": {
                        "type": "string",
                        "description": "Reason for the change"
                    }
                },
                "required": ["file_path", "change_type", "description"]
            }
        ),
        Tool(
            name="log_decision",
            description="Log a decision to gitMaat. Use this to track important decisions.",
            inputSchema={
                "type": "object",
                "properties": {
                    "context": {
                        "type": "string",
                        "description": "Context of the decision"
                    },
                    "decision": {
                        "type": "string",
                        "description": "The decision made"
                    },
                    "rationale": {
                        "type": "string",
                        "description": "Why this decision was made"
                    },
                    "alternatives": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Alternatives considered"
                    }
                },
                "required": ["context", "decision", "rationale"]
            }
        ),
        Tool(
            name="search_conversations",
            description="Search past conversations in gitMaat. Use this to learn from past work.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query"
                    },
                    "limit": {
                        "type": "number",
                        "description": "Maximum results",
                        "default": 10
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="get_recent_changes",
            description="Get recent file changes from gitMaat. Use this to see what other agents are working on.",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "number",
                        "description": "Maximum results",
                        "default": 20
                    },
                    "agent": {
                        "type": "string",
                        "description": "Filter by agent ID (optional)"
                    }
                }
            }
        ),
        Tool(
            name="discover_project",
            description="Discover project structure and suggest builds. Use this to understand what exists and what to build.",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_path": {
                        "type": "string",
                        "description": "Path to project (optional, defaults to current)"
                    }
                }
            }
        ),
        Tool(
            name="ask_question",
            description="Ask a question to gitMaat. Other agents can answer. Use this for coordination between workstations.",
            inputSchema={
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "Your question"
                    },
                    "context": {
                        "type": "string",
                        "description": "Additional context (optional)"
                    }
                },
                "required": ["question"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool calls."""
    try:
        if name == "get_tasks":
            tasks = memory.get_tasks(
                status=arguments.get("status", "pending"),
                limit=arguments.get("limit", 10),
                agent=arguments.get("agent")
            )
            return [TextContent(
                type="text",
                text=f"Found {len(tasks)} tasks:\n" + "\n".join([
                    f"- {t.get('title', 'Untitled')} (Status: {t.get('status')}, Priority: {t.get('priority', 'normal')})"
                    for t in tasks
                ])
            )]
        
        elif name == "log_change":
            memory.log_change(
                agent=agent_id,
                file_path=arguments["file_path"],
                change_type=arguments["change_type"],
                summary=arguments["description"],
                reason=arguments.get("reason", "")
            )
            return [TextContent(
                type="text",
                text=f"✅ Logged change: {arguments['change_type']} to {arguments['file_path']}"
            )]
        
        elif name == "log_decision":
            memory.log_decision(
                agent=agent_id,
                context=arguments["context"],
                decision_made=arguments["decision"],
                rationale=arguments["rationale"],
                options_considered=arguments.get("alternatives", [])
            )
            return [TextContent(
                type="text",
                text=f"✅ Logged decision: {arguments['decision']}"
            )]
        
        elif name == "search_conversations":
            results = memory.search_conversations(
                query=arguments["query"],
                limit=arguments.get("limit", 10)
            )
            return [TextContent(
                type="text",
                text=f"Found {len(results)} conversations:\n" + "\n".join([
                    f"- {r.get('user_query', 'N/A')[:100]}..."
                    for r in results
                ])
            )]
        
        elif name == "get_recent_changes":
            changes = memory.get_recent_changes(
                limit=arguments.get("limit", 20),
                agent=arguments.get("agent")
            )
            return [TextContent(
                type="text",
                text=f"Recent changes:\n" + "\n".join([
                    f"- {c.get('file_path')} ({c.get('change_type')}) by {c.get('agent', 'unknown')}"
                    for c in changes
                ])
            )]
        
        elif name == "discover_project":
            project_path = arguments.get("project_path")
            discovery = discover_project(project_path)
            return [TextContent(
                type="text",
                text=f"Project Discovery:\n"
                     f"Missing: {len(discovery.get('missing', []))} components\n"
                     f"Suggestions: {len(discovery.get('suggestions', []))} builds\n"
                     f"\nSuggestions:\n" + "\n".join([
                    f"- {s}"
                    for s in discovery.get('suggestions', [])[:10]
                ])
            )]
        
        elif name == "ask_question":
            # Log question as a task for other agents to answer
            question = arguments["question"]
            context = arguments.get("context", "")
            
            memory.log_task(
                agent=agent_id,
                title=f"Question: {question[:50]}",
                description=f"{question}\n\nContext: {context}",
                status="pending",
                priority="normal"
            )
            
            # Also log as conversation for searchability
            memory.log_conversation(
                agent=agent_id,
                user_query=f"QUESTION: {question}",
                agent_response=f"Question logged to gitMaat. Other agents can answer.",
                metadata={"type": "question", "context": context}
            )
            
            return [TextContent(
                type="text",
                text=f"✅ Question logged to gitMaat. Other agents will see it and can answer.\n\nQuestion: {question}"
            )]
        
        else:
            return [TextContent(
                type="text",
                text=f"❌ Unknown tool: {name}"
            )]
    
    except Exception as e:
        log.error(f"Error calling tool {name}: {e}")
        return [TextContent(
            type="text",
            text=f"❌ Error: {str(e)}"
        )]


async def main():
    """Run MCP server."""
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())

