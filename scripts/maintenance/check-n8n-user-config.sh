#!/bin/bash
# Check n8n user configuration

echo "=== Current System User ==="
whoami
id

echo ""
echo "=== n8n Service User ==="
systemctl show n8n.service | grep User=

echo ""
echo "=== PostgreSQL Users ==="
psql -U suspect -d jarvis -c "\du" 2>&1 | grep -E "suspect|imhotep"

echo ""
echo "=== n8n Database Connections ==="
psql -U suspect -d jarvis -c "SELECT usename, datname, application_name FROM pg_stat_activity WHERE application_name LIKE '%n8n%' OR datname = 'n8n';" 2>&1

echo ""
echo "=== n8n Environment (from .env if readable) ==="
if [ -f /home/suspect/.n8n/.env ]; then
    grep -E "DB_|DATABASE|POSTGRES|USER" /home/suspect/.n8n/.env 2>/dev/null | head -10
else
    echo ".env file not readable or doesn't exist"
fi

echo ""
echo "=== n8n Process Info ==="
ps aux | grep "[n]8n" | grep -v systemd | head -3

