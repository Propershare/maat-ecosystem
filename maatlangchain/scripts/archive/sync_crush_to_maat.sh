#!/bin/bash
# Script to sync "crush" to "maat_memory" renaming across all systems
# Run this on each laptop (Imhotep, MacDaddy, Imhotepjr)

echo "🔄 Syncing Crush → Maat Memory renaming..."
echo ""

# 1. Remove old crush config directory
if [ -d "$HOME/.config/crush" ]; then
    echo "🗑️  Removing old crush config directory..."
    rm -rf "$HOME/.config/crush"
    echo "✅ Removed $HOME/.config/crush"
fi

# 2. Rename test file if it exists
if [ -f "$HOME/.n8n/maatlangchain/test_crush_integration.py" ]; then
    echo "📝 Renaming test file..."
    mv "$HOME/.n8n/maatlangchain/test_crush_integration.py" \
       "$HOME/.n8n/maatlangchain/test_maat_memory_integration.py"
    echo "✅ Renamed test file"
fi

# 3. Update code references (if files exist)
if [ -f "$HOME/.n8n/maatlangchain/api/main_backup_rag.py" ]; then
    echo "📝 Updating main_backup_rag.py..."
    sed -i 's/crush = get_maat_logger()/maat_memory = get_maat_logger()/g' \
        "$HOME/.n8n/maatlangchain/api/main_backup_rag.py"
    sed -i 's/Log to Crush memory/Log to Maat Memory/g' \
        "$HOME/.n8n/maatlangchain/api/main_backup_rag.py"
    echo "✅ Updated main_backup_rag.py"
fi

if [ -f "$HOME/.n8n/maatlangchain/api/main_original.py" ]; then
    echo "📝 Updating main_original.py..."
    sed -i 's/crush = get_crush_memory()/maat_memory = get_maat_memory()/g' \
        "$HOME/.n8n/maatlangchain/api/main_original.py"
    sed -i 's/get_crush_logger/get_maat_memory_logger/g' \
        "$HOME/.n8n/maatlangchain/api/main_original.py"
    sed -i 's/CRUSH_AVAILABLE/MAAT_MEMORY_AVAILABLE/g' \
        "$HOME/.n8n/maatlangchain/api/main_original.py"
    sed -i 's/Crush memory/Maat Memory/g' \
        "$HOME/.n8n/maatlangchain/api/main_original.py"
    sed -i 's/Log error to Crush/Log error to Maat Memory/g' \
        "$HOME/.n8n/maatlangchain/api/main_original.py"
    echo "✅ Updated main_original.py"
fi

echo ""
echo "✅ Crush → Maat Memory sync complete!"
echo ""
echo "📋 Summary:"
echo "   - Removed ~/.config/crush directory"
echo "   - Renamed test file"
echo "   - Updated code references"
echo ""
echo "💡 Note: This script only updates local files."
echo "   The main codebase already uses 'Maat Memory' - this just cleans up old references."

