#!/usr/bin/env python3
"""
Fix Tool Server URLs - Remove /openapi.json from URL field
Maat: Truth - Correct configuration based on WebUI code
"""

import sys
from pathlib import Path

workspace_root = Path(__file__).parent.parent
openwebui_backend = workspace_root / "open-webui" / "backend"
sys.path.insert(0, str(openwebui_backend))

from open_webui.config import get_config, save_config

def fix_tool_server_urls():
    """Fix tool server URLs - remove /openapi.json from URL field."""
    
    config = get_config()
    tool_servers = config.get("TOOL_SERVER_CONNECTIONS", [])
    
    fixed = 0
    for server in tool_servers:
        url = server.get("url", "")
        if "/openapi.json" in url:
            # Remove /openapi.json from URL (keep it in path only)
            server["url"] = url.replace("/openapi.json", "").rstrip("/")
            fixed += 1
            print(f"✅ Fixed: {server.get('name', 'Unknown')}")
            print(f"   Old: {url}")
            print(f"   New: {server['url']}")
            print()
    
    if fixed > 0:
        config["TOOL_SERVER_CONNECTIONS"] = tool_servers
        save_config(config)
        print(f"📊 Fixed {fixed} tool server URLs")
        print("🔄 Restart WebUI to apply changes")
    else:
        print("✅ All URLs are already correct")

if __name__ == "__main__":
    fix_tool_server_urls()

