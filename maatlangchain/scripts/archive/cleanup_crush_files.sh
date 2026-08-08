#!/bin/bash
# Comprehensive cleanup - removes all crush.json files and references
# Run this on each laptop to clean up confusing files

echo "🧹 MaatLangChain - Crush.json Cleanup"
echo "====================================="
echo ""

PROJECT_ROOT="$HOME/.n8n/maatlangchain"
BACKUP_DIR="$PROJECT_ROOT/.cleanup_backup_$(date +%Y%m%d_%H%M%S)"
CLEANED=0

# Create backup directory
mkdir -p "$BACKUP_DIR"
echo "📦 Backup location: $BACKUP_DIR"
echo ""

# 1. Remove crush.json from project root
echo "1. Removing crush.json from project root..."
find "$PROJECT_ROOT" -maxdepth 1 -name "crush.json" -type f 2>/dev/null | while read file; do
    echo "   🗑️  Removing: $file"
    cp "$file" "$BACKUP_DIR/" 2>/dev/null
    rm -f "$file"
    CLEANED=$((CLEANED + 1))
done

# 2. Remove crush.json from subdirectories
echo ""
echo "2. Removing crush.json from subdirectories..."
find "$PROJECT_ROOT" -name "crush.json" -type f \
    -not -path "*/node_modules/*" \
    -not -path "*/__pycache__/*" \
    -not -path "*/.git/*" \
    -not -path "*/venv/*" \
    -not -path "*/env/*" \
    2>/dev/null | while read file; do
    echo "   🗑️  Removing: $file"
    cp "$file" "$BACKUP_DIR/" 2>/dev/null
    rm -f "$file"
    CLEANED=$((CLEANED + 1))
done

# 3. Remove .crush directories
echo ""
echo "3. Removing .crush directories..."
find "$PROJECT_ROOT" -type d -name ".crush" \
    -not -path "*/node_modules/*" \
    -not -path "*/.git/*" \
    2>/dev/null | while read dir; do
    echo "   🗑️  Removing: $dir"
    cp -r "$dir" "$BACKUP_DIR/" 2>/dev/null
    rm -rf "$dir"
    CLEANED=$((CLEANED + 1))
done

# 4. Remove config directory
echo ""
echo "4. Removing ~/.config/crush..."
if [ -d "$HOME/.config/crush" ]; then
    echo "   🗑️  Removing: $HOME/.config/crush"
    cp -r "$HOME/.config/crush" "$BACKUP_DIR/" 2>/dev/null
    rm -rf "$HOME/.config/crush"
    CLEANED=$((CLEANED + 1))
else
    echo "   ✅ Already removed"
fi

# 5. Rename old test file
echo ""
echo "5. Renaming old test file..."
if [ -f "$PROJECT_ROOT/test_crush_integration.py" ]; then
    echo "   📝 Renaming test_crush_integration.py..."
    cp "$PROJECT_ROOT/test_crush_integration.py" "$BACKUP_DIR/"
    mv "$PROJECT_ROOT/test_crush_integration.py" \
       "$PROJECT_ROOT/test_maat_memory_integration.py"
    CLEANED=$((CLEANED + 1))
else
    echo "   ✅ Already renamed"
fi

# 6. Create .gitignore entry to prevent future crush.json files
echo ""
echo "6. Updating .gitignore to prevent crush.json..."
if [ -f "$PROJECT_ROOT/.gitignore" ]; then
    if ! grep -q "crush.json" "$PROJECT_ROOT/.gitignore"; then
        echo "" >> "$PROJECT_ROOT/.gitignore"
        echo "# Prevent crush.json files (use Maat Memory instead)" >> "$PROJECT_ROOT/.gitignore"
        echo "crush.json" >> "$PROJECT_ROOT/.gitignore"
        echo ".crush/" >> "$PROJECT_ROOT/.gitignore"
        echo "   ✅ Added to .gitignore"
    else
        echo "   ✅ Already in .gitignore"
    fi
else
    echo "crush.json" > "$PROJECT_ROOT/.gitignore"
    echo ".crush/" >> "$PROJECT_ROOT/.gitignore"
    echo "   ✅ Created .gitignore"
fi

# Summary
echo ""
echo "===================================="
echo "✅ Cleanup complete!"
echo ""
echo "📊 Summary:"
echo "   - Files/directories removed: $CLEANED"
echo "   - Backup location: $BACKUP_DIR"
echo ""
echo "💡 Agents will no longer be confused by crush.json files."
echo "   All memory operations use Maat Memory (PostgreSQL)."

