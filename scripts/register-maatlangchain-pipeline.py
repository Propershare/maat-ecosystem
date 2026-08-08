#!/usr/bin/env python3
"""
Register MaatLangChain Pipeline MCP Server in Open WebUI
"""

import sys
import os
from pathlib import Path

# Activate venv if available
venv_python = Path("/home/suspect/.n8n/tehuti-lab-webui/venv/bin/python3")
if venv_python.exists():
    # Use venv Python
    pass

# Add WebUI backend to path
webui_backend = Path("/home/suspect/.n8n/tehuti-lab-webui/backend")
sys.path.insert(0, str(webui_backend))

# Set environment
data_dir = Path("/home/suspect/.n8n/tehuti-lab-webui/data")
data_dir.mkdir(parents=True, exist_ok=True)
os.environ.setdefault("DATA_DIR", str(data_dir))
os.environ.setdefault("DATABASE_URL", f"sqlite:///{data_dir}/webui.db")

try:
    from open_webui.config import TOOL_SERVER_CONNECTIONS
except ImportError as e:
    print(f"❌ Error importing WebUI config: {e}")
    print("💡 Try running from WebUI venv:")
    print("   cd /home/suspect/.n8n/tehuti-lab-webui")
    print("   source venv/bin/activate")
    print("   python3 ../scripts/register-maatlangchain-pipeline.py")
    sys.exit(1)

# Get current connections
current_connections = TOOL_SERVER_CONNECTIONS.value or []

# MaatLangChain Pipeline tool
pipeline_tool = {
    "id": "maatlangchain-pipeline",
    "name": "MaatLangChain Pipeline",
    "url": "http://127.0.0.1:8020",
    "path": "openapi.json",
    "description": "RAG/Agent pipeline with Tehuti Core integration for long workflows",
}

# Check if exists in current connections
found = False
for conn in current_connections:
    conn_url = conn.get("url", "")
    if pipeline_tool["url"] in conn_url:
        # Update existing entry
        conn.update({
            "type": "openapi",
            "url": pipeline_tool["url"],
            "path": pipeline_tool["path"],
            "auth_type": "none",
            "config": {"enable": True},
            "info": {
                "id": pipeline_tool["id"],
                "name": pipeline_tool["name"],
                "description": pipeline_tool.get("description", ""),
            },
        })
        updated_connections = current_connections
        found = True
        print(f"✅ Updated: {pipeline_tool['name']} ({pipeline_tool['url']})")
        break

if not found:
    # Add new entry
    updated_connections = current_connections + [{
        "type": "openapi",
        "url": pipeline_tool["url"],
        "path": pipeline_tool["path"],
        "auth_type": "none",
        "config": {"enable": True},
        "info": {
            "id": pipeline_tool["id"],
            "name": pipeline_tool["name"],
            "description": pipeline_tool.get("description", ""),
        },
    }]
    print(f"✅ Added: {pipeline_tool['name']} ({pipeline_tool['url']})")

# Save configuration
try:
    TOOL_SERVER_CONNECTIONS.value = updated_connections
    TOOL_SERVER_CONNECTIONS.save()
    print(f"\n✅ Successfully registered MaatLangChain Pipeline")
    print(f"   URL: {pipeline_tool['url']}")
    print(f"   Path: {pipeline_tool['path']}")
    print("\n⚠️  Restart WebUI for changes to take effect")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

