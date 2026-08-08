#!/bin/bash
# Restore LDAP database from backup
# Maat-Aligned Restore Script

set -e

if [ -z "$1" ]; then
    echo "Usage: $0 <backup_file.ldif.gz>"
    echo ""
    echo "Available backups:"
    ls -lh /home/suspect/.n8n/tehuti-ldap/backups/*.ldif.gz 2>/dev/null || echo "No backups found"
    exit 1
fi

BACKUP_FILE="$1"

if [ ! -f "$BACKUP_FILE" ]; then
    echo "❌ Error: Backup file not found: $BACKUP_FILE"
    exit 1
fi

echo "⚠️  WARNING: This will replace all LDAP data!"
read -p "Are you sure you want to continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "Restore cancelled"
    exit 0
fi

echo "🔄 Restoring LDAP database from: $BACKUP_FILE"

# Get password from secure file
PASSWORD_FILE="/home/suspect/.n8n/tehuti-ldap/.ldap_admin_password"
if [ -z "$LDAP_ADMIN_PASSWORD" ]; then
    if [ -f "$PASSWORD_FILE" ]; then
        export LDAP_ADMIN_PASSWORD=$(cat "$PASSWORD_FILE")
    else
        echo "❌ Error: LDAP_ADMIN_PASSWORD not set and password file not found: $PASSWORD_FILE"
        echo "   Create it with: ./scripts/create-password-file.sh"
        exit 1
    fi
fi

# Stop LDAP server
sudo systemctl stop tehuti-ldap.service || true

# Extract backup
TEMP_FILE=$(mktemp)
if [[ "$BACKUP_FILE" == *.gz ]]; then
    gunzip -c "$BACKUP_FILE" > "$TEMP_FILE"
else
    cp "$BACKUP_FILE" "$TEMP_FILE"
fi

# Clear existing data (if needed)
# Note: This is destructive - use with caution

# Restore data
ldapadd -x -H ldap://127.0.0.1:389 -D "cn=admin,dc=tehuti,dc=lab" -w "$LDAP_ADMIN_PASSWORD" -f "$TEMP_FILE"

# Clean up
rm "$TEMP_FILE"

# Start LDAP server
sudo systemctl start tehuti-ldap.service

echo "✅ Restore completed"

