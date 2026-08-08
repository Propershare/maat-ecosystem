#!/bin/bash
# Fix venv permissions and install Docling

cd /home/suspect/.n8n/maatlangchain

echo "Fixing virtual environment permissions..."
sudo chmod -R u+w /home/suspect/.n8n/tehuti-lab-webui-venv/lib/python3.12/site-packages/ 2>/dev/null || {
    echo "Trying without sudo..."
    chmod -R u+w /home/suspect/.n8n/tehuti-lab-webui-venv/lib/python3.12/site-packages/ 2>/dev/null || true
}

echo ""
echo "Installing Docling..."
pip install docling

echo ""
echo "Verifying installation..."
python3 -c "import docling; print('✅ Docling installed!')" && echo "Ready to test!" || echo "⚠️  Installation may have issues"

