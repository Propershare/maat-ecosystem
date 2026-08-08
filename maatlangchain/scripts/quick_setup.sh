#!/bin/bash
# Quick setup script - just sets the database URL and verifies it works
# Run this on each laptop: bash quick_setup.sh

DB_URL="postgresql://suspect:<password>@192.168.4.21:5434/n8n_ai_starter"

echo "🔧 Setting up Maat Memory..."
echo ""

# Add to .bashrc if not already there
if ! grep -q "PGVECTOR_DB_URL" ~/.bashrc; then
    echo "export PGVECTOR_DB_URL='$DB_URL'" >> ~/.bashrc
    echo "✅ Added to ~/.bashrc"
else
    echo "✅ Already in ~/.bashrc"
fi

# Set for current session
export PGVECTOR_DB_URL="$DB_URL"

# Quick test
echo ""
echo "🧪 Testing connection..."
python3 << EOF
import os
os.environ['PGVECTOR_DB_URL'] = '$DB_URL'
try:
    from maat_memory.memory_postgres import MaatMemoryPostgres
    memory = MaatMemoryPostgres()
    print("✅ PostgreSQL connection successful!")
    print("✅ Maat Memory is ready!")
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)
EOF

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Setup complete! Restart your terminal or run: source ~/.bashrc"
else
    echo ""
    echo "❌ Setup failed. Check your network connection to 192.168.4.21"
fi

