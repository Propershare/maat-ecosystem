#!/bin/bash
# Fix Fine-Tuned Model Visibility in Open WebUI
# This script verifies the model exists, fixes naming issues, and refreshes Open WebUI cache

set -e

echo "🔍 Diagnosing Fine-Tuned Model Visibility Issue"
echo "================================================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Step 1: Check if model exists in Ollama
echo "📋 Step 1: Checking Ollama models..."
echo ""

MODEL_FOUND=false
MODEL_NAME=""

# Check for different possible model names
for name in "tehuti-lab-llama3.1-8b-finetuned:latest" "tehuti-lab:llama3.1-8b-finetuned" "tehuti-lab-llama3.1-8b-finetuned"; do
    if ollama list | grep -q "$name"; then
        MODEL_NAME="$name"
        MODEL_FOUND=true
        echo -e "${GREEN}✅ Found model: $MODEL_NAME${NC}"
        break
    fi
done

if [ "$MODEL_FOUND" = false ]; then
    echo -e "${RED}❌ Fine-tuned model not found in Ollama${NC}"
    echo ""
    echo "Available models:"
    ollama list
    echo ""
    echo "Please import the model first:"
    echo "  ollama create tehuti-lab:llama3.1-8b-finetuned -f <modelfile>"
    exit 1
fi

echo ""

# Step 2: Check Ollama API
echo "📋 Step 2: Checking Ollama API..."
echo ""

