#!/bin/bash
# Maat Cleanup Script
# Removes temporary files, Python cache, and organizes system for continued building

set -e

WORKSPACE_ROOT="/home/suspect/.n8n"
CLEANUP_LOG="$WORKSPACE_ROOT/logs/maat-cleanup-$(date +%Y%m%d-%H%M%S).log"
ARCHIVE_DIR="$WORKSPACE_ROOT/backups/cleanup-archive-$(date +%Y%m%d)"

mkdir -p "$(dirname "$CLEANUP_LOG")"
mkdir -p "$ARCHIVE_DIR"

echo "🧹 Maat Cleanup Script"
echo "======================"
echo "Started: $(date)"
echo "Log: $CLEANUP_LOG"
echo ""

log_action() {
    echo "[$(date +%H:%M:%S)] $1" | tee -a "$CLEANUP_LOG"
}

# Function to safely remove files with backup
safe_remove() {
    local pattern="$1"
    local description="$2"
    local count=$(find "$WORKSPACE_ROOT" -type f -name "$pattern" 2>/dev/null | wc -l)
    
    if [ "$count" -gt 0 ]; then
        log_action "Removing $count $description files..."
        find "$WORKSPACE_ROOT" -type f -name "$pattern" -print0 2>/dev/null | \
            xargs -0 rm -f 2>/dev/null || true
        log_action "✅ Removed $count $description files"
    else
        log_action "No $description files found"
    fi
}

# Function to archive files before removal
archive_and_remove() {
    local pattern="$1"
    local description="$2"
    local archive_subdir="$ARCHIVE_DIR/$3"
    
    mkdir -p "$archive_subdir"
    local count=$(find "$WORKSPACE_ROOT" -type f -name "$pattern" 2>/dev/null | wc -l)
    
    if [ "$count" -gt 0 ]; then
        log_action "Archiving $count $description files to $archive_subdir..."
        find "$WORKSPACE_ROOT" -type f -name "$pattern" -print0 2>/dev/null | \
            xargs -0 -I {} sh -c 'mv "{}" "$1/$(basename "{}")-$(date +%s)"' _ "$archive_subdir" 2>/dev/null || true
        log_action "✅ Archived $count $description files"
    fi
}

# 1. Remove temporary files
log_action "=== Phase 1: Temporary Files ==="
safe_remove "*.tmp" "temporary"
safe_remove "*.bak" "backup"
safe_remove "*~" "backup (~)"
safe_remove "*.swp" "swap"
safe_remove "*.swo" "swap"

# 2. Clean Python cache
log_action ""
log_action "=== Phase 2: Python Cache ==="
PYCACHE_COUNT=$(find "$WORKSPACE_ROOT" -type d -name "__pycache__" 2>/dev/null | wc -l)
if [ "$PYCACHE_COUNT" -gt 0 ]; then
    log_action "Removing $PYCACHE_COUNT __pycache__ directories..."
    find "$WORKSPACE_ROOT" -type d -name "__pycache__" -print0 2>/dev/null | \
        xargs -0 rm -rf 2>/dev/null || true
    log_action "✅ Removed $PYCACHE_COUNT __pycache__ directories"
else
    log_action "No __pycache__ directories found"
fi

# Remove .pyc files
safe_remove "*.pyc" "Python compiled"
safe_remove "*.pyo" "Python optimized"

# Remove pytest cache
PYTEST_CACHE_COUNT=$(find "$WORKSPACE_ROOT" -type d -name ".pytest_cache" 2>/dev/null | wc -l)
if [ "$PYTEST_CACHE_COUNT" -gt 0 ]; then
    log_action "Removing $PYTEST_CACHE_COUNT .pytest_cache directories..."
    find "$WORKSPACE_ROOT" -type d -name ".pytest_cache" -print0 2>/dev/null | \
        xargs -0 rm -rf 2>/dev/null || true
    log_action "✅ Removed $PYTEST_CACHE_CACHE_COUNT .pytest_cache directories"
fi

# 3. Archive old log files
log_action ""
log_action "=== Phase 3: Log Files ==="
LOG_COUNT=$(find "$WORKSPACE_ROOT" -maxdepth 1 -type f -name "*.log" 2>/dev/null | wc -l)
if [ "$LOG_COUNT" -gt 0 ]; then
    log_action "Found $LOG_COUNT log files in root, archiving..."
    mkdir -p "$ARCHIVE_DIR/logs"
    find "$WORKSPACE_ROOT" -maxdepth 1 -type f -name "*.log" -exec mv {} "$ARCHIVE_DIR/logs/" \; 2>/dev/null || true
    log_action "✅ Archived $LOG_COUNT log files"
else
    log_action "No log files found in root"
fi

# 4. Remove empty directories
log_action ""
log_action "=== Phase 4: Empty Directories ==="
EMPTY_COUNT=$(find "$WORKSPACE_ROOT" -type d -empty 2>/dev/null | wc -l)
if [ "$EMPTY_COUNT" -gt 0 ]; then
    log_action "Found $EMPTY_COUNT empty directories (keeping for structure)"
    # Don't remove empty dirs - they may be needed for structure
fi

# 5. Clean node_modules .turbo cache
log_action ""
log_action "=== Phase 5: Node.js Cache ==="
TURBO_LOG_COUNT=$(find "$WORKSPACE_ROOT" -type f -path "*/.turbo/*.log" 2>/dev/null | wc -l)
if [ "$TURBO_LOG_COUNT" -gt 0 ]; then
    log_action "Removing $TURBO_LOG_COUNT Turbo build logs..."
    find "$WORKSPACE_ROOT" -type f -path "*/.turbo/*.log" -delete 2>/dev/null || true
    log_action "✅ Removed Turbo logs"
fi

# 6. Summary
log_action ""
log_action "=== Cleanup Summary ==="
log_action "Archive location: $ARCHIVE_DIR"
log_action "Cleanup log: $CLEANUP_LOG"
log_action ""
log_action "✅ Cleanup complete!"
log_action "Finished: $(date)"

echo ""
echo "📊 Cleanup Summary:"
echo "   Archive: $ARCHIVE_DIR"
echo "   Log: $CLEANUP_LOG"
echo ""

