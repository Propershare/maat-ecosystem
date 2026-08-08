#!/usr/bin/env python3
"""
Register ports 8015-8019 in Open WebUI with correct URL format
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

# Define tools to register (ports 8015-8019)
tools_to_register = [
    {
        "id": "n8n-mcp",
        "name": "n8n MCP",
        "url": "http://127.0.0.1:8015",
        "path": "openapi.json",
    },
    {
        "id": "filesystem-mcp",
        "name": "Filesystem MCP",
        "url": "http://127.0.0.1:8016",
        "path": "openapi.json",
    },
    {
        "id": "postgres-mcp",
        "name": "Postgres MCP",
        "url": "http://127.0.0.1:8017",
        "path": "openapi.json",
    },
    {
        "id": "memory-mcp",
        "name": "Memory MCP",
        "url": "http://127.0.0.1:8018",
        "path": "openapi.json",
    },
    {
        "id": "comfyui-intelligent",
        "name": "ComfyUI Intelligent",
        "url": "http://127.0.0.1:8019",
        "path": "openapi.json",
    },
]

# Remove existing entries for these ports
updated_connections = []
for conn in current_connections:
    conn_url = conn.get("url", "")
    # Keep if not one of our target ports
    if not any(f":{port}" in conn_url for port in [8015, 8016, 8017, 8018, 8019]):
        updated_connections.append(conn)

# Add new entries with correct format
for tool in tools_to_register:
    # Check if already exists
    exists = False
    for conn in updated_connections:
        if conn.get("url", "") == tool["url"]:
            exists = True
            # Update existing entry
            conn.update({
                "type": "openapi",
                "url": tool["url"],
                "path": tool["path"],
                "auth_type": "none",
                "config": {"enable": True},
            })
            break
    
    if not exists:
        # Add new entry
        updated_connections.append({
            "type": "openapi",
            "url": tool["url"],
            "path": tool["path"],
            "auth_type": "none",
            "config": {"enable": True},
        })
        print(f"✅ Added: {tool['name']} ({tool['url']})")
    else:
        print(f"🔄 Updated: {tool['name']} ({tool['url']})")

# Save configuration
try:
    TOOL_SERVER_CONNECTIONS.value = updated_connections
    TOOL_SERVER_CONNECTIONS.save()
    print(f"\n✅ Successfully registered {len(tools_to_register)} tools!")
    print("\n⚠️  Restart WebUI for changes to take effect")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

