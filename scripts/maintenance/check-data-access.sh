#!/bin/bash
# Check if data is accessible and what user owns it

echo "=== Checking OpenWebUI Data Access ==="
echo ""

echo "1. Service Status:"
systemctl is-active open-webui.service && echo "✅ Service is running" || echo "❌ Service is not running"

echo ""
echo "2. Port Status:"
ss -ltnp | grep 3000 && echo "✅ Port 3000 is listening" || echo "❌ Port 3000 not listening"

echo ""
echo "3. Models in Database:"
sqlite3 open-webui/data/webui.db "SELECT name, user_id FROM model WHERE is_active=1;" 2>/dev/null

echo ""
echo "4. Knowledge Bases in Database:"
sqlite3 open-webui/data/webui.db "SELECT name, user_id FROM knowledge;" 2>/dev/null

echo ""
echo "5. Users in Database:"
sqlite3 open-webui/data/webui.db "SELECT id, email, role FROM auth;" 2>/dev/null || echo "Could not query auth table"

echo ""
echo "6. Model Ownership Check:"
MODEL_USER=$(sqlite3 open-webui/data/webui.db "SELECT DISTINCT user_id FROM model LIMIT 1;" 2>/dev/null)
echo "Models belong to user_id: $MODEL_USER"

if [ ! -z "$MODEL_USER" ]; then
    echo "Checking if this user exists in auth table:"
    sqlite3 open-webui/data/webui.db "SELECT id, email FROM auth WHERE id='$MODEL_USER';" 2>/dev/null || echo "User not found in auth table - this might be the issue!"
fi

echo ""
echo "=== Recommendations ==="
echo "If models belong to a user_id that doesn't exist in auth table:"
echo "  - You may need to recreate the user account"
echo "  - Or reassign models to your current user"
echo ""
echo "If you see your email in the auth table:"
echo "  - Make sure you're logged in with that exact email"
echo "  - Try logging out and back in"
echo "  - Clear browser cache"

