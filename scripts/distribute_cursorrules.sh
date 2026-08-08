#!/bin/bash
# Distribute .cursorrules to all laptops
# Maat: Order - Consistent system prompts across all machines

set -e

WORKSPACE_ROOT="/home/suspect/.n8n"
CURSORRULES_FILE="$WORKSPACE_ROOT/.cursorrules"

# Laptop IPs (update as needed)
declare -A LAPTOPS=(
    ["imhotep"]="192.168.4.25"
    ["macdaddy"]="192.168.4.36"
    ["imhotepjr"]="192.168.4.81"
)

echo "📊 Maat Audit: Distributing .cursorrules to all laptops"
echo "========================================================="
echo ""

# Check if .cursorrules exists
if [ ! -f "$CURSORRULES_FILE" ]; then
    echo "❌ Error: .cursorrules not found at $CURSORRULES_FILE"
    exit 1
fi

echo "✅ Found .cursorrules at: $CURSORRULES_FILE"
echo ""

# Distribute to each laptop
for laptop_name in "${!LAPTOPS[@]}"; do
    ip="${LAPTOPS[$laptop_name]}"
    echo "📤 Distributing to $laptop_name ($ip)..."
    
    # Use scp to copy (will prompt for password)
    scp "$CURSORRULES_FILE" "suspect@$ip:$WORKSPACE_ROOT/.cursorrules" || {
        echo "⚠️  Failed to copy to $laptop_name - may need manual copy"
        echo "   Command: scp $CURSORRULES_FILE suspect@$ip:$WORKSPACE_ROOT/.cursorrules"
    }
done

echo ""
echo "✅ Distribution complete!"
echo ""
echo "📋 Verification:"
echo "   On each laptop, verify:"
echo "   - File exists: $WORKSPACE_ROOT/.cursorrules"
echo "   - Cursor AI picks it up automatically"
echo "   - Works from any project subdirectory"
echo ""

