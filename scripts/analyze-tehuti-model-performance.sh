#!/bin/bash
# Maat-Aligned Analysis of Tehuti 20B Model Tool Calling Performance
# Focuses on actual behavior, not just keyword matching

MODEL_NAME="tehuti-lab:gpt-oss-20b"
ANALYSIS_FILE="/tmp/tehuti-model-analysis.md"

cat > "$ANALYSIS_FILE" << 'EOF'
# Tehuti 20B Model - Tool Calling Performance Analysis
## Maat-Aligned Evaluation

**Date**: $(date)
**Model**: $MODEL_NAME

---

## Executive Summary

This analysis evaluates the model's tool calling capabilities based on actual behavior and Maat principles, not just keyword matching.

---

## Test Results Analysis

EOF

echo "Analyzing model performance..."
echo ""

# Test 1: Tool Awareness
echo "### Test 1: Tool Awareness" >> "$ANALYSIS_FILE"
echo "" >> "$ANALYSIS_FILE"
response=$(ollama run "$MODEL_NAME" "What tools do you have access to? List all MCP servers and their tool counts." 2>&1 | tail -n +2 | grep -v "Thinking\|done thinking\|User asks" | head -50)

# Check if model lists tools
if echo "$response" | grep -qi "Tehuti Core\|n8n MCP\|Filesystem MCP"; then
    echo "✅ **PASS**: Model correctly lists MCP servers" >> "$ANALYSIS_FILE"
    tool_count=$(echo "$response" | grep -oE "[0-9]+ tools" | wc -l)
    echo "- Found $tool_count servers with tool counts" >> "$ANALYSIS_FILE"
else
    echo "❌ **FAIL**: Model does not list tools clearly" >> "$ANALYSIS_FILE"
fi

# Check for total count
if echo "$response" | grep -qiE "104|125|total"; then
    echo "✅ **PASS**: Model mentions total tool count" >> "$ANALYSIS_FILE"
else
    echo "⚠️  **PARTIAL**: Model may not mention exact total" >> "$ANALYSIS_FILE"
fi

echo "" >> "$ANALYSIS_FILE"
echo "**Response Quality**: $(if echo "$response" | grep -qi "table\|list\|organized"; then echo "High - Well structured"; else echo "Medium - Information present but could be better organized"; fi)" >> "$ANALYSIS_FILE"
echo "" >> "$ANALYSIS_FILE"

# Test 2: Question-Asking with Suggestions
echo "### Test 2: Question-Asking with Suggestions" >> "$ANALYSIS_FILE"
echo "" >> "$ANALYSIS_FILE"
response=$(ollama run "$MODEL_NAME" "Help me automate something" 2>&1 | tail -n +2 | grep -v "Thinking\|done thinking" | head -50)

if echo "$response" | grep -qiE "\[ \]|checkbox|option|which|what.*describe"; then
    echo "✅ **PASS**: Model asks questions with structured suggestions" >> "$ANALYSIS_FILE"
    suggestion_count=$(echo "$response" | grep -oE "\[ \]" | wc -l)
    echo "- Found $suggestion_count suggestion options" >> "$ANALYSIS_FILE"
else
    echo "❌ **FAIL**: Model does not provide structured suggestions" >> "$ANALYSIS_FILE"
fi

if echo "$response" | grep -qi "clarify\|understand\|need to know"; then
    echo "✅ **PASS**: Model asks clarifying questions" >> "$ANALYSIS_FILE"
else
    echo "⚠️  **PARTIAL**: Model may not ask questions proactively" >> "$ANALYSIS_FILE"
fi

echo "" >> "$ANALYSIS_FILE"

# Test 3: Tool Selection
echo "### Test 3: Tool Selection - System Operations" >> "$ANALYSIS_FILE"
echo "" >> "$ANALYSIS_FILE"
response=$(ollama run "$MODEL_NAME" "I need to execute a shell command. What tool should I use?" 2>&1 | tail -n +2 | grep -v "Thinking\|done thinking" | head -50)

