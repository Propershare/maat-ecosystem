#!/usr/bin/env python3
"""
Add All MCP Servers to WebUI Configuration
Maat: Order - Complete tool server configuration
"""

import sys
from pathlib import Path

# Add open-webui backend to path
workspace_root = Path(__file__).parent.parent
openwebui_backend = workspace_root / "open-webui" / "backend"
sys.path.insert(0, str(openwebui_backend))

from open_webui.config import get_config, save_config

def add_all_mcp_servers():
    """Add all 9 MCP servers to WebUI configuration."""
    
    config = get_config()
    
    # Define all MCP servers - CORRECT FORMAT:
    # - url: Base URL only (NO trailing path)
    # - path: Path without leading slash
    # WebUI concatenates: {url}/{path} = http://127.0.0.1:8012/openapi.json
    mcp_servers = [
        {
            "name": "Tehuti Curriculum",
            "url": "http://127.0.0.1:8011",
            "path": "openapi.json",
            "enabled": True
        },
        {
            "name": "Tehuti Research",
            "url": "http://127.0.0.1:8012",
            "path": "openapi.json",
            "enabled": True
        },
        {
            "name": "Tehuti Integration",
            "url": "http://127.0.0.1:8013",
            "path": "openapi.json",
            "enabled": True
        },
        {
            "name": "Tehuti Core",
            "url": "http://127.0.0.1:8014",
            "path": "openapi.json",
            "enabled": True
        },
        {
            "name": "n8n MCP",
            "url": "http://127.0.0.1:8015",
            "path": "openapi.json",
            "enabled": True
        },
        {
            "name": "Filesystem MCP",
            "url": "http://127.0.0.1:8016",
            "path": "openapi.json",
            "enabled": True
        },
        {
            "name": "Postgres MCP",
            "url": "http://127.0.0.1:8017",
            "path": "openapi.json",
            "enabled": True
        },
        {
            "name": "Memory MCP",
            "url": "http://127.0.0.1:8018",
            "path": "openapi.json",
            "enabled": True
        },
        {
            "name": "ComfyUI Intelligent",
            "url": "http://127.0.0.1:8019",
            "path": "openapi.json",
            "enabled": True
        },
    ]
    
    # REPLACE all existing connections (clean slate, prevents duplicates)
    config["TOOL_SERVER_CONNECTIONS"] = mcp_servers
    save_config(config)
    
    print()
    print(f"✅ Configured {len(mcp_servers)} MCP servers")
    print()
    print("📋 Servers configured:")
    for server in mcp_servers:
        print(f"   {server['name']}: {server['url']}/{server['path']}")
    print()
    print("🔄 Restart WebUI to apply changes:")
    print("   sudo systemctl restart open-webui.service")
    print()
    print("⚠️  IMPORTANT: This is the CORRECT format. Do not change URLs unless servers move.")

if __name__ == "__main__":
    add_all_mcp_servers()

