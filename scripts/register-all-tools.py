#!/usr/bin/env python3
"""
Register ALL MCP tools: Core, Curriculum, Integration + Others (8015-8019)
"""

import sys
import os
from pathlib import Path

# Add WebUI backend to path
webui_backend = Path("/home/suspect/.n8n/tehuti-lab-webui/backend")
sys.path.insert(0, str(webui_backend))

# Set environment
data_dir = Path("/home/suspect/.n8n/tehuti-lab-webui/data")
data_dir.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("DATA_DIR", str(data_dir))
os.environ.setdefault("DATABASE_URL", f"sqlite:///{data_dir}/webui.db")

from open_webui.config import TOOL_SERVER_CONNECTIONS

# Get current connections
current_connections = TOOL_SERVER_CONNECTIONS.value or []

# Define ALL tools to register
all_tools = [
    # Core 3
    {
        "id": "tehuti-core",
        "name": "Tehuti Core",
        "url": "http://127.0.0.1:8014",
        "path": "openapi.json",
        "description": "MaatCode powers - terminal execution, code running, system management",
    },
    {
        "id": "tehuti-curriculum",
        "name": "Tehuti Curriculum",
        "url": "http://127.0.0.1:8011",
        "path": "openapi.json",
        "description": "Research methodologies and curriculum generation",
    },
    {
        "id": "tehuti-integration",
        "name": "Tehuti Integration",
        "url": "http://127.0.0.1:8013",
        "path": "openapi.json",
        "description": "Workflow automation via n8n",
    },
    # Others (8015-8019)
    {
        "id": "n8n-mcp",
        "name": "n8n MCP",
        "url": "http://127.0.0.1:8015",
        "path": "openapi.json",
        "description": "n8n workflow integration",
    },
    {
        "id": "filesystem-mcp",
        "name": "Filesystem MCP",
        "url": "http://127.0.0.1:8016",
        "path": "openapi.json",
        "description": "File system operations",
    },
    {
        "id": "postgres-mcp",
        "name": "Postgres MCP",
        "url": "http://127.0.0.1:8017",
        "path": "openapi.json",
        "description": "PostgreSQL database operations",
    },
    {
        "id": "memory-mcp",
        "name": "Memory MCP",
        "url": "http://127.0.0.1:8018",
        "path": "openapi.json",
        "description": "Memory management",
    },
    {
        "id": "comfyui-intelligent",
        "name": "ComfyUI Intelligent",
        "url": "http://127.0.0.1:8019",
        "path": "openapi.json",
        "description": "ComfyUI workflow execution",
    },
]

# Build updated connections list
updated_connections = []

for tool in all_tools:
    # Check if exists in current connections
    found = False
    for conn in current_connections:
        conn_url = conn.get("url", "")
        if tool["url"] in conn_url:
            # Update existing entry with info field
            conn.update({
                "type": "openapi",
                "url": tool["url"],
                "path": tool["path"],
                "auth_type": "none",
                "config": {"enable": True},
                "info": {
                    "id": tool["id"],
                    "name": tool["name"],
                    "description": tool.get("description", ""),
                },
            })
            updated_connections.append(conn)
            found = True
            print(f"✅ Kept: {tool['name']} ({tool['url']})")
            break
    
    if not found:
        # Add new entry with info field
        updated_connections.append({
            "type": "openapi",
            "url": tool["url"],
            "path": tool["path"],
            "auth_type": "none",
            "config": {"enable": True},
            "info": {
                "id": tool["id"],
                "name": tool["name"],
                "description": tool.get("description", ""),
            },
        })
        print(f"✅ Added: {tool['name']} ({tool['url']})")

# Save configuration
try:
    TOOL_SERVER_CONNECTIONS.value = updated_connections
    TOOL_SERVER_CONNECTIONS.save()
    print(f"\n✅ Successfully registered {len(updated_connections)} tools:")
    print("   Core: 8011, 8013, 8014")
    print("   Others: 8015, 8016, 8017, 8018, 8019")
    print("\n⚠️  Restart WebUI for changes to take effect")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

