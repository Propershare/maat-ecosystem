#!/bin/bash
# Setup Maat-Aligned Uncensored Model
# Creates a wrapper model with Maat system prompt using the fine-tuned uncensored model as base
# This combines the fine-tuned weights (better Maat alignment) with the Maat system prompt

# Use uncensored base model directly (no fine-tuning)
# Note: Using Duggles/meta-llama3.1-instruct-uncensored if available, otherwise use regular base
UNCENSORED_BASE="Duggles/meta-llama3.1-instruct-uncensored:latest"
if ollama list | grep -q "meta-llama3.1-instruct-uncensored"; then
    BASE_MODEL="$UNCENSORED_BASE"
    OUTPUT_MODEL_NAME="tehuti-lab-llama3.1-8b-uncensored-maat"
    echo "Setting up Maat-aligned uncensored model (base model, no fine-tuning)"
    echo "✅ Using uncensored base model: $BASE_MODEL"
    echo "   Creating Maat wrapper: $OUTPUT_MODEL_NAME"
    echo "   (No fine-tuning - base model + system prompt only)"
else
    echo "⚠️  Uncensored base model not found: $UNCENSORED_BASE"
    echo "   Falling back to regular base model: llama3.1:8b"
    BASE_MODEL="llama3.1:8b"
    OUTPUT_MODEL_NAME="tehuti-lab:llama3.1-8b-maat"
    echo "   Creating Maat wrapper: $OUTPUT_MODEL_NAME"
fi

echo ""

# Create Modelfile with Maat system prompt
MODELFILE="/tmp/tehuti-uncensored-maat-modelfile"
cat > "$MODELFILE" << 'EOF'
# Maat-Aligned Uncensored Model (Base Model, No Fine-Tuning)
# Uses base uncensored Llama 3.1 Instruct + Maat system prompt
# No fine-tuning to avoid training data contamination
FROM PLACEHOLDER_BASE_MODEL

SYSTEM """
You are an AI assistant in **Tehuti Lab**, guided by Maat principles (Truth, Balance, Order, Justice, Self-Reflection).

**CRITICAL - WHEN TO QUERY GITMAAT:**

**DO NOT query gitMaat for simple questions like:**
- "what tools you have?" → Answer directly by listing tools from your system message (NO gitMaat query)
- "read the file X" → Use the tool directly (NO gitMaat query)
- "execute command X" → Execute directly (NO gitMaat query)
- Simple math or factual questions → Answer directly (NO gitMaat query)

**ONLY query gitMaat when you need context about:**
- Past work, tasks, decisions, learnings
- "What should I do first?" → Query gitMaat for pending tasks
- "Help me with the project" → Query gitMaat for project context
- "What's the best way to..." → Query gitMaat for learnings
- "Can you check maat memory" → Query gitMaat for updates

**MAAT JUDGMENT - INTELLIGENT TOOL USAGE:**

Use **Maat judgment** to decide when to query gitMaat vs when to answer directly. For simple questions that don't need context, answer directly without querying gitMaat.

**CRITICAL - GITMAAT QUERY TOOL:**
- **ONLY use**: `tool_query_gitmaat_post` from Tehuti Core MCP server
- **NEVER use**: `tool_query_post` from postgres-mcp (this is for SQL queries, NOT gitMaat)
- **NEVER use**: SQL queries like `SELECT * FROM MaatMemory` - gitMaat is queried via `tool_query_gitmaat_post` with JSON parameters, NOT SQL
- **NEVER use**: Any other tool name - the EXACT name is `tool_query_gitmaat_post` from Tehuti Core
- **If Tehuti Core is not enabled**: Say "Tehuti Core MCP must be enabled to query gitMaat. Please enable it in Chat Settings → External Tools → Enable 'Tehuti Core'."

**CRITICAL RULES FOR TOOL CALLING:**
- **DO NOT call tools with placeholder/fake parameters** like "/allowed/directory", "/example/path", or empty strings
- **ONLY call tools when you have valid, real parameters** that the user provided or that you know are correct
- **USE CORRECT PATHS** - Use `/home/suspect/.n8n` not `/n8n` for n8n root directory

"""

PARAMETER temperature 0.3
PARAMETER top_p 0.8
PARAMETER top_k 20
PARAMETER num_ctx 4096
EOF

# Update FROM line with actual base model name
sed -i "s|FROM PLACEHOLDER_BASE_MODEL|FROM $BASE_MODEL|" "$MODELFILE"

echo "✅ Created Modelfile at: $MODELFILE"
echo ""

# Create the model (force overwrite if exists)
echo "Creating model: $OUTPUT_MODEL_NAME"
if ollama list | grep -q "$OUTPUT_MODEL_NAME"; then
    echo "⚠️  Model $OUTPUT_MODEL_NAME already exists. Removing old version..."
    ollama rm "$OUTPUT_MODEL_NAME" || true
fi
ollama create "$OUTPUT_MODEL_NAME" -f "$MODELFILE"

echo ""
echo "✅ Model created successfully!"
echo ""
echo "📋 Model Details:"
echo "   Name: $OUTPUT_MODEL_NAME"
echo "   Base: $BASE_MODEL (base model, no fine-tuning)"
echo "   System Prompt: Maat-aligned with intelligent tool usage"
echo ""
echo "🧪 Test the model:"
echo "  ollama run $OUTPUT_MODEL_NAME \"what tools you have?\""
echo ""
echo "✅ Expected behavior:"
echo "   - Starts with 'QUERY gitMaat FIRST' (first line, nothing before it)"
echo "   - Lists actual tools from system message (Tehuti Core, n8n MCP, etc.)"
echo "   - Does NOT hallucinate tools (gitMaat, MaatAligner, etc.)"
echo "   - Does NOT start with 'A straightforward question!' or similar"
echo ""

