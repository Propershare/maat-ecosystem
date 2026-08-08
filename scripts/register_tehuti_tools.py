#!/usr/bin/env python3
"""
Register Tehuti Lab Python Tools in OpenWebUI Database
Replaces MCP servers with direct Python tools
"""
import os
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent / "tehuti-lab-webui" / "backend"
sys.path.insert(0, str(backend_path))

# Set environment
os.environ.setdefault("DATABASE_URL", "sqlite:////home/suspect/.n8n/tehuti-lab-webui/data/webui.db")

from open_webui.models.tools import Tools, ToolForm, ToolMeta
from open_webui.models.users import Users
from open_webui.internal.db import get_db
from open_webui.models.users import User
from open_webui.utils.tools import get_tool_specs
from open_webui.utils.plugin import load_tool_module_by_id
import uuid
import importlib

def register_tools():
    """Register all Tehuti Lab Python tools"""
    
    # Get admin user
    admin_user = Users.get_user_by_email("propershare@gmail.com")
    if not admin_user:
        with get_db() as db:
            admin_user = db.query(User).filter(User.role == "admin").first()
    
    if not admin_user:
        print("❌ No admin user found. Please create an admin user first.")
        return False
    
    print(f"✅ Using admin user: {admin_user.name} ({admin_user.email})")
    
    # Define tools to register
    tools_to_register = [
        {
            "name": "Tehuti Research Tools",
            "description": "Research methodology tools (direct Python, no MCP)",
            "module": "open_webui.tools.research_tools",
            "user_id": admin_user.id
        },
        {
            "name": "Tehuti Integration Tools",
            "description": "n8n workflow integration tools (direct Python, no MCP)",
            "module": "open_webui.tools.integration_tools",
            "user_id": admin_user.id
        },
        {
            "name": "Tehuti Filesystem Tools",
            "description": "Filesystem operations (direct Python, no MCP)",
            "module": "open_webui.tools.filesystem_tools",
            "user_id": admin_user.id
        },
    ]
    
    registered_count = 0
    for tool_def in tools_to_register:
        try:
            # Check if tool already exists by loading module
            try:
                module = importlib.import_module(tool_def["module"])
                # Check if tool exists in database by querying all tools
                all_tools = Tools.get_tools()
                existing = next((t for t in all_tools if t.name == tool_def["name"]), None)
                if existing:
                    print(f"⚠️  Tool '{tool_def['name']}' already exists (ID: {existing.id}), skipping...")
                    continue
            except Exception:
                pass
            
            # Load module to get specs
            module = importlib.import_module(tool_def["module"])
            # Get Tools class instance
            if hasattr(module, "Tools"):
                tools_instance = module.Tools()
                specs = get_tool_specs(tools_instance)
            else:
                print(f"⚠️  Module {tool_def['module']} has no Tools class, skipping...")
                continue
            
            if not specs:
                print(f"⚠️  No specs found for {tool_def['name']}, skipping...")
                continue
            
            # Create ToolForm
            tool_id = str(uuid.uuid4())
            form_data = ToolForm(
                id=tool_id,
                name=tool_def["name"],
                content=f"# {tool_def['name']}\n\n{tool_def['description']}",
                meta=ToolMeta(description=tool_def["description"]),
                access_control=None  # Public access
            )
            
            # Insert tool
            result = Tools.insert_new_tool(
                user_id=tool_def["user_id"],
                form_data=form_data,
                specs=specs
            )
            
            if result:
                print(f"✅ Registered: {tool_def['name']} (ID: {result.id})")
                registered_count += 1
            else:
                print(f"❌ Failed to register: {tool_def['name']}")
        except Exception as e:
            import traceback
            print(f"❌ Error registering {tool_def['name']}: {e}")
            traceback.print_exc()
    
    print(f"\n✅ Registered {registered_count} tools")
    return registered_count > 0

if __name__ == "__main__":
    success = register_tools()
    sys.exit(0 if success else 1)

