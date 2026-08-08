#!/usr/bin/env python3
"""
Register Tehuti Core MCP Server in Open WebUI
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

from open_webui.config import TOOL_SERVER_CONNECTIONS, save_config
from open_webui.models.users import Users

# Get current connections
current_connections = TOOL_SERVER_CONNECTIONS.value or []

# Check if Tehuti Core already registered and update if needed
tehuti_core_index = None
for i, conn in enumerate(current_connections):
    if conn.get("info", {}).get("id") == "tehuti-core":
        tehuti_core_index = i
        break

# Remove old entry if exists (will replace with new format)
if tehuti_core_index is not None:
    print("🔄 Updating existing Tehuti Core registration...")
    current_connections.pop(tehuti_core_index)

# Create Tehuti Core MCP connection
# Using mcpo wrapper to expose stdio MCP server via HTTP (like other servers)
tehuti_core_connection = {
    "type": "mcp",
    "url": "http://127.0.0.1:8014",  # HTTP URL for mcpo wrapper
    "info": {
        "id": "tehuti-core",
        "name": "Tehuti Core",
        "description": "MaatCode powers - terminal execution, code running, system management",
    },
    "auth_type": "none",
    "config": {
        "enable": True
    }
}

# Add to connections
current_connections.append(tehuti_core_connection)

# Save configuration
try:
    TOOL_SERVER_CONNECTIONS.value = current_connections
    TOOL_SERVER_CONNECTIONS.save()
    print("✅ Tehuti Core MCP server registered successfully!")
    print(f"   Server ID: tehuti-core")
    print(f"   Command: python3 /home/suspect/.n8n/mcp-servers/tehuti-core/tehuti_core_server.py")
    print("\n⚠️  Restart WebUI for changes to take effect:")
    print("   sudo systemctl restart tehuti-lab-webui.service")
    print("   OR")
    print("   Stop and restart manually")
except Exception as e:
    print(f"❌ Error registering: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