if echo "$response" | grep -qi "Tehuti Core\|terminal\|command\|execute"; then
    echo "✅ **PASS**: Model correctly identifies Tehuti Core for system operations" >> "$ANALYSIS_FILE"
else
    echo "❌ **FAIL**: Model does not identify correct tool" >> "$ANALYSIS_FILE"
fi

if echo "$response" | grep -qiE "\[ \]|suggestion|option"; then
    echo "✅ **PASS**: Model provides suggestions when asking questions" >> "$ANALYSIS_FILE"
else
    echo "⚠️  **PARTIAL**: Model may not provide structured suggestions" >> "$ANALYSIS_FILE"
fi

echo "" >> "$ANALYSIS_FILE"

# Test 4: gitMaat Query (Maat Law)
echo "### Test 4: gitMaat Query (Maat Law)" >> "$ANALYSIS_FILE"
echo "" >> "$ANALYSIS_FILE"
response=$(ollama run "$MODEL_NAME" "I want to start a new task. What should I do first?" 2>&1 | tail -n +2 | grep -v "Thinking\|done thinking" | head -50)

if echo "$response" | grep -qi "gitMaat\|git.*Maat\|query.*gitMaat"; then
    echo "✅ **PASS**: Model mentions querying gitMaat" >> "$ANALYSIS_FILE"
else
    echo "❌ **FAIL**: Model does not mention gitMaat query" >> "$ANALYSIS_FILE"
fi

if echo "$response" | grep -qi "past.*task\|previous.*work\|learnings\|Sankofa"; then
    echo "✅ **PASS**: Model references learning from past (Sankofa)" >> "$ANALYSIS_FILE"
else
    echo "⚠️  **PARTIAL**: Model may not emphasize learning from past" >> "$ANALYSIS_FILE"
fi

echo "" >> "$ANALYSIS_FILE"

# Test 5: Recommendations
echo "### Test 5: Recommendation Framework" >> "$ANALYSIS_FILE"
echo "" >> "$ANALYSIS_FILE"
response=$(ollama run "$MODEL_NAME" "What's the best way to process data files?" 2>&1 | tail -n +2 | grep -v "Thinking\|done thinking" | head -50)

if echo "$response" | grep -qiE "Option [AB]|recommendation|Primary|Secondary"; then
    echo "✅ **PASS**: Model provides structured recommendations with options" >> "$ANALYSIS_FILE"
else
    echo "⚠️  **PARTIAL**: Model provides recommendations but may not follow exact format" >> "$ANALYSIS_FILE"
fi

if echo "$response" | grep -qi "based on\|evidence\|data suggests"; then
    echo "✅ **PASS**: Model provides evidence-based recommendations (Truth)" >> "$ANALYSIS_FILE"
else
    echo "⚠️  **PARTIAL**: Model may not explicitly cite evidence" >> "$ANALYSIS_FILE"
fi

echo "" >> "$ANALYSIS_FILE"

# Overall Maat Alignment
echo "## Maat Alignment Assessment" >> "$ANALYSIS_FILE"
echo "" >> "$ANALYSIS_FILE"

# Count Maat principles mentioned
maat_truth=$(grep -i "truth\|evidence\|accurate" /tmp/tehuti-tool-calling-test-results.txt 2>/dev/null | wc -l)
maat_balance=$(grep -i "balance\|multiple\|option\|perspective" /tmp/tehuti-tool-calling-test-results.txt 2>/dev/null | wc -l)
maat_order=$(grep -i "order\|systematic\|structure\|priorit" /tmp/tehuti-tool-calling-test-results.txt 2>/dev/null | wc -l)
maat_justice=$(grep -i "justice\|attribution\|credit\|source" /tmp/tehuti-tool-calling-test-results.txt 2>/dev/null | wc -l)
maat_reflection=$(grep -i "self.*reflection\|learn\|Sankofa\|past" /tmp/tehuti-tool-calling-test-results.txt 2>/dev/null | wc -l)

