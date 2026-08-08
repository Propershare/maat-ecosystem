#!/bin/bash
# Force models to be visible by checking and fixing access_control

echo "=== Checking Model Visibility ==="
USER_ID="b9937d92-97c1-42fb-90ea-ffa53f394a31"

echo "Current model status:"
sqlite3 open-webui/data/webui.db "SELECT id, name, is_active, access_control FROM model WHERE user_id='$USER_ID';" 2>/dev/null

echo ""
echo "=== Fixing Model Visibility ==="
echo "Setting all models to active and removing access_control restrictions..."

sqlite3 open-webui/data/webui.db <<EOF
UPDATE model SET is_active=1, access_control=NULL WHERE user_id='$USER_ID';
SELECT 'Updated models:', COUNT(*) FROM model WHERE user_id='$USER_ID' AND is_active=1;
EOF

echo ""
echo "=== Verifying Knowledge Bases ==="
sqlite3 open-webui/data/webui.db "SELECT id, name, user_id FROM knowledge;" 2>/dev/null

echo ""
echo "✅ Done! Models should now be visible."
echo ""
echo "Next steps:"
echo "1. Refresh OpenWebUI (hard refresh: Ctrl+Shift+R)"
echo "2. Check Settings → Models section"
echo "3. If still not visible, try logging out and back in"

