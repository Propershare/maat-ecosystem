#!/bin/bash
# Fix OpenWebUI Frontend Path
# Maat: Order - Point service to correct frontend location

echo "🔧 Fixing OpenWebUI frontend path..."

# Create override directory if it doesn't exist
sudo mkdir -p /etc/systemd/system/open-webui.service.d

# Add FRONTEND_BUILD_DIR to override
sudo tee -a /etc/systemd/system/open-webui.service.d/override.conf > /dev/null << 'EOF'

# Point to frontend in installed package
Environment="FRONTEND_BUILD_DIR=/home/suspect/.n8n/open-webui-venv/lib/python3.11/site-packages/open_webui/frontend"
EOF

echo "✅ Added FRONTEND_BUILD_DIR to service override"
echo ""
echo "🔄 Reloading systemd..."
sudo systemctl daemon-reload

echo ""
echo "🔄 Restarting service..."
sudo systemctl restart open-webui.service

echo ""
echo "⏳ Waiting for service to start..."
sleep 3

echo ""
echo "📊 Service status:"
systemctl status open-webui.service --no-pager | head -10

echo ""
echo "🧪 Testing frontend..."
curl -I http://127.0.0.1:3000 2>&1 | head -3

echo ""
echo "✅ Fix complete!"
echo ""
echo "Frontend should now be accessible at:"
echo "  http://127.0.0.1:3000"
echo "  https://ai.suspecttv.com"

