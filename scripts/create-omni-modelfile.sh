#!/bin/bash
# Create Modelfile for Qwen2.5-Omni-3B-GGUF (lightest Omni model)

MODEL_NAME="qwen2.5-omni:3b"
HF_MODEL="Qwen/Qwen2.5-Omni-3B-GGUF"

echo "Creating Modelfile for $MODEL_NAME..."
echo "Importing from HuggingFace: $HF_MODEL"
echo ""

cat > /tmp/Modelfile.qwen2.5-omni-3b << 'EOF'
FROM $HF_MODEL

TEMPLATE """{{ if .System }}<|im_start|>system
{{ .System }}<|im_end|>
{{ end }}{{ if .Prompt }}<|im_start|>user
{{ .Prompt }}<|im_end|>
{{ end }}<|im_start|>assistant
{{ .Response }}<|im_end|>
"""

PARAMETER stop "<|im_start|>"
PARAMETER stop "<|im_end|>"
PARAMETER stop "<|endoftext|>"

# Multimodal support (text, image, audio, video)
PARAMETER num_ctx 32768
EOF

echo "Modelfile created at /tmp/Modelfile.qwen2.5-omni-3b"
echo ""
echo "To create the model, run:"
echo "  ollama create $MODEL_NAME -f /tmp/Modelfile.qwen2.5-omni-3b"
