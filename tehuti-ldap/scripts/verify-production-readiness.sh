#!/bin/bash
# Verify all configurations are applied and test end-to-end functionality
# Maat-Aligned Production Readiness Verification

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "🔍 Verifying production readiness..."
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

PASSED=0
FAILED=0
WARNINGS=0

# Function to check status
check_status() {
    local name="$1"
    local command="$2"
    local expected="$3"
    
    if eval "$command" > /dev/null 2>&1; then
        echo -e "${GREEN}✅${NC} $name"
        ((PASSED++))
        return 0
    else
        if [ "$expected" = "required" ]; then
            echo -e "${RED}❌${NC} $name (REQUIRED)"
            ((FAILED++))
            return 1
        else
            echo -e "${YELLOW}⚠️${NC} $name (OPTIONAL)"
            ((WARNINGS++))
            return 0
        fi
    fi
}

# Get password from secure file
PASSWORD_FILE="$PROJECT_DIR/.ldap_admin_password"
if [ -f "$PASSWORD_FILE" ]; then
    export LDAP_ADMIN_PASSWORD=$(cat "$PASSWORD_FILE")
else
    export LDAP_ADMIN_PASSWORD="${LDAP_ADMIN_PASSWORD:-changeme}"
fi

# 1. Check LDAP server is running
echo "1. Service Status"
check_status "LDAP server is running" \
    "sudo systemctl is-active --quiet tehuti-ldap.service" \
    "required"

# 2. Check secure password file exists
echo ""
echo "2. Security Configuration"
check_status "Secure password file exists" \
    "[ -f \"$PASSWORD_FILE\" ]" \
    "required"

check_status "Password file has correct permissions (600)" \
    "[ \$(stat -c %a \"$PASSWORD_FILE\" 2>/dev/null) = \"600\" ]" \
    "required"

# 3. Check password policy is loaded
echo ""
echo "3. Password Policy"
check_status "Password policy is loaded" \
    "ldapsearch -x -H ldap://127.0.0.1:389 -D \"cn=admin,dc=tehuti,dc=lab\" -w \"\$LDAP_ADMIN_PASSWORD\" -b \"cn=passwordPolicy,ou=policies,dc=tehuti,dc=lab\" -s base \"(objectClass=pwdPolicy)\" cn 2>/dev/null | grep -q \"cn: passwordPolicy\"" \
    "required"

# 4. Check ACLs are configured
echo ""
echo "4. Access Control"
check_status "ACLs are configured in slapd.conf" \
    "grep -q \"access to\" \"$PROJECT_DIR/config/slapd.conf\"" \
    "required"

# 5. Check firewall rules
echo ""
echo "5. Network Security"
check_status "Firewall rules configured (ufw)" \
    "sudo ufw status | grep -q \"389\|636\"" \
    "optional"

# 6. Check logging is configured
echo ""
echo "6. Logging"
check_status "Logging is configured in slapd.conf" \
    "grep -q \"loglevel\" \"$PROJECT_DIR/config/slapd.conf\"" \
    "required"

check_status "Log rotation is configured" \
    "[ -f \"/etc/logrotate.d/tehuti-ldap\" ]" \
    "optional"

# 7. Check SSL/TLS certificates
echo ""
echo "7. SSL/TLS"
check_status "SSL certificate exists" \
    "[ -f \"$PROJECT_DIR/ssl/ldap.crt\" ]" \
    "optional"

check_status "SSL key exists" \
    "[ -f \"$PROJECT_DIR/ssl/ldap.key\" ]" \
    "optional"

check_status "CA certificate exists" \
    "[ -f \"$PROJECT_DIR/ssl/ca.crt\" ]" \
    "optional"

# 8. Test LDAP connection
echo ""
echo "8. Connectivity"
check_status "LDAP connection works (port 389)" \
    "ldapsearch -x -H ldap://127.0.0.1:389 -D \"cn=admin,dc=tehuti,dc=lab\" -w \"\$LDAP_ADMIN_PASSWORD\" -b \"dc=tehuti,dc=lab\" -s base \"(objectClass=*)\" > /dev/null 2>&1" \
    "required"

check_status "LDAPS connection works (port 636)" \
    "ldapsearch -x -H ldaps://127.0.0.1:636 -D \"cn=admin,dc=tehuti,dc=lab\" -w \"\$LDAP_ADMIN_PASSWORD\" -b \"dc=tehuti,dc=lab\" -s base \"(objectClass=*)\" > /dev/null 2>&1" \
    "optional"

# 9. Check test suite
echo ""
echo "9. Test Suite"
check_status "Test requirements file exists" \
    "[ -f \"$PROJECT_DIR/tests/requirements.txt\" ]" \
    "required"

check_status "Security tests exist" \
    "[ -f \"$PROJECT_DIR/tests/test_security.py\" ]" \
    "required"

check_status "Error handling tests exist" \
    "[ -f \"$PROJECT_DIR/tests/test_error_handling.py\" ]" \
    "required"

check_status "Integration tests exist" \
    "[ -f \"$PROJECT_DIR/tests/test_integration.py\" ]" \
    "required"

check_status "Performance tests exist" \
    "[ -f \"$PROJECT_DIR/tests/test_performance.py\" ]" \
    "required"

# 10. Check documentation
echo ""
echo "10. Documentation"
check_status "Cross-workstation documentation exists" \
    "[ -f \"$PROJECT_DIR/docs/cross-workstation-setup.md\" ]" \
    "required"

check_status "User management documentation exists" \
    "[ -f \"$PROJECT_DIR/docs/USER_MANAGEMENT.md\" ]" \
    "required"

check_status "Group management documentation exists" \
    "[ -f \"$PROJECT_DIR/docs/GROUP_MANAGEMENT.md\" ]" \
    "required"

# Summary
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 Verification Summary"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}✅ Passed:${NC} $PASSED"
echo -e "${RED}❌ Failed:${NC} $FAILED"
echo -e "${YELLOW}⚠️  Warnings:${NC} $WARNINGS"
echo ""

# Calculate score
TOTAL=$((PASSED + FAILED + WARNINGS))
if [ $TOTAL -gt 0 ]; then
    SCORE=$((PASSED * 100 / TOTAL))
    echo "📈 Production Readiness Score: $SCORE%"
    echo ""
    
    if [ $FAILED -eq 0 ] && [ $SCORE -ge 95 ]; then
        echo -e "${GREEN}✅ Production Ready!${NC}"
        exit 0
    elif [ $FAILED -eq 0 ]; then
        echo -e "${YELLOW}⚠️  Mostly ready, but some optional items missing${NC}"
        exit 0
    else
        echo -e "${RED}❌ Not production ready. Please fix required items.${NC}"
        exit 1
    fi
else
    echo "❌ No checks performed"
    exit 1
fi