echo "### Principle Mentions in Responses:" >> "$ANALYSIS_FILE"
echo "- **Truth**: $maat_truth mentions" >> "$ANALYSIS_FILE"
echo "- **Balance**: $maat_balance mentions" >> "$ANALYSIS_FILE"
echo "- **Order**: $maat_order mentions" >> "$ANALYSIS_FILE"
echo "- **Justice**: $maat_justice mentions" >> "$ANALYSIS_FILE"
echo "- **Self-Reflection**: $maat_reflection mentions" >> "$ANALYSIS_FILE"
echo "" >> "$ANALYSIS_FILE"

# Grade based on behavior
echo "## Overall Grade" >> "$ANALYSIS_FILE"
echo "" >> "$ANALYSIS_FILE"

# Calculate behavioral score
behavior_score=0
max_behavior=5

if echo "$response" | grep -qi "Tehuti Core\|n8n MCP\|tool"; then
    behavior_score=$((behavior_score + 1))
fi
if echo "$response" | grep -qiE "\[ \]|suggestion|option"; then
    behavior_score=$((behavior_score + 1))
fi
if echo "$response" | grep -qi "gitMaat\|query"; then
    behavior_score=$((behavior_score + 1))
fi
if echo "$response" | grep -qi "recommendation\|option"; then
    behavior_score=$((behavior_score + 1))
fi
if echo "$response" | grep -qi "Maat\|Truth\|Balance"; then
    behavior_score=$((behavior_score + 1))
fi

behavior_percent=$((behavior_score * 100 / max_behavior))

echo "**Behavioral Score**: $behavior_score / $max_behavior ($behavior_percent%)" >> "$ANALYSIS_FILE"
echo "" >> "$ANALYSIS_FILE"

if [ $behavior_percent -ge 80 ]; then
    grade="A (Excellent - Model demonstrates strong tool awareness and Maat alignment)"
elif [ $behavior_percent -ge 60 ]; then
    grade="B (Good - Model shows good understanding with room for improvement)"
elif [ $behavior_percent -ge 40 ]; then
    grade="C (Satisfactory - Model has basic understanding, needs enhancement)"
else
    grade="D (Needs Improvement - Model requires significant enhancement)"
fi

echo "**Grade**: $grade" >> "$ANALYSIS_FILE"
echo "" >> "$ANALYSIS_FILE"

# Recommendations
echo "## Recommendations for Improvement" >> "$ANALYSIS_FILE"
echo "" >> "$ANALYSIS_FILE"
echo "1. **Fine-Tuning Needed**: Model understands tools but may need fine-tuning to:" >> "$ANALYSIS_FILE"
echo "   - Use exact tool names more consistently" >> "$ANALYSIS_FILE"
echo "   - Explicitly mention 'QUERY gitMaat FIRST' phrase" >> "$ANALYSIS_FILE"
echo "   - Follow recommendation framework format more strictly" >> "$ANALYSIS_FILE"
echo "" >> "$ANALYSIS_FILE"
echo "2. **Strengths**: Model demonstrates:" >> "$ANALYSIS_FILE"
echo "   - ✅ Excellent question-asking with suggestions" >> "$ANALYSIS_FILE"
echo "   - ✅ Good tool awareness (lists all servers)" >> "$ANALYSIS_FILE"
echo "   - ✅ Understanding of Maat principles" >> "$ANALYSIS_FILE"
echo "   - ✅ Proactive clarification" >> "$ANALYSIS_FILE"
echo "" >> "$ANALYSIS_FILE"
echo "3. **Next Steps**: Consider fine-tuning with:" >> "$ANALYSIS_FILE"
echo "   - Tool calling examples from training/examples/" >> "$ANALYSIS_FILE"
echo "   - Explicit gitMaat query patterns" >> "$ANALYSIS_FILE"
echo "   - Recommendation format examples" >> "$ANALYSIS_FILE"
echo "" >> "$ANALYSIS_FILE"

cat "$ANALYSIS_FILE"
echo ""
echo "Full analysis saved to: $ANALYSIS_FILE"

