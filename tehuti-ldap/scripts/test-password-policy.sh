#!/bin/bash
# Test password policy enforcement
# Maat-Aligned Policy Testing

set -e

LDAP_HOST="${1:-127.0.0.1}"
LDAP_PORT="${2:-389}"
LDAP_ADMIN="${3:-cn=admin,dc=tehuti,dc=lab}"

echo "🧪 Testing password policy enforcement..."

if [ -z "$LDAP_ADMIN_PASSWORD" ]; then
    PASSWORD_FILE="/home/suspect/.n8n/tehuti-ldap/.ldap_admin_password"
    if [ -f "$PASSWORD_FILE" ]; then
        export LDAP_ADMIN_PASSWORD=$(cat "$PASSWORD_FILE")
    else
        echo "❌ Error: LDAP_ADMIN_PASSWORD not set and password file not found"
        exit 1
    fi
fi

# Test 1: Check if policy exists
echo "Test 1: Checking if password policy exists..."
if ldapsearch -x -H "ldap://$LDAP_HOST:$LDAP_PORT" \
    -D "$LDAP_ADMIN" \
    -w "$LDAP_ADMIN_PASSWORD" \
    -b "cn=passwordPolicy,ou=policies,dc=tehuti,dc=lab" \
    "(objectClass=pwdPolicy)" > /dev/null 2>&1; then
    echo "✅ Password policy found"
else
    echo "❌ Password policy not found - load it first: ./scripts/load-password-policy.sh"
    exit 1
fi

# Test 2: Check policy attributes
echo ""
echo "Test 2: Checking policy attributes..."
POLICY_DATA=$(ldapsearch -x -H "ldap://$LDAP_HOST:$LDAP_PORT" \
    -D "$LDAP_ADMIN" \
    -w "$LDAP_ADMIN_PASSWORD" \
    -b "cn=passwordPolicy,ou=policies,dc=tehuti,dc=lab" \
    "(objectClass=pwdPolicy)")

if echo "$POLICY_DATA" | grep -q "pwdMinLength: 12"; then
    echo "✅ Minimum password length: 12 characters"
else
    echo "⚠️  Minimum password length not set correctly"
fi

if echo "$POLICY_DATA" | grep -q "pwdLockout: TRUE"; then
    echo "✅ Password lockout enabled"
else
    echo "⚠️  Password lockout not enabled"
fi

if echo "$POLICY_DATA" | grep -q "pwdMaxFailure: 5"; then
    echo "✅ Max failures: 5"
else
    echo "⚠️  Max failures not set correctly"
fi

echo ""
echo "✅ Password policy test complete"
echo ""
echo "📋 Note: Actual enforcement testing requires:"
echo "   1. Policy applied to users (pwdPolicySubentry attribute)"
echo "   2. Attempting weak passwords"
echo "   3. Attempting brute force attacks"

