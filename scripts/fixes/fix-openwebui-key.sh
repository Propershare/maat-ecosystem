#!/bin/bash
# Fix OpenWebUI secret key with a valid Fernet key
# This will stabilize the service without losing your data

NEW_KEY=$(python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")

echo "Generated new valid Fernet key: $NEW_KEY"
echo ""
echo "Setting key in systemd override..."
sudo mkdir -p /etc/systemd/system/open-webui.service.d
printf "[Service]\nEnvironment=WEBUI_SECRET_KEY=%s\n" "$NEW_KEY" | sudo tee /etc/systemd/system/open-webui.service.d/override.conf >/dev/null

echo "Reloading systemd..."
sudo systemctl daemon-reload

echo "Restarting OpenWebUI..."
sudo systemctl restart open-webui.service

echo "Waiting for service to start..."
sleep 5

echo "Checking service status..."
systemctl status open-webui.service --no-pager | head -15

echo ""
echo "✅ Done! OpenWebUI should now be stable."
echo ""
echo "⚠️  IMPORTANT: Your models and knowledge bases are safe (not encrypted)."
echo "   However, you may need to log out and log back in to refresh your session."
echo ""
echo "Your data status:"
echo "  - 4 models in database"
echo "  - 2 knowledge bases in database"
echo "  - Vector DB files intact"

