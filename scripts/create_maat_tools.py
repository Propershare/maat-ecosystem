#!/usr/bin/env python3
"""
Create Maat Tools in WebUI Database
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
        if hasattr(tool_module, "Tools"):
            tools_instance = tool_module.Tools()
            return (
                tools_instance.get_tools()
                if hasattr(tools_instance, "get_tools")
                else []
            )
        return []


def create_maat_tools():
    """Create maat_tools in WebUI database."""

    # Read tool file
    tool_file = workspace_root / "open-webui" / "data" / "tools" / "maat_tools.py"
    if not tool_file.exists():
        print(f"❌ Tool file not found: {tool_file}")
        return False

    tool_content = tool_file.read_text()

    # Get admin user for tool ownership
    from open_webui.internal.db import get_db
    from open_webui.models.users import User

    admin_user = None
    with get_db() as db:
        # Try to get admin user
        admin_user = db.query(User).filter(User.role == "admin").first()
        # If no admin, get first user
        if not admin_user:
            admin_user = db.query(User).first()

    if not admin_user:
        print("❌ No users found in database.")
        print("   Please log into WebUI first to create a user account.")
        print("   Then run this script again.")
        return False

    print(f"✅ Using user: {admin_user.email} (ID: {admin_user.id}, Role: {admin_user.role})")

    # Check if tool already exists
    existing_tool = Tools.get_tool_by_id("maat_tools")
    if existing_tool:
        print("⚠️  Tool 'maat_tools' already exists. Updating...")
        # Update existing tool
        try:
            tool_content = replace_imports(tool_content)
            tool_module, frontmatter = load_tool_module_by_id(
                "maat_tools", content=tool_content
            )
            specs = get_tool_specs(tool_module)

            updated = {
                "name": "Maat Tools",
                "content": tool_content,
                "specs": specs,
                "meta": {
                    "description": "Custom tools for Tehuti Lab - user info, time, calculator, and weather",
                    "manifest": frontmatter,
                },
                "user_id": admin_user.id,
            }

            Tools.update_tool_by_id("maat_tools", updated)
            print("✅ Tool 'maat_tools' updated successfully!")
            return True
        except Exception as e:
            print(f"❌ Error updating tool: {e}")
            import traceback

            traceback.print_exc()
            return False
    else:
        # Create new tool
        print("Creating new 'maat_tools' tool...")
        try:
            tool_content = replace_imports(tool_content)
            tool_module, frontmatter = load_tool_module_by_id(
                "maat_tools", content=tool_content
            )
            specs = get_tool_specs(tool_module)

            tool_form = ToolForm(
                id="maat_tools",
                name="Maat Tools",
                content=tool_content,
                meta={
                    "description": "Custom tools for Tehuti Lab - user info, time, calculator, and weather",
                    "manifest": frontmatter,
                },
            )

            tool = Tools.insert_new_tool(
                user_id=admin_user.id,  # Use admin user ID
                form_data=tool_form,
                specs=specs,
            )

            if tool:
                print("✅ Tool 'maat_tools' created successfully!")
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
    success = create_maat_tools()
    sys.exit(0 if success else 1)

