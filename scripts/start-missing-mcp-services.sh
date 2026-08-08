#!/bin/bash
# Start missing MCP services
# Maat-Aligned Service Startup

echo "🚀 Starting missing MCP services..."
echo ""

# Check and start Tehuti Core (8014)
if ! curl -s http://127.0.0.1:8014/openapi.json > /dev/null 2>&1; then
    echo "Starting mcpo-tehuti-core.service (port 8014)..."
    sudo systemctl start mcpo-tehuti-core.service
    sleep 3
    if curl -s http://127.0.0.1:8014/openapi.json > /dev/null 2>&1; then
        echo "✅ Tehuti Core started"
    else
        echo "❌ Tehuti Core failed to start - check logs:"
        echo "   sudo journalctl -u mcpo-tehuti-core.service -n 20"
    fi
else
    echo "✅ Tehuti Core (8014) already running"
fi

# Check and start ComfyUI Intelligent (8019)
if ! curl -s http://127.0.0.1:8019/openapi.json > /dev/null 2>&1; then
    echo "Starting mcpo-comfyui-intelligent.service (port 8019)..."
    sudo systemctl start mcpo-comfyui-intelligent.service
    sleep 3
    if curl -s http://127.0.0.1:8019/openapi.json > /dev/null 2>&1; then
        echo "✅ ComfyUI Intelligent started"
    else
        echo "❌ ComfyUI Intelligent failed to start - check logs:"
        echo "   sudo journalctl -u mcpo-comfyui-intelligent.service -n 20"
    fi
else
    echo "✅ ComfyUI Intelligent (8019) already running"
fi

echo ""
echo "📊 Checking all MCP servers..."
WORKING=0
TOTAL=10

for port in 8011 8012 8013 8014 8015 8016 8017 8018 8019 8020; do
    if curl -s http://127.0.0.1:$port/openapi.json > /dev/null 2>&1; then
        WORKING=$((WORKING + 1))
        echo "  ✅ Port $port: Working"
    else
        echo "  ❌ Port $port: Not responding"
    fi
done

echo ""
echo "Summary: $WORKING / $TOTAL tools working"
if [ $WORKING -eq $TOTAL ]; then
    echo "✅ All tools are working!"
    echo ""
    echo "🔄 Restart WebUI to refresh tool list:"
    echo "   pkill -f 'open-webui serve'"
    echo "   cd /home/suspect/.n8n/tehuti-lab-webui && source venv/bin/activate"
    echo "   nohup open-webui serve --host 0.0.0.0 --port 3000 > /tmp/tehuti-webui.log 2>&1 &"
else
    echo "⚠️  Some tools are not working. Check service logs above."
fi

