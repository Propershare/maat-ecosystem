#!/bin/bash
# Configure Ollama to use /mnt/ai_models/ollama for model storage
# This script requires sudo access

set -e

echo "🔧 Configuring Ollama Storage to /mnt/ai_models/ollama"
echo "======================================================"
echo ""

# Check if running as root or with sudo
if [ "$EUID" -ne 0 ]; then
    echo "⚠️  This script requires sudo access"
    echo "   Please run: sudo bash $0"
    exit 1
fi

# Create storage directory if it doesn't exist
STORAGE_DIR="/mnt/ai_models/ollama"
echo "📁 Creating storage directory: $STORAGE_DIR"
mkdir -p "$STORAGE_DIR"
chown -R suspect:suspect "$STORAGE_DIR"
echo "✅ Directory created and ownership set"
echo ""

# Check if Ollama is running via snap
if command -v snap &> /dev/null && snap list | grep -q ollama; then
    echo "📦 Ollama is installed via snap"
    echo ""
    
    # Stop Ollama service
    echo "🛑 Stopping Ollama service..."
    systemctl stop snap.ollama.ollama.service 2>/dev/null || snap stop ollama 2>/dev/null || echo "   Service stop attempted"
    sleep 2
    echo ""
    
    # Set OLLAMA_MODELS via snap
    echo "⚙️  Configuring snap to use custom models directory..."
    snap set ollama models="$STORAGE_DIR"
    echo "✅ Snap configuration updated"
    echo ""
    
    # Start Ollama service
    echo "▶️  Starting Ollama service..."
    systemctl start snap.ollama.ollama.service 2>/dev/null || snap start ollama 2>/dev/null || echo "   Service start attempted"
    sleep 3
    echo ""
    
    echo "✅ Ollama configured to use: $STORAGE_DIR"
    echo ""
    echo "📊 Storage Status:"
    df -h "$STORAGE_DIR" | tail -1
    echo ""
    echo "🧪 Test configuration:"
    echo "   ollama list"
    echo ""
    
elif [ -f "/etc/systemd/system/ollama.service" ]; then
    echo "🔧 Ollama is installed via systemd service"
    echo ""
    
    # Stop Ollama service
    echo "🛑 Stopping Ollama service..."
    systemctl stop ollama.service
    sleep 2
    echo ""
    
    # Create systemd override directory
    OVERRIDE_DIR="/etc/systemd/system/ollama.service.d"
    mkdir -p "$OVERRIDE_DIR"
    
    # Create override file
    echo "⚙️  Creating systemd override..."
    cat > "$OVERRIDE_DIR/override.conf" << EOF
[Service]
Environment="OLLAMA_MODELS=$STORAGE_DIR"
EOF
    echo "✅ Systemd override created"
    echo ""
    
    # Reload systemd and start service
    echo "🔄 Reloading systemd and starting Ollama..."
    systemctl daemon-reload
    systemctl start ollama.service
    sleep 3
    echo ""
    
    echo "✅ Ollama configured to use: $STORAGE_DIR"
    echo ""
    
else
    echo "⚠️  Could not determine Ollama installation method"
    echo "   Please configure OLLAMA_MODELS manually:"
    echo "   export OLLAMA_MODELS=$STORAGE_DIR"
    exit 1
fi

echo "✅ Configuration complete!"
echo ""
echo "📋 Next steps:"
echo "   1. Verify: ollama list"
echo "   2. Download uncensored model: ollama pull Duggles/meta-llama3.1-instruct-uncensored"
echo "   3. Check storage: df -h $STORAGE_DIR"
echo ""

