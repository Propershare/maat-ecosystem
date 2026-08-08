#!/bin/bash
# Create secure password file
# Maat-Aligned Secure Password Storage

set -e

PASSWORD_FILE="/home/suspect/.n8n/tehuti-ldap/.ldap_admin_password"

echo "🔒 Creating secure password file..."

if [ -f "$PASSWORD_FILE" ]; then
    echo "⚠️  Password file already exists: $PASSWORD_FILE"
    read -p "Overwrite? (yes/no): " confirm
    if [ "$confirm" != "yes" ]; then
        echo "Cancelled"
        exit 0
    fi
fi

read -sp "Enter LDAP admin password: " PASSWORD
echo ""
read -sp "Confirm LDAP admin password: " PASSWORD_CONFIRM
echo ""

if [ "$PASSWORD" != "$PASSWORD_CONFIRM" ]; then
    echo "❌ Passwords do not match"
    exit 1
fi

if [ -z "$PASSWORD" ]; then
    echo "❌ Password cannot be empty"
    exit 1
fi

# Create password file
echo "$PASSWORD" > "$PASSWORD_FILE"
chmod 600 "$PASSWORD_FILE"

echo "✅ Password file created: $PASSWORD_FILE"
echo "   Permissions: $(ls -l "$PASSWORD_FILE" | awk '{print $1}')"
echo ""
echo "📋 Usage in scripts:"
echo "   export LDAP_ADMIN_PASSWORD=\$(cat $PASSWORD_FILE)"
echo ""
echo "🔒 Security:"
echo "   - File permissions: 600 (owner read/write only)"
echo "   - Do NOT commit to git"
echo "   - Store backup securely"

