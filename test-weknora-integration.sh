#!/bin/bash
# Quick test script for WeKnora Integration (Phase 1 & 2)

echo "=== WeKnora Integration Test Script ==="
echo ""

# Check if backend is running
echo "1. Checking backend..."
if curl -s http://localhost:8080/health > /dev/null 2>&1; then
    echo "   ✅ Backend is running"
else
    echo "   ❌ Backend is not running on port 8080"
    echo "   Start it with: cd /home/suspect/.n8n/tehuti-lab-webui && python3 -m uvicorn open_webui.main:app --reload"
fi

# Check if frontend is running
echo ""
echo "2. Checking frontend..."
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo "   ✅ Frontend is running"
else
    echo "   ❌ Frontend is not running on port 3000"
    echo "   Start it with: cd /home/suspect/.n8n/tehuti-lab-webui && npm run dev"
fi

# Check if tehuti-core MCP is running
echo ""
echo "3. Checking Tehuti Core MCP server..."
if systemctl is-active --quiet mcpo-tehuti-core 2>/dev/null || systemctl is-active --quiet tehuti-core-mcp.service 2>/dev/null; then
    echo "   ✅ Tehuti Core MCP service is running"
elif curl -s http://localhost:8014/health > /dev/null 2>&1; then
    echo "   ✅ Tehuti Core MCP is running on port 8014"
else
    echo "   ⚠️  Tehuti Core MCP may not be running"
    echo "   Check with: sudo systemctl status mcpo-tehuti-core"
fi

# Check Python imports
echo ""
echo "4. Checking Python backend code..."
cd /home/suspect/.n8n/tehuti-lab-webui
if python3 -c "from open_webui.utils.middleware import determine_display_type; print('✅ determine_display_type imported successfully')" 2>/dev/null; then
    echo "   ✅ Backend code imports successfully"
else
    echo "   ❌ Backend code has import errors"
    echo "   Check with: python3 -c 'from open_webui.utils.middleware import determine_display_type'"
fi

# Check TypeScript types
echo ""
echo "5. Checking TypeScript types..."
if [ -f "src/lib/types/tool-results.ts" ] && [ -f "src/lib/types/agent-timeline.ts" ]; then
    echo "   ✅ TypeScript type files exist"
else
    echo "   ❌ TypeScript type files missing"
fi

# Check components
echo ""
echo "6. Checking Svelte components..."
components=(
    "src/lib/components/tool-results/ToolResultRenderer.svelte"
    "src/lib/components/tool-results/FilesystemListRenderer.svelte"
    "src/lib/components/tool-results/FilesystemFileRenderer.svelte"
    "src/lib/components/tool-results/GitMaatRenderer.svelte"
    "src/lib/components/tool-results/CommandOutputRenderer.svelte"
    "src/lib/components/tool-results/PythonResultRenderer.svelte"
    "src/lib/components/tool-results/SystemInfoRenderer.svelte"
    "src/lib/components/agent/AgentTimeline.svelte"
    "src/lib/components/agent/ToolCallTimeline.svelte"
)

missing=0
for comp in "${components[@]}"; do
    if [ -f "$comp" ]; then
        echo "   ✅ $(basename $comp)"
    else
        echo "   ❌ Missing: $comp"
        missing=$((missing + 1))
    fi
done

if [ $missing -eq 0 ]; then
    echo "   ✅ All components exist"
else
    echo "   ❌ $missing component(s) missing"
fi

echo ""
echo "=== Test Checklist ==="
echo ""
echo "To test the integration:"
echo "1. Open http://localhost:3000 in your browser"
echo "2. Go to Chat Settings > External Tools"
echo "3. Enable 'Tehuti Core' (or server:openapi:tehuti-core)"
echo "4. In Chat Settings > Advanced, set function_calling to 'native'"
echo "5. Try these test prompts:"
echo ""
echo "   Test 1: 'List the contents of /home/suspect/.n8n'"
echo "   - Should show FilesystemListRenderer with icons"
echo "   - Should show timeline node above citations"
echo ""
echo "   Test 2: 'Read the file /home/suspect/.n8n/.cursorrules'"
echo "   - Should show FilesystemFileRenderer with code block"
echo "   - Should show timeline node"
echo ""
echo "   Test 3: 'Execute: ls -la /home/suspect/.n8n | head -5'"
echo "   - Should show CommandOutputRenderer with command and output"
echo "   - Should show timeline node"
echo ""
echo "   Test 4: 'List the contents of /home/suspect/.n8n, then read .cursorrules'"
echo "   - Should show timeline with 2 nodes"
echo "   - Each node should show different tool"
echo ""
echo "See docs/WEKNORA-INTEGRATION-TEST-GUIDE.md for detailed test cases"
echo ""

