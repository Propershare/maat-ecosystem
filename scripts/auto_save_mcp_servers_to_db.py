#!/usr/bin/env python3
"""
Auto-Save MCP Servers to Tool Database
Maat: Order - Persist MCP servers so chat can use them
"""

import sys
import asyncio
from pathlib import Path
import time

# Add open-webui backend to path
workspace_root = Path(__file__).parent.parent
openwebui_backend = workspace_root / "open-webui" / "backend"
sys.path.insert(0, str(openwebui_backend))

from open_webui.config import get_config
from open_webui.utils.tools import get_tool_servers_data
from open_webui.models.tools import Tools, ToolForm, ToolModel

async def auto_save_mcp_servers():
    """Auto-save MCP servers to Tool database."""
    
    config = get_config()
    connections = config.get("TOOL_SERVER_CONNECTIONS", [])
    
    if not connections:
        print("❌ No tool servers configured")
        return
    
    print(f"📊 Fetching {len(connections)} MCP servers...")
    servers = await get_tool_servers_data(connections)
    
    if not servers:
        print("❌ No MCP servers fetched")
        return
    
    print(f"✅ Fetched {len(servers)} MCP servers")
    print()
    
    # Get existing tools
    existing_tools = Tools.get_tools()
    existing_ids = {tool.id for tool in existing_tools}
    
    saved = 0
    updated = 0
    
    for server in servers:
        server_id = f"server:{server['idx']}"
        server_name = server["openapi"].get("info", {}).get("title", "Tool Server")
        server_desc = server["openapi"].get("info", {}).get("description", "")
        
        # Check if already exists
        existing_tool = Tools.get_tool_by_id(server_id)
        
        if existing_tool:
            # Update existing
            tool_form = ToolForm(
                id=server_id,
                name=server_name,
                content="",  # MCP servers don't have content
                meta={
                    "description": server_desc,
                    "manifest": {
                        "type": "mcp_server",
                        "url": server["url"],
                        "idx": server["idx"]
                    }
                },
                access_control=connections[server["idx"]].get("config", {}).get("access_control", None)
            )
            
            # Update tool
            updated_data = {
                "name": server_name,
                "meta": tool_form.meta,
                "access_control": tool_form.access_control,
                "updated_at": int(time.time())
            }
            Tools.update_tool_by_id(server_id, updated_data)
            updated += 1
            print(f"🔄 Updated: {server_name} ({server_id})")
        else:
            # Create new
            tool_form = ToolForm(
                id=server_id,
                name=server_name,
                content="",  # MCP servers don't have content
                meta={
                    "description": server_desc,
                    "manifest": {
                        "type": "mcp_server",
                        "url": server["url"],
                        "idx": server["idx"]
                    }
                },
                access_control=connections[server["idx"]].get("config", {}).get("access_control", None)
            )
            
            # Insert new tool - get any user or use system
            from open_webui.models.users import Users
            from open_webui.internal.db import get_db
            from open_webui.models.users import User
            
            # Try to get any user from database
            user_id = None
            with get_db() as db:
                user = db.query(User).first()
                if user:
                    user_id = user.id
            
            if user_id:
                try:
                    Tools.insert_new_tool(user_id, tool_form, [])
                    saved += 1
                    print(f"✅ Saved: {server_name} ({server_id})")
                except Exception as e:
                    print(f"⚠️  Error saving {server_name}: {e}")
            else:
                print(f"❌ No user found in database, cannot save {server_name}")
                print(f"   Create a user first or run WebUI to initialize database")
    
    print()
    print(f"📊 Summary:")
    print(f"   Saved: {saved}")
    print(f"   Updated: {updated}")
    print(f"   Total in DB: {len(Tools.get_tools())}")
    print()
    print("✅ MCP servers are now in Tool database!")
    print("   Chat will now see all MCP servers via Tools.get_tools()")

if __name__ == "__main__":
    asyncio.run(auto_save_mcp_servers())

