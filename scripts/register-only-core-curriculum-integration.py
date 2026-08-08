#!/usr/bin/env python3
"""
Register ONLY Tehuti Core, Curriculum, and Integration tools
Disable all others (Research, Filesystem, Postgres, Memory, n8n, ComfyUI)
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

# Define ONLY the 3 tools we want (Core, Curriculum, Integration)
tools_to_keep = [
    {
        "id": "tehuti-core",
        "name": "Tehuti Core",
        "url": "http://127.0.0.1:8014",
        "path": "openapi.json",
    },
    {
        "id": "tehuti-curriculum",
        "name": "Tehuti Curriculum",
        "url": "http://127.0.0.1:8011",
        "path": "openapi.json",
    },
    {
        "id": "tehuti-integration",
        "name": "Tehuti Integration",
        "url": "http://127.0.0.1:8013",
        "path": "openapi.json",
    },
]

# Build new connections list - ONLY keep the 3 we want
updated_connections = []

for tool in tools_to_keep:
    # Check if exists in current connections
    found = False
    for conn in current_connections:
        conn_url = conn.get("url", "")
        if tool["url"] in conn_url:
            # Update existing entry
            conn.update({
                "type": "openapi",
                "url": tool["url"],
                "path": tool["path"],
                "auth_type": "none",
                "config": {"enable": True},
            })
            updated_connections.append(conn)
            found = True
            print(f"✅ Kept: {tool['name']} ({tool['url']})")
            break
    
    if not found:
        # Add new entry
        updated_connections.append({
            "type": "openapi",
            "url": tool["url"],
            "path": tool["path"],
            "auth_type": "none",
            "config": {"enable": True},
        })
        print(f"✅ Added: {tool['name']} ({tool['url']})")

# Count disabled tools
disabled_count = len(current_connections) - len(updated_connections)
if disabled_count > 0:
    print(f"\n🚫 Disabled {disabled_count} other tools (Research, Filesystem, Postgres, Memory, n8n, ComfyUI)")

# Save configuration
try:
    TOOL_SERVER_CONNECTIONS.value = updated_connections
    TOOL_SERVER_CONNECTIONS.save()
    print(f"\n✅ Successfully configured {len(updated_connections)} tools:")
    print("   - Tehuti Core (8014)")
    print("   - Tehuti Curriculum (8011)")
    print("   - Tehuti Integration (8013)")
    print("\n⚠️  Restart WebUI for changes to take effect")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

