#!/bin/bash
# Distribute workspace and project files to all workstations
# Maat: Order - Consistent setup across all machines

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Workspace root
WORKSPACE_ROOT="/home/suspect/.n8n"
PROJECT_ROOT="$WORKSPACE_ROOT/maatlangchain"

# Laptop IPs (update these if needed)
declare -A LAPTOPS=(
    ["Imhotep"]="192.168.4.25"
    ["MacDaddy"]="192.168.4.36"
    ["Imhotepjr"]="192.168.4.81"
)

# Remote user
REMOTE_USER="suspect"

echo "🚀 Maat Workspace File Distribution"
echo "===================================="
echo ""

# Check if source files exist
echo "📋 Checking source files..."

# Workspace root files
WORKSPACE_FILES=(
    ".cursorrules"
    "opencode.json"
)

# Project root files
PROJECT_FILES=(
    "AGENTS.md"
    "README.md"
    "PROMPT-NEXT-ACTION.md"
    "opencode.json"
)

# Verify source files exist
echo "  Workspace root files:"
for file in "${WORKSPACE_FILES[@]}"; do
    if [ -f "$WORKSPACE_ROOT/$file" ]; then
        echo "    ✅ $file"
    else
        echo "    ⚠️  $file (optional, skipping)"
    fi
done

echo "  Project root files:"
for file in "${PROJECT_FILES[@]}"; do
    if [ -f "$PROJECT_ROOT/$file" ]; then
        echo "    ✅ $file"
    else
        echo "    ⚠️  $file (optional, skipping)"
    fi
done

echo ""

# Function to copy files to a laptop
copy_to_laptop() {
    local laptop_name=$1
    local laptop_ip=$2
    local success=true
    
    echo "📤 Distributing to $laptop_name ($laptop_ip)..."
    
    # Create remote directories if they don't exist
    ssh "$REMOTE_USER@$laptop_ip" "mkdir -p $WORKSPACE_ROOT $PROJECT_ROOT" 2>/dev/null || {
        echo "    ${RED}❌ Failed to create directories${NC}"
        return 1
    }
    
    # Copy workspace root files
    echo "  Copying workspace root files..."
    for file in "${WORKSPACE_FILES[@]}"; do
        if [ -f "$WORKSPACE_ROOT/$file" ]; then
            if scp "$WORKSPACE_ROOT/$file" "$REMOTE_USER@$laptop_ip:$WORKSPACE_ROOT/$file" 2>/dev/null; then
                echo "    ${GREEN}✅ $file${NC}"
            else
                echo "    ${RED}❌ $file (failed)${NC}"
                success=false
            fi
        fi
    done
    
    # Copy project root files
    echo "  Copying project root files..."
    for file in "${PROJECT_FILES[@]}"; do
        if [ -f "$PROJECT_ROOT/$file" ]; then
            if scp "$PROJECT_ROOT/$file" "$REMOTE_USER@$laptop_ip:$PROJECT_ROOT/$file" 2>/dev/null; then
                echo "    ${GREEN}✅ $file${NC}"
            else
                echo "    ${RED}❌ $file (failed)${NC}"
                success=false
            fi
        fi
    done
    
    # Verify files on remote
    echo "  Verifying files on $laptop_name..."
    ssh "$REMOTE_USER@$laptop_ip" "ls -la $WORKSPACE_ROOT/.cursorrules $PROJECT_ROOT/AGENTS.md" 2>/dev/null && {
        echo "    ${GREEN}✅ Verification passed${NC}"
    } || {
        echo "    ${YELLOW}⚠️  Verification incomplete (may need manual check)${NC}"
    }
    
    if [ "$success" = true ]; then
        echo "  ${GREEN}✅ $laptop_name: Distribution complete${NC}"
    else
        echo "  ${YELLOW}⚠️  $laptop_name: Distribution completed with warnings${NC}"
    fi
    
    echo ""
}

# Distribute to all laptops
for laptop_name in "${!LAPTOPS[@]}"; do
    laptop_ip="${LAPTOPS[$laptop_name]}"
    
    # Test connection first
    if ping -c 1 -W 2 "$laptop_ip" >/dev/null 2>&1; then
        copy_to_laptop "$laptop_name" "$laptop_ip"
    else
        echo "${YELLOW}⚠️  $laptop_name ($laptop_ip): Not reachable, skipping${NC}"
        echo ""
    fi
done

echo "✅ Distribution complete!"
echo ""
echo "📋 Next steps on each workstation:"
echo "  1. Verify files exist:"
echo "     ls -la $WORKSPACE_ROOT/.cursorrules"
echo "     ls -la $PROJECT_ROOT/AGENTS.md"
echo ""
echo "  2. Test Cursor AI:"
echo "     - Open Cursor in any project subdirectory"
echo "     - Cursor should auto-detect .cursorrules"
echo "     - Agent ID should be unique (e.g., cursor_imhotep)"
echo ""
echo "  3. Test auto-setup:"
echo "     - Agent should read AGENTS.md automatically"
echo "     - Should connect to gitMaat (PostgreSQL)"
echo ""

