#!/bin/bash
# Quick script to refresh Open WebUI model cache
# This restarts the service to force model list refresh

echo "🔄 Refreshing Open WebUI Model Cache"
echo "====================================="
echo ""

# Check if running as root or with sudo
if [ "$EUID" -eq 0 ]; then
    SUDO=""
else
    SUDO="sudo"
fi

# Restart service
echo "Restarting tehuti-lab-webui.service..."
$SUDO systemctl restart tehuti-lab-webui.service

# Wait for service to start
echo "Waiting for service to start..."
sleep 5

# Check status
echo ""
echo "Service status:"
$SUDO systemctl status tehuti-lab-webui.service --no-pager | head -10

echo ""
echo "✅ Service restarted. Model cache should be refreshed."
echo ""
echo "Verify model appears in Open WebUI UI at:"
echo "  http://localhost:8088 (or your configured port)"
echo ""

