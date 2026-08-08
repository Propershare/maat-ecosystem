#!/bin/bash
# Backup LDAP database
# Maat-Aligned Backup Script

set -e

BACKUP_DIR="/home/suspect/.n8n/tehuti-ldap/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/ldap_backup_$DATE.ldif"
PASSWORD_FILE="/home/suspect/.n8n/tehuti-ldap/.ldap_admin_password"

echo "📦 Backing up LDAP database..."

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Get password from secure file
if [ -z "$LDAP_ADMIN_PASSWORD" ]; then
    if [ -f "$PASSWORD_FILE" ]; then
        export LDAP_ADMIN_PASSWORD=$(cat "$PASSWORD_FILE")
    else
        echo "❌ Error: LDAP_ADMIN_PASSWORD not set and password file not found: $PASSWORD_FILE"
        echo "   Create it with: ./scripts/create-password-file.sh"
        exit 1
    fi
fi

# Backup LDAP data
ldapsearch -x -H ldap://127.0.0.1:389 -D "cn=admin,dc=tehuti,dc=lab" -w "$LDAP_ADMIN_PASSWORD" -b "dc=tehuti,dc=lab" > "$BACKUP_FILE"

# Compress backup
gzip "$BACKUP_FILE"

echo "✅ Backup completed: ${BACKUP_FILE}.gz"

# Keep only last 30 backups
find "$BACKUP_DIR" -name "ldap_backup_*.ldif.gz" -type f -mtime +30 -delete

echo "✅ Old backups cleaned (kept last 30 days)"

