#!/bin/bash
# Setup Tehuti Lab System Prompt for Ollama Models
# Enhanced with Maat-aligned question asking and recommendations
#
# CRITICAL REQUIREMENT: Tehuti Core MCP must be enabled in Open WebUI chat settings
# for the model to query gitMaat. The tool_query_gitmaat_post tool is provided
# by Tehuti Core MCP server (port 8014). Without it, "QUERY gitMaat FIRST" cannot execute.
# Enable: Open WebUI → Chat Settings → External Tools → Enable "Tehuti Core"

MODEL_NAME="${1:-llama3.1:8b}"

# Use base model directly (no fine-tuning) - base models follow system prompts better
# Fine-tuning on bad training data causes hallucinations, so we skip it
BASE_MODEL="llama3.1:8b"
OUTPUT_MODEL_NAME="tehuti-lab:llama3.1-8b-maat"
echo "✅ Using base model: $BASE_MODEL"
echo "   Creating Maat wrapper: $OUTPUT_MODEL_NAME"
echo "   (No fine-tuning - base model + system prompt only)"

echo ""

# Check if base model exists
if ! ollama list | grep -q "$BASE_MODEL"; then
    echo "⚠️  Model $BASE_MODEL not found. Available models:"
    ollama list
    echo ""
    echo "Please install the model first:"
    echo "  ollama pull $BASE_MODEL"
    exit 1
fi

echo "✅ Base model $BASE_MODEL found"
echo ""

# Create Modelfile with enhanced system prompt
MODELFILE="/tmp/tehuti-lab-modelfile"
cat > "$MODELFILE" << 'EOF'
# Fine-tuned Tehuti Lab Model (GGUF format)
# This model uses the actual fine-tuned weights for better Maat alignment
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

# Performance settings for 3080 Ti
PARAMETER num_gpu 1
PARAMETER num_thread 8
PARAMETER temperature 0.3
PARAMETER top_p 0.8
PARAMETER top_k 20
PARAMETER num_ctx 4096
EOF

# Replace placeholder with actual base model
sed -i "s|FROM PLACEHOLDER_BASE_MODEL|FROM $BASE_MODEL|" "$MODELFILE"

echo "✅ Created enhanced Modelfile at: $MODELFILE"
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
echo "   Base: $BASE_MODEL"
if [ "$BASE_MODEL" = "$FINE_TUNED_MODEL" ]; then
    echo "   Type: Fine-tuned weights + Maat system prompt (RECOMMENDED)"
else
    echo "   Type: Base model + Maat system prompt"
fi
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
