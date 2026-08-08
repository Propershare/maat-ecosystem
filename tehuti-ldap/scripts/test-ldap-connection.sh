#!/bin/bash
# Test LDAP connection from remote workstations
# Maat-Aligned Connection Test

set -e

LDAP_SERVER="${1:-47.200.181.85}"
LDAP_PORT="${2:-389}"
LDAP_BASE="${3:-dc=tehuti,dc=lab}"
LDAP_ADMIN="${4:-cn=admin,dc=tehuti,dc=lab}"

echo "🔍 Testing LDAP connection..."
echo "   Server: $LDAP_SERVER:$LDAP_PORT"
echo "   Base DN: $LDAP_BASE"
echo ""

# Test 1: Basic connectivity
echo "Test 1: Basic connectivity..."
if timeout 5 bash -c "echo > /dev/tcp/$LDAP_SERVER/$LDAP_PORT" 2>/dev/null; then
    echo "✅ Port $LDAP_PORT is accessible"
else
    echo "❌ Port $LDAP_PORT is not accessible"
    exit 1
fi

# Get password from secure file if not set
if [ -z "$LDAP_ADMIN_PASSWORD" ]; then
    PASSWORD_FILE="/home/suspect/.n8n/tehuti-ldap/.ldap_admin_password"
    if [ -f "$PASSWORD_FILE" ]; then
        export LDAP_ADMIN_PASSWORD=$(cat "$PASSWORD_FILE")
    fi
fi

# Test 2: LDAP bind (if password provided)
if [ -n "$LDAP_ADMIN_PASSWORD" ]; then
    echo ""
    echo "Test 2: LDAP bind..."
    if ldapsearch -x -H "ldap://$LDAP_SERVER:$LDAP_PORT" \
        -D "$LDAP_ADMIN" \
        -w "$LDAP_ADMIN_PASSWORD" \
        -b "$LDAP_BASE" \
        -s base "(objectClass=*)" > /dev/null 2>&1; then
        echo "✅ LDAP bind successful"
    else
        echo "❌ LDAP bind failed"
        exit 1
    fi
else
    echo "⚠️  Skipping bind test (LDAP_ADMIN_PASSWORD not set)"
fi

# Test 3: Search for base DN
if [ -n "$LDAP_ADMIN_PASSWORD" ]; then
    echo ""
    echo "Test 3: Search base DN..."
    RESULT=$(ldapsearch -x -H "ldap://$LDAP_SERVER:$LDAP_PORT" \
        -D "$LDAP_ADMIN" \
        -w "$LDAP_ADMIN_PASSWORD" \
        -b "$LDAP_BASE" \
        -s base "(objectClass=*)" dn 2>/dev/null | grep "^dn:" | head -1)
    
    if [ -n "$RESULT" ]; then
        echo "✅ Base DN found: $RESULT"
    else
        echo "❌ Base DN not found"
        exit 1
    fi
fi

# Test 4: Search for users
if [ -n "$LDAP_ADMIN_PASSWORD" ]; then
    echo ""
    echo "Test 4: Search users..."
    USER_COUNT=$(ldapsearch -x -H "ldap://$LDAP_SERVER:$LDAP_PORT" \
        -D "$LDAP_ADMIN" \
        -w "$LDAP_ADMIN_PASSWORD" \
        -b "ou=users,$LDAP_BASE" \
        "(objectClass=maatUser)" dn 2>/dev/null | grep "^dn:" | wc -l)
    
    echo "✅ Found $USER_COUNT users"
fi

echo ""
echo "✅ All connection tests passed!"

