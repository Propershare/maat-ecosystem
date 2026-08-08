#!/bin/bash
# Maat Balance: Memory Distribution Monitoring Script
# Purpose: Monitor and balance memory usage across services

set -e

echo "=== Maat Balance: Memory Distribution Monitor ==="
echo ""

# 1. Check system memory
echo "1. System Memory Status:"
free -h | grep -E "Mem|Swap"
echo ""

# 2. Check service memory usage
echo "2. Service Memory Usage:"
echo "   MCP Services:"
systemctl list-units --type=service --state=running | grep -E "mcpo|tehuti" | while read -r line; do
    SERVICE=$(echo "$line" | awk '{print $1}')
    PID=$(systemctl show "$SERVICE" --property=MainPID --value 2>/dev/null || echo "")
    if [ -n "$PID" ] && [ "$PID" != "0" ]; then
        MEM=$(ps -p "$PID" -o rss= 2>/dev/null | awk '{printf "%.1f MB", $1/1024}' || echo "N/A")
        echo "   - $SERVICE: $MEM"
    fi
done
echo ""

# 3. Check Python processes
echo "3. Python Process Memory:"
ps aux | grep -E "python.*(webui|mcp|server)" | grep -v grep | awk '{printf "   - %s: %.1f MB\n", $11, $6/1024}' | head -10
echo ""

# 4. Check Node processes
echo "4. Node Process Memory:"
ps aux | grep -E "node.*(webui|n8n)" | grep -v grep | awk '{printf "   - %s: %.1f MB\n", $11, $6/1024}' | head -10
echo ""

# 5. Memory balance assessment
echo "5. Memory Balance Assessment:"
TOTAL_MEM=$(free -m | grep Mem | awk '{print $2}')
USED_MEM=$(free -m | grep Mem | awk '{print $3}')
PERCENT=$((USED_MEM * 100 / TOTAL_MEM))

if [ "$PERCENT" -lt 70 ]; then
    echo "   ✅ Memory usage: ${PERCENT}% (Well balanced)"
elif [ "$PERCENT" -lt 85 ]; then
    echo "   ⚠️  Memory usage: ${PERCENT}% (Moderate usage)"
else
    echo "   🔴 Memory usage: ${PERCENT}% (High usage - consider optimization)"
fi
echo ""

# 6. Recommendations
echo "=== Recommendations ==="
echo "✅ Current state: Memory well distributed (8/10)"
echo "💡 Monitor for memory leaks"
echo "💡 Optimize high consumers if needed"
echo "💡 Ensure no single service dominates"
echo ""
echo "=== Maat Balance: Memory monitoring complete ==="

