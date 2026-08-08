#!/bin/bash
# Complete fix: Fix base model reference and verify everything

USER_ID="b9937d92-97c1-42fb-90ea-ffa53f394a31"

echo "=== Fixing Base Model Reference ==="
sqlite3 open-webui/data/webui.db <<EOF
UPDATE model SET base_model_id='llama3.2:3b' WHERE id='tom--jerry-branding-maverick' AND base_model_id='llama3.2:latest';
SELECT 'Fixed Tom & Jerry to use llama3.2:3b';
EOF

echo ""
echo "=== Ensuring All Models Are Active ==="
sqlite3 open-webui/data/webui.db <<EOF
UPDATE model SET is_active=1 WHERE user_id='$USER_ID';
SELECT 'All models set to active';
EOF

echo ""
echo "=== Restarting OpenWebUI to Refresh ==="
sudo systemctl restart open-webui.service
sleep 5

echo ""
echo "=== Verification ==="
echo "Models:"
sqlite3 open-webui/data/webui.db "SELECT name, base_model_id FROM model WHERE user_id='$USER_ID' AND is_active=1;" 2>/dev/null

echo ""
echo "Knowledge Bases:"
sqlite3 open-webui/data/webui.db "SELECT name FROM knowledge WHERE user_id='$USER_ID';" 2>/dev/null

echo ""
echo "✅ Fixes applied!"
echo ""
echo "NOW DO THIS IN OPENWEBUI:"
echo "1. Hard refresh the page (Ctrl+Shift+R or Cmd+Shift+R)"
echo "2. Go to Settings (gear icon) → Models"
echo "3. Your 4 custom models should appear there"
echo "4. Check Knowledge Bases section for your 2 knowledge bases"
echo ""
echo "If still nothing:"
echo "  - Try incognito/private window"
echo "  - Check browser console for errors (F12)"
echo "  - Log out and log back in"

