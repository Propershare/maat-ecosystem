#!/bin/bash
# Load ACL configuration into LDAP cn=config
# Maat-Aligned ACL Loading

set -e

LDAP_HOST="${1:-127.0.0.1}"
LDAP_PORT="${2:-389}"
LDAP_ADMIN="${3:-cn=admin,dc=tehuti,dc=lab}"
ACL_FILE="/home/suspect/.n8n/tehuti-ldap/config/acl.ldif"

echo "🔒 Loading ACL configuration into LDAP..."

if [ ! -f "$ACL_FILE" ]; then
    echo "❌ Error: ACL file not found: $ACL_FILE"
    exit 1
fi

if [ -z "$LDAP_ADMIN_PASSWORD" ]; then
    echo "⚠️  LDAP_ADMIN_PASSWORD not set. Reading from secure password file..."
    PASSWORD_FILE="/home/suspect/.n8n/tehuti-ldap/.ldap_admin_password"
    
    if [ -f "$PASSWORD_FILE" ]; then
        export LDAP_ADMIN_PASSWORD=$(cat "$PASSWORD_FILE")
    else
        echo "❌ Error: Password file not found: $PASSWORD_FILE"
        echo "   Create it with: echo 'password' > $PASSWORD_FILE && chmod 600 $PASSWORD_FILE"
        exit 1
    fi
fi

# Note: ACLs need to be loaded into cn=config, not the database
# This requires the server to be running with cn=config backend
echo "⚠️  Note: ACLs must be loaded into cn=config backend"
echo "   If using slapd.conf, ACLs are already in the config file"
echo "   If using cn=config, use ldapmodify to update olcAccess"
echo ""
echo "For cn=config backend, use:"
echo "  ldapmodify -x -H ldap://$LDAP_HOST:$LDAP_PORT -D \"cn=config\" -w <config_password> -f $ACL_FILE"
echo ""
echo "For slapd.conf (current setup), ACLs are in the config file and will be applied on restart"
echo ""
echo "✅ ACL configuration ready"
echo "   Restart LDAP server to apply: sudo systemctl restart tehuti-ldap"

