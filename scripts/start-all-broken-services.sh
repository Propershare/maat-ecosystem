#!/bin/bash
# Start All Broken Services
# Maat-Aligned Service Recovery

echo "🚀 Starting broken services..."

# Start Tehuti Core
echo "Starting mcpo-tehuti-core.service..."
sudo systemctl start mcpo-tehuti-core.service
sleep 3
if systemctl is-active --quiet mcpo-tehuti-core.service; then
    echo "✅ Tehuti Core started"
else
    echo "❌ Tehuti Core failed to start"
    echo "   Check logs: journalctl -u mcpo-tehuti-core.service -n 30"
fi

# Start ComfyUI Intelligent
echo "Starting mcpo-comfyui-intelligent.service..."
sudo systemctl start mcpo-comfyui-intelligent.service
sleep 3
if systemctl is-active --quiet mcpo-comfyui-intelligent.service; then
    echo "✅ ComfyUI Intelligent started"
else
    echo "❌ ComfyUI Intelligent failed to start"
    echo "   Check logs: journalctl -u mcpo-comfyui-intelligent.service -n 30"
fi

echo ""
echo "📊 Checking all tools..."
WORKING=0
for port in 8011 8012 8013 8014 8015 8016 8017 8018 8019 8020; do
    status=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 2 http://127.0.0.1:$port/openapi.json 2>/dev/null || echo "000")
    if [ "$status" = "200" ]; then
        WORKING=$((WORKING + 1))
        echo "  ✅ Port $port: Working"
    else
        echo "  ❌ Port $port: Not responding"
    fi
done

echo ""
echo "Summary: $WORKING / 10 tools working"

