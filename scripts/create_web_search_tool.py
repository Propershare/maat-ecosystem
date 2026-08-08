#!/usr/bin/env python3
"""
Create Web Search Tool in WebUI Database
Maat: Order - Automated tool creation
"""

import sys
import json
from pathlib import Path

# Add open-webui backend to path
workspace_root = Path(__file__).parent.parent
openwebui_backend = workspace_root / "open-webui" / "backend"
sys.path.insert(0, str(openwebui_backend))

from open_webui.models.tools import Tools, ToolForm
from open_webui.models.users import Users
from open_webui.utils.plugin import load_tool_module_by_id, replace_imports

# Import get_tool_specs from the correct location
try:
    from open_webui.utils.tools import get_tool_specs
except ImportError:
    # Fallback: define it here if not available
    def get_tool_specs(tool_module):
        """Extract tool specs from module."""
        if hasattr(tool_module, 'Tools'):
            tools_instance = tool_module.Tools()
            return tools_instance.get_tools() if hasattr(tools_instance, 'get_tools') else []
        return []

def create_web_search_tool():
    """Create web_search tool in WebUI database."""
    
    # Read tool file
    tool_file = workspace_root / "open-webui" / "data" / "tools" / "web_search.py"
    if not tool_file.exists():
        print(f"❌ Tool file not found: {tool_file}")
        return False
    
    tool_content = tool_file.read_text()
    
    # Check if tool already exists
    existing_tool = Tools.get_tool_by_id("web_search")
    if existing_tool:
        print("⚠️  Tool 'web_search' already exists. Updating...")
        # Update existing tool
        try:
            tool_content = replace_imports(tool_content)
            tool_module, frontmatter = load_tool_module_by_id("web_search", content=tool_content)
            specs = get_tool_specs(tool_module)
            
            updated = {
                "name": "Web Search",
                "content": tool_content,
                "specs": specs,
                "meta": {
                    "description": "Search the web for current information using SearXNG. Use for factual queries, current events, and up-to-date information.",
                    "manifest": frontmatter
                }
            }
            
            # Get admin user for update
            admin_user = Users.get_user_by_email("admin@example.com")
            if not admin_user:
                from open_webui.internal.db import get_db
                from open_webui.models.users import User
                with get_db() as db:
                    admin_user = db.query(User).filter(User.role == "admin").first()
            
            if admin_user:
                updated["user_id"] = admin_user.id
            
            Tools.update_tool_by_id("web_search", updated)
            print("✅ Tool 'web_search' updated successfully!")
            return True
        except Exception as e:
            print(f"❌ Error updating tool: {e}")
            import traceback
            traceback.print_exc()
            return False
    else:
        # Create new tool
        print("Creating new 'web_search' tool...")
        try:
            tool_content = replace_imports(tool_content)
            tool_module, frontmatter = load_tool_module_by_id("web_search", content=tool_content)
            specs = get_tool_specs(tool_module)
            
            tool_form = ToolForm(
                id="web_search",
                name="Web Search",
                content=tool_content,
                meta={
                    "description": "Search the web for current information using SearXNG. Use for factual queries, current events, and up-to-date information.",
                    "manifest": frontmatter
                }
            )
            
            # Get admin user for tool ownership
            admin_user = Users.get_user_by_email("admin@example.com")
            if not admin_user:
                # Try to get any admin user
                from open_webui.internal.db import get_db
                from open_webui.models.users import User
                with get_db() as db:
                    admin_user = db.query(User).filter(User.role == "admin").first()
            
            if not admin_user:
                print("❌ No admin user found. Cannot create tool without user ownership.")
                return False
            
            tool = Tools.insert_new_tool(
                user_id=admin_user.id,  # Use admin user ID
                form_data=tool_form,
                specs=specs
            )
            
            if tool:
                print("✅ Tool 'web_search' created successfully!")
                print(f"   ID: {tool.id}")
                print(f"   Name: {tool.name}")
                print(f"   Specs: {len(specs)} functions")
                return True
            else:
                print("❌ Failed to create tool")
                return False
                
        except Exception as e:
            print(f"❌ Error creating tool: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    success = create_web_search_tool()
    sys.exit(0 if success else 1)

