#!/bin/bash
# Fix postgres tool URL if it's pointing to wrong port

DB="/home/suspect/.n8n/open-webui/data/webui.db"

echo "Checking for tools pointing to port 8000..."
sqlite3 "$DB" "SELECT id, name FROM tool WHERE content LIKE '%8000%';"

echo ""
echo "Updating postgres-tools to ensure correct URL..."
sqlite3 "$DB" <<EOF
UPDATE tool 
SET content = json_set(
    json(content),
    '$.url', 'http://127.0.0.1:8017'
),
specs = 'http://127.0.0.1:8017/openapi.json'
WHERE id = 'postgres-tools';
EOF

echo ""
echo "Verifying postgres-tools URL..."
sqlite3 "$DB" "SELECT id, json_extract(content, '$.url') as url, specs FROM tool WHERE id = 'postgres-tools';"

echo ""
echo "✅ Done! Restart OpenWebUI to clear cache:"
echo "   systemctl restart open-webui"

