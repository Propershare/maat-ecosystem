#!/bin/bash
# Test ACL enforcement
# Maat-Aligned ACL Testing

set -e

LDAP_HOST="${1:-127.0.0.1}"
LDAP_PORT="${2:-389}"
LDAP_ADMIN="${3:-cn=admin,dc=tehuti,dc=lab}"

echo "🧪 Testing ACL enforcement..."

if [ -z "$LDAP_ADMIN_PASSWORD" ]; then
    PASSWORD_FILE="/home/suspect/.n8n/tehuti-ldap/.ldap_admin_password"
    if [ -f "$PASSWORD_FILE" ]; then
        export LDAP_ADMIN_PASSWORD=$(cat "$PASSWORD_FILE")
    else
        echo "❌ Error: LDAP_ADMIN_PASSWORD not set and password file not found"
        exit 1
    fi
fi

# Test 1: Admin can read
echo "Test 1: Admin can read base DN..."
if ldapsearch -x -H "ldap://$LDAP_HOST:$LDAP_PORT" \
    -D "$LDAP_ADMIN" \
    -w "$LDAP_ADMIN_PASSWORD" \
    -b "dc=tehuti,dc=lab" \
    -s base "(objectClass=*)" > /dev/null 2>&1; then
    echo "✅ Admin can read (expected)"
else
    echo "❌ Admin cannot read (unexpected)"
    exit 1
fi

# Test 2: Anonymous cannot read (if ACLs are enforced)
echo ""
echo "Test 2: Anonymous access test..."
if ldapsearch -x -H "ldap://$LDAP_HOST:$LDAP_PORT" \
    -b "dc=tehuti,dc=lab" \
    -s base "(objectClass=*)" > /dev/null 2>&1; then
    echo "⚠️  Anonymous can read (may indicate ACLs not enforced)"
else
    echo "✅ Anonymous cannot read (ACLs working)"
fi

# Test 3: Admin can write
echo ""
echo "Test 3: Admin write access test..."
# Try to modify a test attribute (will revert)
TEST_DN="dc=tehuti,dc=lab"
if ldapmodify -x -H "ldap://$LDAP_HOST:$LDAP_PORT" \
    -D "$LDAP_ADMIN" \
    -w "$LDAP_ADMIN_PASSWORD" <<EOF 2>/dev/null; then
dn: $TEST_DN
changetype: modify
replace: description
description: ACL Test
EOF
    echo "✅ Admin can write (expected)"
    # Revert change
    ldapmodify -x -H "ldap://$LDAP_HOST:$LDAP_PORT" \
        -D "$LDAP_ADMIN" \
        -w "$LDAP_ADMIN_PASSWORD" <<EOF 2>/dev/null || true
dn: $TEST_DN
changetype: modify
replace: description
description: Tehuti Lab LDAP Directory - Maat-Aligned
EOF
else
    echo "❌ Admin cannot write (unexpected)"
fi

echo ""
echo "✅ ACL test complete"
echo ""
echo "📋 Note: Full ACL testing requires:"
echo "   1. Test user accounts with different permissions"
echo "   2. Test group-based access"
echo "   3. Test resource-specific access"

