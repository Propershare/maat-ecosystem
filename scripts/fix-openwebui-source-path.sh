#!/bin/bash
# Fix OpenWebUI to use source code instead of installed package
# Maat: Order - Proper development workflow

echo "🔧 Fixing OpenWebUI to use source code..."

# Create override directory if it doesn't exist
sudo mkdir -p /etc/systemd/system/open-webui.service.d

# Create override file
sudo tee /etc/systemd/system/open-webui.service.d/override.conf > /dev/null << 'EOF'
[Service]
# Use source code instead of installed package
Environment="PYTHONPATH=/home/suspect/.n8n/open-webui/backend"
EOF

echo "✅ Override file created"
echo ""
echo "🔄 Reloading systemd..."
sudo systemctl daemon-reload

echo ""
echo "⚠️  Restart service to apply changes:"
echo "   sudo systemctl restart open-webui.service"
echo ""
echo "✅ After restart, service will use source code from:"
echo "   /home/suspect/.n8n/open-webui/backend"
echo ""
echo "📝 Future changes to source code will take effect after restart!"

