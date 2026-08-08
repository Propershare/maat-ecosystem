#!/bin/bash
# CRITICAL: Kill docker-proxy on port 5678 - requires sudo
# This is the ONLY way to free port 5678 for n8n

echo "🔴 KILLING docker-proxy on port 5678..."

# Find and kill ALL docker-proxy processes on port 5678
sudo pkill -9 -f "docker-proxy.*5678"

# Also kill any n8n processes
sudo pkill -9 -f "node.*n8n"
sudo pkill -9 -f "n8n.*start"

# Wait
sleep 2

# Verify
if ps aux | grep -q "docker-proxy.*5678"; then
    echo "❌ docker-proxy still running - need to find source"
    ps aux | grep "docker-proxy.*5678"
    exit 1
else
    echo "✅ docker-proxy killed"
fi

# Check port
if netstat -tlnp 2>/dev/null | grep -q :5678; then
    echo "❌ Port 5678 still in use:"
    netstat -tlnp 2>/dev/null | grep :5678
    exit 1
else
    echo "✅ Port 5678 is FREE"
fi

echo "✅ Ready for n8n to start"