API_RESPONSE=$(curl -s http://localhost:11434/api/tags)
if echo "$API_RESPONSE" | grep -q "tehuti-lab.*finetuned"; then
    echo -e "${GREEN}✅ Model visible in Ollama API${NC}"
    echo "$API_RESPONSE" | python3 -m json.tool | grep -A 3 "tehuti-lab.*finetuned" | head -10
else
    echo -e "${YELLOW}⚠️  Model not found in Ollama API response${NC}"
    echo "This might be a naming issue."
fi

echo ""

# Step 3: Standardize model name (create alias if needed)
echo "📋 Step 3: Standardizing model name..."
echo ""

DESIRED_NAME="tehuti-lab:llama3.1-8b-finetuned"

if [ "$MODEL_NAME" != "$DESIRED_NAME" ]; then
    echo -e "${YELLOW}⚠️  Model name mismatch detected${NC}"
    echo "   Current: $MODEL_NAME"
    echo "   Desired: $DESIRED_NAME"
    echo ""
    echo "Creating alias..."
    
    # Extract base name without tag
    BASE_NAME=$(echo "$MODEL_NAME" | cut -d: -f1)
    
    # Create a new model with the desired name pointing to the existing one
    # We'll create a Modelfile that references the existing model
    TEMP_MODELFILE="/tmp/tehuti-finetuned-modelfile"
    cat > "$TEMP_MODELFILE" << EOF
FROM $MODEL_NAME

# Fine-tuned Tehuti Lab Model
# This model uses the actual fine-tuned weights for better Maat alignment
EOF
    
    # Check if desired name already exists
    if ollama list | grep -q "$DESIRED_NAME"; then
        echo -e "${YELLOW}⚠️  Model $DESIRED_NAME already exists. Removing old version...${NC}"
        ollama rm "$DESIRED_NAME" || true
    fi
    
    echo "Creating model with standardized name..."
    if ollama create "$DESIRED_NAME" -f "$TEMP_MODELFILE"; then
        echo -e "${GREEN}✅ Created standardized model: $DESIRED_NAME${NC}"
        MODEL_NAME="$DESIRED_NAME"
    else
        echo -e "${YELLOW}⚠️  Could not create alias. Using existing name: $MODEL_NAME${NC}"
    fi
    
    rm -f "$TEMP_MODELFILE"
else
    echo -e "${GREEN}✅ Model name is correct: $MODEL_NAME${NC}"
fi

echo ""

# Step 4: Update setup script to use correct model name
echo "📋 Step 4: Updating setup script..."
echo ""

SETUP_SCRIPT="/home/suspect/.n8n/scripts/setup-tehuti-ollama-model.sh"
if [ -f "$SETUP_SCRIPT" ]; then
    # Check if FROM line matches
    if grep -q "FROM.*finetuned" "$SETUP_SCRIPT"; then
        CURRENT_FROM=$(grep "FROM.*finetuned" "$SETUP_SCRIPT" | head -1 | sed 's/.*FROM //')
        if [ "$CURRENT_FROM" != "$MODEL_NAME" ]; then
            echo -e "${YELLOW}⚠️  Updating FROM line in setup script...${NC}"
            sed -i "s|FROM.*finetuned|FROM $MODEL_NAME|" "$SETUP_SCRIPT"
            echo -e "${GREEN}✅ Updated setup script${NC}"
        else
            echo -e "${GREEN}✅ Setup script already uses correct model name${NC}"
        fi
    fi
else
    echo -e "${YELLOW}⚠️  Setup script not found at $SETUP_SCRIPT${NC}"
fi

echo ""

# Step 5: Check Open WebUI status
echo "📋 Step 5: Checking Open WebUI status..."
echo ""

# Check if running in Docker
if docker ps | grep -q "webui\|open-webui"; then
    echo -e "${GREEN}✅ Open WebUI is running in Docker${NC}"
    CONTAINER_NAME=$(docker ps | grep "webui\|open-webui" | awk '{print $NF}' | head -1)
    echo "   Container: $CONTAINER_NAME"
    echo ""
    echo "To refresh model cache, restart the container:"
    echo "  docker restart $CONTAINER_NAME"
    echo ""
    read -p "Restart Open WebUI container now? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Restarting container..."
        docker restart "$CONTAINER_NAME"
        echo -e "${GREEN}✅ Container restarted${NC}"
    fi
elif systemctl is-active --quiet open-webui 2>/dev/null; then
    echo -e "${GREEN}✅ Open WebUI is running as systemd service${NC}"
    echo ""
    read -p "Restart Open WebUI service now? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Restarting service..."
        sudo systemctl restart open-webui
        echo -e "${GREEN}✅ Service restarted${NC}"
    fi
elif pgrep -f "uvicorn.*open_webui" > /dev/null; then
    echo -e "${GREEN}✅ Open WebUI is running as a process${NC}"
    echo ""
    echo "To refresh model cache, restart the process manually"
else
    echo -e "${YELLOW}⚠️  Open WebUI status unknown${NC}"
    echo "   Please restart Open WebUI manually to refresh model cache"
fi

echo ""

# Step 6: Verify model is accessible
echo "📋 Step 6: Testing model accessibility..."
echo ""

echo "Testing model response..."
TEST_RESPONSE=$(timeout 10 ollama run "$MODEL_NAME" "test" 2>&1 | head -5 || echo "ERROR")
if echo "$TEST_RESPONSE" | grep -q "ERROR\|timeout\|failed"; then
    echo -e "${RED}❌ Model test failed${NC}"
    echo "$TEST_RESPONSE"
else
    echo -e "${GREEN}✅ Model is responding${NC}"
fi

echo ""

# Summary
echo "================================================"
echo "📊 Summary"
echo "================================================"
echo ""
echo "Model Name: $MODEL_NAME"
echo "Status: $([ "$MODEL_FOUND" = true ] && echo -e "${GREEN}✅ Found${NC}" || echo -e "${RED}❌ Not Found${NC}")"
echo ""
echo "Next Steps:"
echo "1. Verify model appears in Open WebUI after restart"
echo "2. If still not visible, check Open WebUI logs for errors"
echo "3. Ensure OLLAMA_BASE_URL is correctly configured in Open WebUI"
echo ""
echo "To manually refresh models in Open WebUI:"
echo "  - Restart the service/container"
echo "  - Or use the refresh button in the UI (if available)"
echo ""

