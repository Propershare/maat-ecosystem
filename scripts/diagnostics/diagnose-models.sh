#!/bin/bash
# Diagnose why custom models aren't showing

echo "=== OpenWebUI Custom Model Diagnosis ==="
echo ""

echo "1. Your Custom Models in Database:"
sqlite3 open-webui/data/webui.db "SELECT id, name, base_model_id FROM model WHERE user_id='b9937d92-97c1-42fb-90ea-ffa53f394a31';" 2>/dev/null

echo ""
echo "2. Checking if base models exist in Ollama:"
echo "   - llama3.2:latest"
ollama list 2>/dev/null | grep -q "llama3.2" && echo "   ✅ Found" || echo "   ❌ Missing"

echo "   - qwen2.5:14b"
ollama list 2>/dev/null | grep -q "qwen2.5" && echo "   ✅ Found" || echo "   ❌ Missing"

echo "   - qwen3-vl:8b"
ollama list 2>/dev/null | grep -q "qwen3-vl" && echo "   ✅ Found" || echo "   ❌ Missing"

echo ""
echo "3. OpenWebUI Service Status:"
systemctl is-active open-webui.service && echo "   ✅ Running" || echo "   ❌ Not running"

echo ""
echo "4. Knowledge Bases:"
sqlite3 open-webui/data/webui.db "SELECT name FROM knowledge WHERE user_id='b9937d92-97c1-42fb-90ea-ffa53f394a31';" 2>/dev/null

echo ""
echo "=== Where to Find Your Models in OpenWebUI ==="
echo "Custom model profiles appear in:"
echo "  1. Settings (gear icon) → Models section"
echo "  2. Model selector dropdown (if base models are available)"
echo ""
echo "If base models are missing, custom profiles won't show in the dropdown."
echo "But they should still appear in Settings → Models."

