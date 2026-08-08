#!/bin/bash
# Fix ComfyUI MCP Server
# Add missing sys import

set -e

echo "🔧 Fixing ComfyUI MCP server..."

# The sys import has been added to mcp_server_simple.py
# Now restart the service

sudo systemctl restart mcpo-comfyui-intelligent.service
sleep 5

if systemctl is-active --quiet mcpo-comfyui-intelligent.service; then
    echo "✅ ComfyUI Intelligent service started"
    
    # Wait a bit and check if it responds
    sleep 3
    HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 3 http://127.0.0.1:8019/openapi.json 2>/dev/null || echo "000")
    
    if [ "$HTTP_STATUS" = "200" ]; then
        echo "✅ ComfyUI Intelligent (port 8019) is responding"
        echo ""
        echo "🎉 All 10 tools are now working!"
    else
        echo "⚠️  Service started but not responding yet (HTTP: $HTTP_STATUS)"
        echo "   Check logs: journalctl -u mcpo-comfyui-intelligent.service -n 30"
    fi
else
    echo "❌ ComfyUI Intelligent service failed to start"
    echo "   Check logs: journalctl -u mcpo-comfyui-intelligent.service -n 30"
    exit 1
fi

