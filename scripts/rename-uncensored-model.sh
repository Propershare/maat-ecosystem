#!/bin/bash
# Create a custom-named model from the uncensored base
# This creates an alias/wrapper with your preferred name

SOURCE_MODEL="${1:-Duggles/meta-llama3.1-instruct-uncensored}"
CUSTOM_NAME="${2:-llama3.1-uncensored}"

echo "Creating custom-named model from: $SOURCE_MODEL"
echo "New name: $CUSTOM_NAME"
echo ""

# Check if source model exists
if ! ollama list | grep -q "$SOURCE_MODEL"; then
    echo "⚠️  Source model $SOURCE_MODEL not found."
    echo ""
    echo "Available models:"
    ollama list
    echo ""
    echo "Please wait for the download to complete, or use a different source model."
    exit 1
fi

echo "✅ Source model found: $SOURCE_MODEL"
echo ""

# Create Modelfile
MODELFILE="/tmp/custom-name-modelfile"
cat > "$MODELFILE" << EOF
FROM $SOURCE_MODEL
EOF

echo "Creating model: $CUSTOM_NAME"
ollama create "$CUSTOM_NAME" -f "$MODELFILE"

echo ""
echo "✅ Model created: $CUSTOM_NAME"
echo ""
echo "Usage:"
echo "  ollama run $CUSTOM_NAME \"your prompt here\""
echo ""
echo "You can now use the shorter name: $CUSTOM_NAME"
echo "instead of: $SOURCE_MODEL"
echo ""

