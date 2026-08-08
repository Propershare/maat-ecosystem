# Crush → Maat Memory Sync Guide

## Overview

All "crush" references have been renamed to "maat_memory" to align with Maat principles. This document explains what was changed and how to sync to all systems.

## Changes Made

### 1. Config Directory
- **Removed:** `~/.config/crush/` (empty directory)
- **Status:** ✅ Removed on main server

### 2. Test File
- **Renamed:** `test_crush_integration.py` → `test_maat_memory_integration.py`
- **Updated:** All function names, comments, and variable names
- **Status:** ✅ Renamed and updated on main server

### 3. Code Files
- **`api/main_backup_rag.py`**: Updated comments and variable names
- **`api/main_original.py`**: Updated imports, comments, and variable names
- **Status:** ✅ Updated on main server

## Syncing to All Systems

### Option 1: Automated Script (Recommended)

Run this script on each laptop:

```bash
# On each laptop (Imhotep, MacDaddy, Imhotepjr)
cd ~/.n8n/maatlangchain
./scripts/sync_crush_to_maat.sh
```

**Or copy the script first:**
```bash
# From main server, copy script to shared location
scp scripts/sync_crush_to_maat.sh suspect@<laptop-ip>:~/.n8n/maatlangchain/scripts/

# Then run on each laptop
ssh suspect@<laptop-ip> "cd ~/.n8n/maatlangchain && ./scripts/sync_crush_to_maat.sh"
```

### Option 2: Manual Steps

On each laptop, run:

```bash
# 1. Remove old config directory
rm -rf ~/.config/crush

# 2. Rename test file (if exists)
mv ~/.n8n/maatlangchain/test_crush_integration.py \
   ~/.n8n/maatlangchain/test_maat_memory_integration.py

# 3. Update code files (if they exist)
# The main codebase already uses Maat Memory, so this is just cleanup
```

## What's Already Done

✅ **Main Server (192.168.4.21):**
- Config directory removed
- Test file renamed and updated
- Code files updated
- Script created for syncing

## What Needs to Be Done

📋 **On Each Laptop:**
- Run sync script OR follow manual steps
- Verify no "crush" references remain

## Verification

After syncing, verify on each system:

```bash
# Check for any remaining "crush" references
grep -r "crush\|Crush\|CRUSH" ~/.n8n/maatlangchain --exclude-dir=node_modules --exclude-dir=__pycache__ | grep -v ".pyc" | head -20
```

Should return minimal results (only in documentation or old backup files).

## Important Notes

1. **Active Codebase**: The main codebase already uses "Maat Memory" - these changes are just cleanup of old references
2. **PostgreSQL Backend**: Maat Memory uses PostgreSQL, not file-based storage, so no data migration needed
3. **Backward Compatibility**: Old "crush" references in backup files are harmless but should be cleaned up

## Systems to Update

- ✅ **Main Server (192.168.4.21)** - Already done
- ⏳ **Imhotep (192.168.4.25)** - Run sync script
- ⏳ **MacDaddy (192.168.4.36)** - Run sync script  
- ⏳ **Imhotepjr (192.168.4.81)** - Run sync script

---

**Last Updated:** 2025-12-21
**Status:** Main server complete, laptops pending sync

