#!/bin/bash
# Load password policy into LDAP
# Maat-Aligned Policy Loading

set -e

LDAP_HOST="${1:-127.0.0.1}"
LDAP_PORT="${2:-389}"
LDAP_ADMIN="${3:-cn=admin,dc=tehuti,dc=lab}"
POLICY_FILE="/home/suspect/.n8n/tehuti-ldap/config/password-policy.ldif"

echo "🔒 Loading password policy into LDAP..."

if [ ! -f "$POLICY_FILE" ]; then
    echo "❌ Error: Policy file not found: $POLICY_FILE"
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

# First, create policies OU if it doesn't exist
echo "Creating policies OU..."
ldapadd -x -H "ldap://$LDAP_HOST:$LDAP_PORT" \
    -D "$LDAP_ADMIN" \
    -w "$LDAP_ADMIN_PASSWORD" <<EOF 2>/dev/null || true
dn: ou=policies,dc=tehuti,dc=lab
objectClass: top
objectClass: organizationalUnit
ou: policies
description: Password policies
EOF

# Load password policy
echo "Loading password policy..."
if ldapadd -x -H "ldap://$LDAP_HOST:$LDAP_PORT" \
    -D "$LDAP_ADMIN" \
    -w "$LDAP_ADMIN_PASSWORD" \
    -f "$POLICY_FILE"; then
    echo "✅ Password policy loaded successfully"
else
    echo "⚠️  Policy may already exist or there was an error"
    echo "   Check with: ldapsearch -x -H ldap://$LDAP_HOST:$LDAP_PORT -D \"$LDAP_ADMIN\" -w \"<password>\" -b \"ou=policies,dc=tehuti,dc=lab\""
fi

echo ""
echo "📋 Verify policy is active:"
echo "   ldapsearch -x -H ldap://$LDAP_HOST:$LDAP_PORT -D \"$LDAP_ADMIN\" -w \"<password>\" -b \"cn=passwordPolicy,ou=policies,dc=tehuti,dc=lab\""

