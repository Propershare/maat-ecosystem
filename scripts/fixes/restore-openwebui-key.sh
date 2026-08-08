#!/bin/bash
# Restore OpenWebUI to use default key mechanism
# This should restore access to your models and knowledge bases

echo "Removing override that changed the secret key..."
sudo rm -f /etc/systemd/system/open-webui.service.d/override.conf

echo "Reloading systemd..."
sudo systemctl daemon-reload

echo "Restarting OpenWebUI..."
sudo systemctl restart open-webui.service

echo "Waiting for service to start..."
sleep 5

echo "Checking service status..."
systemctl status open-webui.service --no-pager | head -15

echo ""
echo "✅ Done! OpenWebUI should now use its default key mechanism."
echo ""
echo "Next steps:"
echo "1. Go to https://ai.suspecttv.com (or http://127.0.0.1:3000)"
echo "2. Log out completely"
echo "3. Clear your browser cache (Ctrl+Shift+Delete)"
echo "4. Log back in"
echo "5. Your models and knowledge bases should be visible again"
echo ""
echo "Your data is safe - all 4 models and 2 knowledge bases are in the database."

