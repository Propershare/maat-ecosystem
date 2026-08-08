#!/usr/bin/env python3
"""
Check tehuti-core tool server configuration
"""

import sys
from pathlib import Path

backend_path = Path(__file__).parent.parent / "tehuti-lab-webui" / "backend"
sys.path.insert(0, str(backend_path))

# Import the config
from open_webui.utils.tools import set_tool_servers
from fastapi import Request
from unittest.mock import MagicMock

# Create a mock request
request = MagicMock(spec=Request)
request.app = MagicMock()
request.app.state = MagicMock()
request.app.state.config = MagicMock()
request.app.state.config.TOOL_SERVER_CONNECTIONS = []
request.app.state.redis = None

# This will call set_tool_servers which has the hardcoded config
import asyncio

async def check_config():
    servers = await set_tool_servers(request)
    tc = [s for s in servers if s.get('id') == 'tehuti-core']
    
    if tc:
        server = tc[0]
        print(f"tehuti-core server found:")
        print(f"  URL: {server.get('url')}")
        print(f"  Specs count: {len(server.get('specs', []))}")
        print(f"\nAll tool names in specs:")
        for i, spec in enumerate(server.get('specs', []), 1):
            print(f"  {i:2d}. {spec.get('name', 'NO NAME')}")
    else:
        print("tehuti-core not found in servers")

asyncio.run(check_config())

