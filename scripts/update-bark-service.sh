#!/bin/bash
# Update Bark TTS service with latest configuration
# Maat-Aligned Service Update

set -e

echo "🔧 Updating Bark TTS service configuration..."

# Copy updated service file
sudo cp /home/suspect/.n8n/systemd-services/mcpo-tehuti-audio.service /etc/systemd/system/mcpo-tehuti-audio.service

# Reload systemd
sudo systemctl daemon-reload

# Restart service
sudo systemctl restart mcpo-tehuti-audio.service

echo "✅ Service updated and restarted"
echo ""
echo "📋 Check status:"
echo "   systemctl status mcpo-tehuti-audio.service"
echo ""
echo "📋 Test health:"
echo "   curl http://127.0.0.1:8021/health"
echo ""
echo "📋 View logs:"
echo "   journalctl -u mcpo-tehuti-audio.service -f"

