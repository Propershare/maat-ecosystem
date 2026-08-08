#!/bin/bash
# Fix database permissions and apply model fixes

USER_ID="b9937d92-97c1-42fb-90ea-ffa53f394a31"
DB_PATH="open-webui/data/webui.db"

echo "=== Fixing Database Permissions ==="
echo "Database is owned by root, fixing ownership..."
sudo chown suspect:suspect "$DB_PATH"
sudo chmod 644 "$DB_PATH"

echo ""
echo "=== Fixing Base Model Reference ==="
sqlite3 "$DB_PATH" <<EOF
UPDATE model SET base_model_id='llama3.2:3b' WHERE id='tom--jerry-branding-maverick' AND base_model_id='llama3.2:latest';
SELECT 'Fixed Tom & Jerry to use llama3.2:3b';
EOF

echo ""
echo "=== Ensuring All Models Are Active ==="
sqlite3 "$DB_PATH" <<EOF
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
sqlite3 "$DB_PATH" "SELECT name, base_model_id FROM model WHERE user_id='$USER_ID' AND is_active=1;" 2>/dev/null

echo ""
echo "Knowledge Bases:"
sqlite3 "$DB_PATH" "SELECT name FROM knowledge WHERE user_id='$USER_ID';" 2>/dev/null

echo ""
echo "✅ Database fixed and models updated!"
echo ""
echo "NOW IN OPENWEBUI:"
echo "1. Hard refresh (Ctrl+Shift+R)"
echo "2. Go to Settings (gear) → Models"
echo "3. Your 4 custom models should appear"
echo "4. Check Knowledge Bases section"

