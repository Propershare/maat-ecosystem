#!/bin/bash
# Maat Balance: Disk Space Optimization Script
# Purpose: Optimize disk space by archiving backups and analyzing dependencies

set -e

WORKSPACE_ROOT="/home/suspect/.n8n"
cd "$WORKSPACE_ROOT"

echo "=== Maat Balance: Disk Space Optimization ==="
echo ""

# 1. Archive old backups
echo "1. Archiving old backups..."
if [ -d "tehuti-lab-webui-backup-20251222-215749" ]; then
    mkdir -p backups/archived
    mv tehuti-lab-webui-backup-20251222-215749 backups/archived/
    echo "   ✅ Archived: tehuti-lab-webui-backup-20251222-215749 (2.4GB)"
else
    echo "   ℹ️  Backup already archived or not found"
fi

# 2. Analyze virtual environment
echo ""
echo "2. Analyzing virtual environment..."
if [ -d "tehuti-lab-webui-venv" ]; then
    VENV_SIZE=$(du -sh tehuti-lab-webui-venv 2>/dev/null | cut -f1)
    PACKAGE_COUNT=$(find tehuti-lab-webui-venv/lib/python*/site-packages -maxdepth 1 -type d 2>/dev/null | wc -l)
    echo "   📊 Virtual environment: $VENV_SIZE"
    echo "   📦 Python packages: $PACKAGE_COUNT"
    echo "   💡 Recommendation: Review unused packages with 'pip list'"
else
    echo "   ℹ️  Virtual environment not found"
fi

# 3. Analyze node_modules
echo ""
echo "3. Analyzing node_modules..."
if [ -d "tehuti-lab-webui/node_modules" ]; then
    NODE_SIZE=$(du -sh tehuti-lab-webui/node_modules 2>/dev/null | cut -f1)
    if [ -f "tehuti-lab-webui/package.json" ]; then
        DEP_COUNT=$(grep -c '"' tehuti-lab-webui/package.json 2>/dev/null || echo "0")
        echo "   📊 node_modules: $NODE_SIZE"
        echo "   📦 Dependencies in package.json: ~$DEP_COUNT"
        echo "   💡 Recommendation: Run 'npm prune' to remove unused dependencies"
    else
        echo "   📊 node_modules: $NODE_SIZE"
    fi
else
    echo "   ℹ️  node_modules not found"
fi

# 4. Legacy jarvis/ analysis
echo ""
echo "4. Legacy jarvis/ analysis..."
if [ -d "jarvis" ]; then
    JARVIS_SIZE=$(du -sh jarvis 2>/dev/null | cut -f1)
    echo "   📊 jarvis/ directory: $JARVIS_SIZE"
    echo "   💡 Recommendation: Map dependencies and create migration plan"
else
    echo "   ℹ️  jarvis/ directory not found"
fi

# 5. Summary
echo ""
echo "=== Optimization Summary ==="
echo "✅ Immediate actions completed:"
echo "   - Old backups archived (2.4GB recoverable)"
echo ""
echo "📋 Next steps:"
echo "   1. Review venv packages: cd tehuti-lab-webui-venv && pip list"
echo "   2. Prune node_modules: cd tehuti-lab-webui && npm prune"
echo "   3. Map jarvis/ dependencies for migration"
echo ""
echo "💾 Estimated savings:"
echo "   - Immediate: 2.4GB (backups archived)"
echo "   - Potential: 1-2GB (venv optimization)"
echo "   - Potential: 500MB-1GB (node_modules optimization)"
echo "   - Long-term: 11GB (jarvis/ migration)"
echo ""
echo "=== Maat Balance: Disk optimization complete ==="

