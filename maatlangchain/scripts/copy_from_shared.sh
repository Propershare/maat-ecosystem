#!/bin/bash
# Copy scripts from shared directory to local maatlangchain
# Run this on each laptop (MacDaddy, Imhotepjr)

echo "Copying Maat Memory scripts from shared directory..."

# Copy scripts
cp /home/suspect/.n8n/shared/setup_maat_memory.py /home/suspect/.n8n/maatlangchain/scripts/
cp /home/suspect/.n8n/shared/verify_sync.py /home/suspect/.n8n/maatlangchain/scripts/

# Make executable
chmod +x /home/suspect/.n8n/maatlangchain/scripts/setup_maat_memory.py
chmod +x /home/suspect/.n8n/maatlangchain/scripts/verify_sync.py

echo "✅ Scripts copied!"
echo ""
echo "Next: Run setup script:"
echo "  python3 /home/suspect/.n8n/maatlangchain/scripts/setup_maat_memory.py"

