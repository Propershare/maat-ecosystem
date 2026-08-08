#!/bin/bash
# Fix all OpenWebUI data directory permissions

echo "=== Fixing OpenWebUI Data Directory Permissions ==="

DATA_DIR="/home/suspect/.n8n/open-webui/data"

echo "Fixing ownership of data directory..."
sudo chown -R suspect:suspect "$DATA_DIR"

echo "Fixing permissions..."
sudo chmod -R 755 "$DATA_DIR"
sudo chmod 644 "$DATA_DIR/webui.db" 2>/dev/null || true

echo ""
echo "=== Setting DATA_DIR in systemd ==="
sudo mkdir -p /etc/systemd/system/open-webui.service.d
cat > /tmp/override.conf <<EOF
[Service]
Environment=DATA_DIR=$DATA_DIR
Environment=WEBUI_SECRET_KEY=$(python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
EOF

sudo cp /tmp/override.conf /etc/systemd/system/open-webui.service.d/override.conf
sudo chmod 644 /etc/systemd/system/open-webui.service.d/override.conf

echo ""
echo "=== Reloading and restarting ==="
sudo systemctl daemon-reload
sudo systemctl restart open-webui.service

echo "Waiting for service to start..."
sleep 8

echo ""
echo "=== Verifying ==="
systemctl status open-webui.service --no-pager | head -15

echo ""
echo "=== Checking data ==="
echo "Models:"
sqlite3 "$DATA_DIR/webui.db" "SELECT COUNT(*) FROM model;" 2>/dev/null

echo ""
echo "Knowledge bases:"
sqlite3 "$DATA_DIR/webui.db" "SELECT COUNT(*) FROM knowledge;" 2>/dev/null

echo ""
echo "✅ All permissions fixed!"
echo ""
echo "OpenWebUI should now be running. Check https://ai.suspecttv.com"
echo "Your models and knowledge bases should be visible."

