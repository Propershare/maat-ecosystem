#!/bin/bash
# Fix and Start All Services
# Complete setup script for all tools and monitoring

set -e

echo "🔧 Fixing and starting all services..."
echo ""

# 1. Fix Tehuti Core service file
echo "1. Fixing Tehuti Core service..."
sudo cp /home/suspect/.n8n/systemd-services/mcpo-tehuti-core-fixed.service /etc/systemd/system/mcpo-tehuti-core.service
echo "   ✅ Service file updated"

# 2. Reload systemd
echo ""
echo "2. Reloading systemd..."
sudo systemctl daemon-reload
echo "   ✅ Systemd reloaded"

# 3. Start broken services
echo ""
echo "3. Starting broken services..."
sudo systemctl start mcpo-tehuti-core.service
sleep 3
if systemctl is-active --quiet mcpo-tehuti-core.service; then
    echo "   ✅ Tehuti Core started"
else
    echo "   ❌ Tehuti Core failed - check logs"
fi

sudo systemctl start mcpo-comfyui-intelligent.service
sleep 3
if systemctl is-active --quiet mcpo-comfyui-intelligent.service; then
    echo "   ✅ ComfyUI Intelligent started"
else
    echo "   ❌ ComfyUI Intelligent failed - check logs"
fi

# 4. Install monitor service
echo ""
echo "4. Installing monitor service..."
sudo cp /home/suspect/.n8n/systemd-services/tehuti-tool-monitor.service /etc/systemd/system/
sudo cp /home/suspect/.n8n/systemd-services/tehuti-tool-monitor.timer /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable tehuti-tool-monitor.service
sudo systemctl enable tehuti-tool-monitor.timer
sudo systemctl start tehuti-tool-monitor.timer
echo "   ✅ Monitor service installed and started"

# 5. Verify all tools
echo ""
echo "5. Verifying all tools..."
WORKING=0
TOTAL=10
for port in 8011 8012 8013 8014 8015 8016 8017 8018 8019 8020; do
    status=$(curl -s -o /dev/null -w "%{http_code}" --connect-timeout 2 http://127.0.0.1:$port/openapi.json 2>/dev/null || echo "000")
    if [ "$status" = "200" ]; then
        WORKING=$((WORKING + 1))
        echo "   ✅ Port $port: Working"
    else
        echo "   ❌ Port $port: Not responding"
    fi
done

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 Final Status: $WORKING / $TOTAL tools working"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if [ $WORKING -eq $TOTAL ]; then
    echo ""
    echo "✅ All tools are working!"
    echo "✅ Monitoring system is active"
    echo "✅ All services will start on reboot"
    echo ""
    echo "📋 Check monitor:"
    echo "   systemctl status tehuti-tool-monitor.service"
    echo "   journalctl -u tehuti-tool-monitor.service -f"
else
    echo ""
    echo "⚠️  Some tools are not working. Check service logs:"
    echo "   journalctl -u mcpo-tehuti-core.service -n 30"
    echo "   journalctl -u mcpo-comfyui-intelligent.service -n 30"
fi

