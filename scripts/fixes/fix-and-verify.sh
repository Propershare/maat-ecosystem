#!/bin/bash
# Fix OpenWebUI and verify your data is accessible

echo "=== Step 1: Fixing OpenWebUI Secret Key ==="
NEW_KEY=$(python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")

echo "Generated valid Fernet key"
sudo mkdir -p /etc/systemd/system/open-webui.service.d
printf "[Service]\nEnvironment=WEBUI_SECRET_KEY=%s\n" "$NEW_KEY" | sudo tee /etc/systemd/system/open-webui.service.d/override.conf >/dev/null

echo "Reloading systemd..."
sudo systemctl daemon-reload

echo "Restarting OpenWebUI..."
sudo systemctl restart open-webui.service

echo "Waiting for service to stabilize..."
sleep 8

echo ""
echo "=== Step 2: Verifying Service Status ==="
systemctl status open-webui.service --no-pager | head -20

echo ""
echo "=== Step 3: Verifying Your Data ==="
echo "Models in database:"
sqlite3 open-webui/data/webui.db "SELECT name FROM model WHERE is_active=1;" 2>/dev/null

echo ""
echo "Knowledge bases in database:"
sqlite3 open-webui/data/webui.db "SELECT name FROM knowledge;" 2>/dev/null

echo ""
echo "=== Step 4: Checking Port ==="
ss -ltnp | grep 3000 || echo "⚠️  Port 3000 not listening yet - service may still be starting"

echo ""
echo "✅ Fix complete!"
echo ""
echo "Next steps:"
echo "1. Wait 30 seconds for service to fully start"
echo "2. Go to https://ai.suspecttv.com"
echo "3. Log out completely (if logged in)"
echo "4. Clear browser cache (Ctrl+Shift+Delete, clear all)"
echo "5. Log back in"
echo "6. Your models and knowledge bases should appear"
echo ""
echo "If you still don't see your data, the issue may be:"
echo "  - User session mismatch (try creating a new user or checking user_id)"
echo "  - Browser cache issue (try incognito/private window)"
echo "  - Data visibility permissions"

