#!/bin/bash
# Fix OpenWebUI to use the correct data directory

echo "=== Setting DATA_DIR environment variable ==="
echo "This will make OpenWebUI use /home/suspect/.n8n/open-webui/data"

sudo mkdir -p /etc/systemd/system/open-webui.service.d
cat > /tmp/override.conf <<EOF
[Service]
Environment=DATA_DIR=/home/suspect/.n8n/open-webui/data
Environment=WEBUI_SECRET_KEY=$(python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
EOF

sudo cp /tmp/override.conf /etc/systemd/system/open-webui.service.d/override.conf
sudo chmod 644 /etc/systemd/system/open-webui.service.d/override.conf

echo ""
echo "=== Reloading systemd ==="
sudo systemctl daemon-reload

echo ""
echo "=== Restarting OpenWebUI ==="
sudo systemctl restart open-webui.service
sleep 5

echo ""
echo "=== Verifying ==="
systemctl status open-webui.service --no-pager | head -15

echo ""
echo "=== Checking data ==="
echo "Models in database:"
sqlite3 /home/suspect/.n8n/open-webui/data/webui.db "SELECT COUNT(*) FROM model;" 2>/dev/null

echo ""
echo "✅ Done! OpenWebUI is now configured to use the correct data directory."
echo ""
echo "NOW:"
echo "1. Hard refresh OpenWebUI (Ctrl+Shift+R)"
echo "2. Your models and knowledge bases should appear!"

