#!/bin/bash
# Fix n8n Database Connection - Maat-Aligned
# Ensures n8n uses correct database credentials

set -e

ENV_FILE="$HOME/.n8n/.env"

echo "🔍 Checking n8n database configuration..."

# Verify database exists and is accessible
export PGPASSWORD='disdick'
if psql -h localhost -U suspect -d n8n -c "SELECT 1;" > /dev/null 2>&1; then
    echo "✅ Database 'n8n' is accessible"
else
    echo "❌ Cannot connect to database 'n8n'"
    exit 1
fi

# Check current config
if grep -q "DB_POSTGRESDB_DATABASE=n8n" "$ENV_FILE"; then
    echo "✅ Database name is correct: n8n"
else
    echo "⚠️  Database name might be wrong, checking..."
    grep DB_POSTGRESDB_DATABASE "$ENV_FILE" || echo "  Not found in .env"
fi

# Verify all DB settings
echo ""
echo "📋 Current database settings:"
grep "^DB_" "$ENV_FILE" | grep -v PASSWORD

echo ""
echo "✅ Configuration check complete"
echo ""
echo "To restart n8n with correct settings:"
echo "  pkill -f 'n8n.*start'"
echo "  cd ~/.n8n && export \$(cat .env | xargs) && /home/suspect/.nvm/versions/node/v20.19.4/bin/node /home/suspect/.nvm/versions/node/v20.19.4/lib/node_modules/n8n/bin/n8n start"

