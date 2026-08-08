#!/bin/bash
# Fix n8n 502 Bad Gateway Error
# This script kills conflicting processes and restarts n8n service

echo "🔍 Diagnosing n8n port conflict..."

# 1. Find all processes using port 5678
echo "Processes using port 5678:"
sudo lsof -ti :5678 2>/dev/null | xargs -r ps -p

# 2. Kill docker-proxy if it exists
echo -e "\n🛑 Killing docker-proxy on port 5678..."
sudo pkill -9 -f "docker-proxy.*5678"

# 3. Kill any manual n8n processes
echo "🛑 Killing manual n8n processes..."
sudo pkill -9 -f "node.*n8n"
sudo pkill -9 -f "n8n.*start"

# 4. Wait for port to free
echo -e "\n⏳ Waiting for port 5678 to free..."
sleep 3

# 5. Verify port is free
if netstat -tlnp 2>/dev/null | grep -q :5678; then
    echo "❌ Port 5678 is still in use!"
    netstat -tlnp 2>/dev/null | grep :5678
    exit 1
else
    echo "✅ Port 5678 is free"
fi

# 6. Restart n8n service
echo -e "\n🔄 Restarting n8n service..."
sudo systemctl restart n8n.service

# 7. Wait for service to start
echo "⏳ Waiting for n8n to start..."
sleep 5

# 8. Check service status
echo -e "\n📊 n8n service status:"
sudo systemctl status n8n.service --no-pager | head -15

# 9. Test n8n endpoint
echo -e "\n🧪 Testing n8n endpoint..."
sleep 3
if curl -s http://localhost:5678/healthz > /dev/null 2>&1; then
    echo "✅ n8n is responding on localhost:5678"
    curl -s http://localhost:5678/healthz
else
    echo "❌ n8n is not responding"
    echo "Recent logs:"
    sudo journalctl -u n8n.service -n 20 --no-pager
fi

echo -e "\n✅ Fix script completed!"

