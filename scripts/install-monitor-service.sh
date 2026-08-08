#!/bin/bash
# Install Tool Monitor Service
# Maat-Aligned Service Installation

set -e

echo "🔧 Installing Tehuti Tool Monitor service..."

# Copy service files
sudo cp /home/suspect/.n8n/systemd-services/tehuti-tool-monitor.service /etc/systemd/system/
sudo cp /home/suspect/.n8n/systemd-services/tehuti-tool-monitor.timer /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable and start
sudo systemctl enable tehuti-tool-monitor.service
sudo systemctl enable tehuti-tool-monitor.timer
sudo systemctl start tehuti-tool-monitor.timer

echo "✅ Tool monitor service installed and started"
echo ""
echo "📋 Check status:"
echo "   systemctl status tehuti-tool-monitor.service"
echo "   systemctl status tehuti-tool-monitor.timer"
echo ""
echo "📋 View logs:"
echo "   journalctl -u tehuti-tool-monitor.service -f"

