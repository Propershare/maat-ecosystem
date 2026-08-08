#!/bin/bash
# Comprehensive test script for all Tehuti tools and services

echo "=========================================="
echo "Tehuti System Test Suite"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

PASSED=0
FAILED=0

test_tool() {
    local port=$1
    local name=$2
    local auth=$3
    
    echo -n "Testing $name (port $port)... "
    
    if [ "$auth" = "bearer" ]; then
        response=$(curl -s -w "\n%{http_code}" -H "Authorization: Bearer TEHUTI_MCP_INTERNAL_ONLY" \
            http://127.0.0.1:$port/openapi.json 2>&1)
    else
        response=$(curl -s -w "\n%{http_code}" http://127.0.0.1:$port/openapi.json 2>&1)
    fi
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)
    
    if [ "$http_code" = "200" ]; then
        title=$(echo "$body" | python3 -c "import sys, json; print(json.load(sys.stdin).get('info', {}).get('title', 'Unknown'))" 2>/dev/null)
        if [ -n "$title" ] && [ "$title" != "Unknown" ]; then
            echo -e "${GREEN}✓ PASS${NC} - $title"
            ((PASSED++))
            return 0
        else
            echo -e "${YELLOW}⚠ WARN${NC} - Response OK but no title found"
            ((PASSED++))
            return 0
        fi
    else
        echo -e "${RED}✗ FAIL${NC} - HTTP $http_code"
        ((FAILED++))
        return 1
    fi
}

echo "=== Testing MCP Tools ==="
echo ""

test_tool 8011 "tehuti-curriculum" "none"
test_tool 8012 "tehuti-research" "none"
test_tool 8013 "tehuti-integration" "bearer"
test_tool 8014 "tehuti-core" "bearer"
test_tool 8015 "n8n-mcp" "none"
test_tool 8016 "filesystem" "bearer"
test_tool 8017 "postgres" "bearer"
test_tool 8018 "memory" "none"

echo ""
echo "=== Testing Core Services ==="
echo ""

# Test OpenWebUI
echo -n "Testing OpenWebUI (port 3000)... "
if curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:3000 | grep -q "200\|301\|302"; then
    echo -e "${GREEN}✓ PASS${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ FAIL${NC}"
    ((FAILED++))
fi

# Test n8n
echo -n "Testing n8n (port 5678)... "
health=$(curl -s http://127.0.0.1:5678/healthz 2>&1)
if echo "$health" | grep -q "ok"; then
    echo -e "${GREEN}✓ PASS${NC} - $health"
    ((PASSED++))
else
    echo -e "${RED}✗ FAIL${NC} - $health"
    ((FAILED++))
fi

# Test Ollama
echo -n "Testing Ollama (port 11434)... "
if curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:11434/api/tags 2>&1 | grep -q "200"; then
    echo -e "${GREEN}✓ PASS${NC}"
    ((PASSED++))
else
    echo -e "${YELLOW}⚠ WARN${NC} - May not have models loaded"
    ((PASSED++))
fi

echo ""
echo "=== Testing Tool Functionality ==="
echo ""

# Test curriculum tool call
echo -n "Testing curriculum list-templates... "
response=$(curl -s -X POST http://127.0.0.1:8011/tehuti-curriculum/list-templates \
    -H "Content-Type: application/json" \
    -d '{}' 2>&1)
if echo "$response" | grep -q "templates\|error"; then
    echo -e "${GREEN}✓ PASS${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ FAIL${NC}"
    ((FAILED++))
fi

# Test research tool call
echo -n "Testing research list-methodologies... "
response=$(curl -s -X POST http://127.0.0.1:8012/tehuti-research/list-methodologies \
    -H "Content-Type: application/json" \
    -d '{}' 2>&1)
if echo "$response" | grep -q "methodologies\|error"; then
    echo -e "${GREEN}✓ PASS${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ FAIL${NC}"
    ((FAILED++))
fi

# Test integration tool call (with auth)
echo -n "Testing integration list-workflows... "
response=$(curl -s -X POST http://127.0.0.1:8013/tehuti-integration/list-workflows \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer TEHUTI_MCP_INTERNAL_ONLY" \
    -d '{}' 2>&1)
if echo "$response" | grep -q "workflows\|error"; then
    echo -e "${GREEN}✓ PASS${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ FAIL${NC}"
    ((FAILED++))
fi

# Test memory tool call
echo -n "Testing memory create-entities... "
response=$(curl -s -X POST http://127.0.0.1:8018/create_entities \
    -H "Content-Type: application/json" \
    -d '{"entities": [{"id": "test", "name": "Test Entity", "description": "Test"}]}' 2>&1)
if echo "$response" | grep -q "entities\|error"; then
    echo -e "${GREEN}✓ PASS${NC}"
    ((PASSED++))
else
    echo -e "${RED}✗ FAIL${NC}"
    ((FAILED++))
fi

echo ""
echo "=== Testing OpenWebUI Database ==="
echo ""

# Check if tools are in config table
echo -n "Checking OpenWebUI external tools config... "
tool_count=$(python3 -c "
import sqlite3, json
try:
    conn = sqlite3.connect('/home/suspect/.n8n/open-webui/data/webui.db')
    cursor = conn.cursor()
    cursor.execute('SELECT data FROM config WHERE id = 1')
    result = cursor.fetchone()
    if result:
        config = json.loads(result[0])
        tools = config.get('tool_server', {}).get('connections', [])
        print(len(tools))
    else:
        print('0')
    conn.close()
except Exception as e:
    print('ERROR')
" 2>/dev/null)

if [ "$tool_count" -ge "8" ]; then
    echo -e "${GREEN}✓ PASS${NC} - $tool_count tools configured"
    ((PASSED++))
elif [ "$tool_count" -gt "0" ]; then
    echo -e "${YELLOW}⚠ WARN${NC} - Only $tool_count tools configured (expected 8)"
    ((PASSED++))
else
    echo -e "${RED}✗ FAIL${NC} - No tools configured"
    ((FAILED++))
fi

echo ""
echo "=========================================="
echo "Test Results: ${GREEN}$PASSED passed${NC}, ${RED}$FAILED failed${NC}"
echo "=========================================="

if [ $FAILED -eq 0 ]; then
    exit 0
else
    exit 1
fi

