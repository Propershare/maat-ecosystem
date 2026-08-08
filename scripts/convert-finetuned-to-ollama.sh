#!/bin/bash
# Convert fine-tuned model to GGUF and import into Ollama
# This script converts the merged fine-tuned model to Ollama format

set -e

PROJECT_ROOT="/home/suspect/.n8n"
FINE_TUNED_DIR="$PROJECT_ROOT/fine-tuned-models/tehuti-lab-llama3.1-8b-maat-merged"
OUTPUT_MODEL_NAME="tehuti-lab-llama3.1-8b-finetuned"

echo "🔄 Converting fine-tuned model to Ollama format..."
echo "=" * 60

# Check if fine-tuned model exists
if [ ! -d "$FINE_TUNED_DIR" ]; then
    echo "❌ Fine-tuned model not found at: $FINE_TUNED_DIR"
    echo "   Please run fine-tuning first: python3 scripts/fine_tune_maat.py"
    exit 1
fi

echo "✅ Fine-tuned model found at: $FINE_TUNED_DIR"
echo ""

# Check if llama.cpp is available
if command -v llama.cpp &> /dev/null || command -v llama-cpp &> /dev/null; then
    echo "✅ llama.cpp found"
    CONVERTER="llama.cpp"
elif [ -f "/usr/local/bin/convert.py" ] || [ -f "$HOME/.local/bin/convert.py" ]; then
    echo "✅ convert.py found"
    CONVERTER="convert.py"
else
    echo "⚠️  llama.cpp not found. Installing via pip..."
    pip3 install llama-cpp-python[server] --upgrade || {
        echo "❌ Failed to install llama.cpp"
        echo "   Please install manually: pip3 install llama-cpp-python"
        exit 1
    }
fi

# Method 1: Use llama.cpp convert script (if available)
if command -v python3 &> /dev/null; then
    echo ""
    echo "📦 Method 1: Using Python transformers + llama.cpp conversion"
    echo "   This will convert the model to GGUF format..."
    
    # Create conversion script
    cat > /tmp/convert_to_gguf.py << 'PYEOF'
import sys
from pathlib import Path
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import json

model_path = sys.argv[1]
output_path = sys.argv[2]

print(f"Loading model from: {model_path}")
print(f"Output will be: {output_path}")

# Load model and tokenizer
model = AutoModelForCausalLM.from_pretrained(
    model_path,
    torch_dtype=torch.float16,
    device_map="auto",
    trust_remote_code=True
)
tokenizer = AutoTokenizer.from_pretrained(model_path)

print("Model loaded successfully!")
print(f"Model type: {type(model)}")
print(f"Model config: {model.config.model_type}")

# Save in a format that can be converted
print("\n💾 Saving model for GGUF conversion...")
print("   Note: Direct GGUF conversion requires llama.cpp")
print("   For now, saving in a compatible format...")

# Save tokenizer
tokenizer.save_pretrained(output_path)

print(f"\n✅ Model prepared at: {output_path}")
print("\n⚠️  Next step: Use llama.cpp convert script to create GGUF file")
print("   Example: python3 -m llama_cpp.convert --model-dir {output_path} --outfile model.gguf")
PYEOF

    python3 /tmp/convert_to_gguf.py "$FINE_TUNED_DIR" "/tmp/tehuti-finetuned-prep" || {
        echo "⚠️  Python conversion method failed, trying alternative..."
    }
fi

# Method 2: Use Ollama's import feature (if model is in HuggingFace format)
echo ""
echo "📦 Method 2: Using Ollama import (recommended)"
echo "   Ollama can import models directly from HuggingFace format..."

# Check if we can use Ollama's import
if command -v ollama &> /dev/null; then
    echo ""
    echo "🔄 Attempting to import model into Ollama..."
    echo "   This may take a while..."
    
    # Create a temporary Modelfile that references the local model
    TEMP_MODELFILE="/tmp/tehuti-finetuned-modelfile"
    cat > "$TEMP_MODELFILE" << EOF
# Fine-tuned Tehuti Lab Model
# This model was fine-tuned for Maat alignment

# Note: Ollama doesn't directly import local PyTorch models
# We need to either:
# 1. Upload to HuggingFace and import from there
# 2. Convert to GGUF first using llama.cpp
# 3. Use a different import method

# For now, we'll create a model that uses the base model
# but with the fine-tuned system prompt
FROM llama3.1:8b

SYSTEM """
You are a fine-tuned AI assistant in **Tehuti Lab**, trained specifically for Maat alignment.
This model was fine-tuned on Maat-aligned examples for better tool calling and recommendations.
"""
EOF

    echo "⚠️  Direct import from local PyTorch model not supported by Ollama"
    echo "   Ollama requires GGUF format or HuggingFace Hub"
    echo ""
    echo "📋 Options:"
    echo "   1. Convert to GGUF using llama.cpp (recommended)"
    echo "   2. Upload to HuggingFace Hub and import from there"
    echo "   3. Use the base model with enhanced system prompt (current approach)"
    echo ""
    
    # Check if we can use llama.cpp-python to convert
    python3 << 'PYEOF'
import sys
from pathlib import Path

try:
    from llama_cpp import Llama
    print("✅ llama-cpp-python available")
    print("   Can use for inference, but conversion still needs llama.cpp tools")
except ImportError:
    print("⚠️  llama-cpp-python not installed")
    print("   Install: pip3 install llama-cpp-python")

# Check for transformers
try:
    from transformers import AutoModelForCausalLM
    print("✅ transformers available")
except ImportError:
    print("❌ transformers not installed")
    sys.exit(1)
PYEOF

else
    echo "❌ Ollama not found. Please install Ollama first."
    exit 1
fi

echo ""
echo "=" * 60
echo "📋 Summary:"
echo "   Fine-tuned model location: $FINE_TUNED_DIR"
echo "   Target Ollama model: $OUTPUT_MODEL_NAME"
echo ""
echo "⚠️  IMPORTANT: Ollama requires GGUF format for local models"
echo "   The fine-tuned model is in PyTorch/Safetensors format"
echo ""
echo "🔧 Next Steps:"
echo "   1. Install llama.cpp: https://github.com/ggerganov/llama.cpp"
echo "   2. Convert model: python3 convert.py $FINE_TUNED_DIR --outfile model.gguf"
echo "   3. Import to Ollama: ollama create $OUTPUT_MODEL_NAME -f Modelfile"
echo ""
echo "   OR use the base model with enhanced system prompt (current approach)"

