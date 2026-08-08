#!/bin/bash
# Fix permissions and install Docling

cd /home/suspect/.n8n/maatlangchain

echo "Fixing virtual environment permissions..."
chmod -R u+w /home/suspect/.n8n/tehuti-lab-webui-venv/lib/python3.12/site-packages/ 2>/dev/null || true

echo ""
echo "Installing Docling with --user flag (safer)..."
python3 -m pip install --user docling

echo ""
echo "Checking if Docling is now available..."
python3 -c "import docling; print('✅ Docling installed successfully!')" 2>/dev/null && echo "Ready to test!" || echo "⚠️  May need to add to PYTHONPATH"

