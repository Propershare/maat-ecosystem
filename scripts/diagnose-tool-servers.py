#!/usr/bin/env python3
"""
Diagnose why only 3 tools are showing in WebUI
"""

import sys
import os
import asyncio
import aiohttp
from pathlib import Path

# Add WebUI backend to path
webui_backend = Path("/home/suspect/.n8n/tehuti-lab-webui/backend")
sys.path.insert(0, str(webui_backend))

# Set environment
data_dir = Path("/home/suspect/.n8n/tehuti-lab-webui/data")
os.environ.setdefault("DATA_DIR", str(data_dir))
os.environ.setdefault("DATABASE_URL", f"sqlite:///{data_dir}/webui.db")

from open_webui.config import TOOL_SERVER_CONNECTIONS
from open_webui.utils.tools import get_tool_servers_data, get_tool_server_url

async def diagnose():
    print("🔍 Diagnosing Tool Server Issues\n")
    
    # Get registered tools
    conns = TOOL_SERVER_CONNECTIONS.value or []
    print(f"Registered tools: {len(conns)}\n")
    
    # Test fetching OpenAPI specs
    print("Testing OpenAPI spec fetching:")
    for i, conn in enumerate(conns):
        port = conn.get("url", "").split(":")[-1] if ":" in conn.get("url", "") else "N/A"
        url = conn.get("url", "")
        path = conn.get("path", "openapi.json")
        
        try:
            spec_url = get_tool_server_url(url, path)
            async with aiohttp.ClientSession() as session:
                async with session.get(spec_url, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        paths_count = len(data.get("paths", {}))
                        print(f"✅ Port {port}: {paths_count} paths - {data.get('info', {}).get('title', 'N/A')}")
                    else:
                        print(f"❌ Port {port}: HTTP {resp.status}")
        except Exception as e:
            print(f"❌ Port {port}: ERROR - {str(e)[:60]}")
    
    print("\n" + "="*50)
    print("Testing get_tool_servers_data (WebUI function):")
    
    try:
        results = await get_tool_servers_data(conns)
        print(f"\n✅ get_tool_servers_data returned {len(results)} servers:")
        for r in results:
            specs_count = len(r.get("specs", []))
            print(f"  - {r.get('id', 'N/A')}: {specs_count} tools")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(diagnose())

