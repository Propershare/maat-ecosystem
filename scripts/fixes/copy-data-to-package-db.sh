#!/bin/bash
# Copy your data from the correct location to where OpenWebUI might be looking

echo "=== Backing up current databases ==="
sudo cp open-webui/data/webui.db open-webui/data/webui.db.backup-$(date +%Y%m%d-%H%M%S)
sudo cp open-webui-venv/lib/python3.11/site-packages/open_webui/data/webui.db open-webui-venv/lib/python3.11/site-packages/open_webui/data/webui.db.backup-$(date +%Y%m%d-%H%M%S) 2>/dev/null || true

echo ""
echo "=== Copying your data to package database location ==="
echo "Source (has your data):"
sqlite3 open-webui/data/webui.db "SELECT COUNT(*) as models FROM model;" 2>/dev/null
echo ""

echo "Destination (currently empty):"
sqlite3 open-webui-venv/lib/python3.11/site-packages/open_webui/data/webui.db "SELECT COUNT(*) as models FROM model;" 2>/dev/null
echo ""

sudo cp open-webui/data/webui.db open-webui-venv/lib/python3.11/site-packages/open_webui/data/webui.db
sudo chown suspect:suspect open-webui-venv/lib/python3.11/site-packages/open_webui/data/webui.db

echo ""
echo "=== Verifying copy ==="
sqlite3 open-webui-venv/lib/python3.11/site-packages/open_webui/data/webui.db "SELECT COUNT(*) as models FROM model;" 2>/dev/null
sqlite3 open-webui-venv/lib/python3.11/site-packages/open_webui/data/webui.db "SELECT name FROM model LIMIT 5;" 2>/dev/null

echo ""
echo "=== Restarting OpenWebUI ==="
sudo systemctl restart open-webui.service
sleep 5

echo ""
echo "✅ Done! OpenWebUI should now see your data."
echo ""
echo "Check OpenWebUI now - your models and knowledge bases should appear!"

