#!/bin/bash
# Comprehensive audit for all crush.json files and references
# Run this on each laptop to find confusing files

echo "🔍 MaatLangChain - Crush.json Audit"
echo "===================================="
echo ""

PROJECT_ROOT="$HOME/.n8n/maatlangchain"
FOUND_ISSUES=0

# 1. Find all crush.json files in project root
echo "1. Searching for crush.json files in project root..."
find "$PROJECT_ROOT" -maxdepth 1 -name "crush.json" -type f 2>/dev/null | while read file; do
    echo "   ❌ FOUND: $file"
    echo "      ⚠️  This file confuses agents - should be removed!"
    FOUND_ISSUES=$((FOUND_ISSUES + 1))
done

# 2. Find crush.json in subdirectories (excluding node_modules, __pycache__)
echo ""
echo "2. Searching for crush.json in subdirectories..."
find "$PROJECT_ROOT" -name "crush.json" -type f \
    -not -path "*/node_modules/*" \
    -not -path "*/__pycache__/*" \
    -not -path "*/.git/*" \
    -not -path "*/venv/*" \
    -not -path "*/env/*" \
    2>/dev/null | while read file; do
    echo "   ❌ FOUND: $file"
    FOUND_ISSUES=$((FOUND_ISSUES + 1))
done

# 3. Find .crush directories
echo ""
echo "3. Searching for .crush directories..."
find "$PROJECT_ROOT" -type d -name ".crush" \
    -not -path "*/node_modules/*" \
    -not -path "*/.git/*" \
    2>/dev/null | while read dir; do
    echo "   ❌ FOUND: $dir"
    FOUND_ISSUES=$((FOUND_ISSUES + 1))
done

# 4. Check config directory
echo ""
echo "4. Checking ~/.config/crush..."
if [ -d "$HOME/.config/crush" ]; then
    echo "   ❌ FOUND: $HOME/.config/crush"
    echo "      ⚠️  This directory should be removed"
    FOUND_ISSUES=$((FOUND_ISSUES + 1))
else
    echo "   ✅ Not found (already cleaned)"
fi

# 5. Check for old test file
echo ""
echo "5. Checking for old test file..."
if [ -f "$PROJECT_ROOT/test_crush_integration.py" ]; then
    echo "   ❌ FOUND: test_crush_integration.py"
    echo "      ⚠️  Should be renamed to test_maat_memory_integration.py"
    FOUND_ISSUES=$((FOUND_ISSUES + 1))
else
    echo "   ✅ Not found (already renamed)"
fi

# 6. Check for references in code (excluding documentation)
echo ""
echo "6. Checking for 'crush' references in code files..."
CODE_REFS=$(grep -r "crush\|Crush\|CRUSH" "$PROJECT_ROOT" \
    --exclude-dir=node_modules \
    --exclude-dir=__pycache__ \
    --exclude-dir=.git \
    --exclude="*.pyc" \
    --exclude="*.json.gz" \
    --include="*.py" \
    --include="*.sh" \
    2>/dev/null | \
    grep -v "CRUSH-TO-MAAT-SYNC.md" | \
    grep -v "sync_crush_to_maat.sh" | \
    grep -v "CLEANUP-SUMMARY.md" | \
    grep -v "chunks.json" | \
    wc -l)

if [ "$CODE_REFS" -gt 0 ]; then
    echo "   ⚠️  Found $CODE_REFS references (excluding docs)"
    echo "      Run cleanup script to fix"
    FOUND_ISSUES=$((FOUND_ISSUES + CODE_REFS))
else
    echo "   ✅ No problematic references found"
fi

# Summary
echo ""
echo "===================================="
if [ "$FOUND_ISSUES" -eq 0 ]; then
    echo "✅ Audit complete - No issues found!"
    echo ""
    echo "💡 Your workspace is clean. Agents won't be confused by crush.json files."
else
    echo "⚠️  Audit complete - Found $FOUND_ISSUES issue(s)"
    echo ""
    echo "🔧 Run cleanup script to fix:"
    echo "   ./scripts/cleanup_crush_files.sh"
fi

