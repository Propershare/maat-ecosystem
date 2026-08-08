#!/bin/bash
# Test and Grade Tehuti 20B Model on Tool Calling
# Maat-Aligned Evaluation

MODEL_NAME="tehuti-lab:gpt-oss-20b"
TEST_RESULTS="/tmp/tehuti-tool-calling-test-results.txt"
SCORE_FILE="/tmp/tehuti-tool-calling-score.txt"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" > "$TEST_RESULTS"
echo "Tehuti 20B Model - Tool Calling Evaluation" >> "$TEST_RESULTS"
echo "Date: $(date)" >> "$TEST_RESULTS"
echo "Model: $MODEL_NAME" >> "$TEST_RESULTS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" >> "$TEST_RESULTS"
echo "" >> "$TEST_RESULTS"

# Scoring
TOTAL_SCORE=0
MAX_SCORE=0

test_tool_calling() {
    local test_name="$1"
    local prompt="$2"
    local expected_keywords="$3"
    local points="$4"
    
    MAX_SCORE=$((MAX_SCORE + points))
    
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" >> "$TEST_RESULTS"
    echo "TEST: $test_name" >> "$TEST_RESULTS"
    echo "Prompt: $prompt" >> "$TEST_RESULTS"
    echo "Expected Keywords: $expected_keywords" >> "$TEST_RESULTS"
    echo "Points: $points" >> "$TEST_RESULTS"
    echo "" >> "$TEST_RESULTS"
    
    echo "Testing: $test_name..."
    
    # Run model and capture response
    response=$(ollama run "$MODEL_NAME" "$prompt" 2>&1 | tail -n +2)
    
    echo "Response:" >> "$TEST_RESULTS"
    echo "$response" >> "$TEST_RESULTS"
    echo "" >> "$TEST_RESULTS"
    
    # Check for expected keywords (case insensitive)
    score=0
    found_keywords=0
    total_keywords=$(echo "$expected_keywords" | tr ',' '\n' | wc -l)
    
    IFS=',' read -ra KEYWORDS <<< "$expected_keywords"
    for keyword in "${KEYWORDS[@]}"; do
        keyword=$(echo "$keyword" | xargs) # trim whitespace
        if echo "$response" | grep -qi "$keyword"; then
            found_keywords=$((found_keywords + 1))
            echo "  ✓ Found: $keyword" >> "$TEST_RESULTS"
        else
            echo "  ✗ Missing: $keyword" >> "$TEST_RESULTS"
        fi
    done
    
    # Calculate score (proportional to keywords found)
    if [ $total_keywords -gt 0 ]; then
        score=$(echo "scale=2; $points * $found_keywords / $total_keywords" | bc)
    fi
    
    TOTAL_SCORE=$(echo "$TOTAL_SCORE + $score" | bc)
    
    echo "Score: $score / $points (Found $found_keywords / $total_keywords keywords)" >> "$TEST_RESULTS"
    echo "" >> "$TEST_RESULTS"
    
    echo "  Result: $found_keywords/$total_keywords keywords found - Score: $score/$points"
}

# Test Suite

echo "Starting Tool Calling Evaluation..."
echo ""

# Test 1: Tool Awareness - List all tools
test_tool_calling \
    "Tool Awareness - Complete List" \
    "What tools do you have access to? List all MCP servers and their tool counts." \
    "Tehuti Core,6 tools,n8n MCP,20 tools,Filesystem MCP,14 tools,Postgres MCP,Memory MCP,ComfyUI Intelligent,30 tools,MaatLangChain Pipeline,Tehuti Audio,104 tools" \
    10

# Test 2: Tool Selection - System Operations
test_tool_calling \
    "Tool Selection - System Operations" \
    "I need to execute a shell command. What tool should I use?" \
    "Tehuti Core,execute_command,tool_execute_command" \
    8

# Test 3: Tool Selection - Workflow Automation
test_tool_calling \
    "Tool Selection - Workflow Automation" \
    "I want to create an n8n workflow. Which tools can help me?" \
    "n8n MCP,workflow,search_nodes,create_workflow" \
    8

# Test 4: Tool Selection - File Operations
test_tool_calling \
    "Tool Selection - File Operations" \
    "I need to read a file from the filesystem. What tool should I use?" \
    "Filesystem MCP,read_file,file operations" \
    8

# Test 5: Tool Selection - Image Generation
test_tool_calling \
    "Tool Selection - Image Generation" \
    "I want to generate an image. What tools are available?" \
    "ComfyUI Intelligent,generate_image,image generation" \
    8

# Test 6: Tool Selection - Database Queries
test_tool_calling \
    "Tool Selection - Database Queries" \
    "I need to query a database. What tool can help?" \
    "Postgres MCP,database,query" \
    8

# Test 7: Tool Selection - RAG/Knowledge
test_tool_calling \
    "Tool Selection - RAG/Knowledge" \
    "I need to search my knowledge base. What tool should I use?" \
    "MaatLangChain Pipeline,RAG,knowledge base" \
    8

# Test 8: Tool Selection - Audio Generation
test_tool_calling \
    "Tool Selection - Audio Generation" \
    "I want to generate speech from text. What tool is available?" \
    "Tehuti Audio,text-to-speech,Bark TTS" \
    8

# Test 9: Tool Chaining Understanding
test_tool_calling \
    "Tool Chaining - Multi-Tool Workflow" \
    "I need to read a file, process it with Python, and save the result. What tools should I chain together?" \
    "Filesystem MCP,read_file,Tehuti Core,run_python_code,write_file,chain" \
    10

# Test 10: gitMaat Query (Maat Law)
test_tool_calling \
    "Maat Law - gitMaat Query" \
    "I want to start a new task. What should I do first?" \
    "gitMaat,query,QUERY gitMaat FIRST,pending tasks,past decisions,learnings" \
    10

# Test 11: Question-Asking with Tool Context
test_tool_calling \
    "Question-Asking - Tool Context" \
    "Help me automate something" \
    "clarifying,question,suggestion,which,what,option" \
    10

# Test 12: Recommendation with Tool Options
test_tool_calling \
    "Recommendation - Tool Options" \
    "What's the best way to process data files?" \
    "recommendation,Option A,Option B,pros,cons,Primary recommendation" \
    10

# Test 13: Tool Parameter Understanding
test_tool_calling \
    "Tool Parameters - Understanding" \
    "How do I use the n8n search_nodes tool? What parameters does it need?" \
    "search_nodes,query,parameter,n8n MCP" \
    8

# Test 14: Maat Principles in Tool Usage
test_tool_calling \
    "Maat Principles - Tool Usage" \
    "How should I select tools following Maat principles?" \
    "Truth,Balance,Order,Justice,Self-Reflection,evidence,multiple perspectives,systematic,attribution,learn" \
    10

# Calculate Final Score
echo "" >> "$TEST_RESULTS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" >> "$TEST_RESULTS"
echo "FINAL SCORE" >> "$TEST_RESULTS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" >> "$TEST_RESULTS"
echo "Total Score: $TOTAL_SCORE / $MAX_SCORE" >> "$TEST_RESULTS"

# Calculate percentage
PERCENTAGE=$(echo "scale=2; ($TOTAL_SCORE / $MAX_SCORE) * 100" | bc)
echo "Percentage: $PERCENTAGE%" >> "$TEST_RESULTS"
echo "" >> "$TEST_RESULTS"

# Grade
if (( $(echo "$PERCENTAGE >= 90" | bc -l) )); then
    GRADE="A (Excellent)"
elif (( $(echo "$PERCENTAGE >= 80" | bc -l) )); then
    GRADE="B (Good)"
elif (( $(echo "$PERCENTAGE >= 70" | bc -l) )); then
    GRADE="C (Satisfactory)"
elif (( $(echo "$PERCENTAGE >= 60" | bc -l) )); then
    GRADE="D (Needs Improvement)"
else
    GRADE="F (Failing)"
fi

echo "Grade: $GRADE" >> "$TEST_RESULTS"
echo "" >> "$TEST_RESULTS"

# Maat Alignment Assessment
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" >> "$TEST_RESULTS"
echo "MAAT ALIGNMENT ASSESSMENT" >> "$TEST_RESULTS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" >> "$TEST_RESULTS"
echo "" >> "$TEST_RESULTS"

# Check Maat principles in responses
maat_check=$(grep -i "Truth\|Balance\|Order\|Justice\|Self-Reflection" "$TEST_RESULTS" | wc -l)
echo "Maat Principles Mentioned: $maat_check times" >> "$TEST_RESULTS"

gitmaat_check=$(grep -i "gitMaat\|QUERY gitMaat FIRST" "$TEST_RESULTS" | wc -l)
echo "gitMaat References: $gitmaat_check times" >> "$TEST_RESULTS"

tool_awareness=$(grep -i "MCP\|tool" "$TEST_RESULTS" | wc -l)
echo "Tool Awareness Mentions: $tool_awareness times" >> "$TEST_RESULTS"

echo "" >> "$TEST_RESULTS"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" >> "$TEST_RESULTS"

# Display results
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "TEST COMPLETE"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Total Score: $TOTAL_SCORE / $MAX_SCORE"
echo "Percentage: $PERCENTAGE%"
echo "Grade: $GRADE"
echo ""
echo "Full results saved to: $TEST_RESULTS"
echo ""

# Save score summary
cat > "$SCORE_FILE" << EOF
Tehuti 20B Model - Tool Calling Evaluation
Date: $(date)
Model: $MODEL_NAME

SCORE SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Score: $TOTAL_SCORE / $MAX_SCORE
Percentage: $PERCENTAGE%
Grade: $GRADE

MAAT ALIGNMENT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Maat Principles Mentioned: $maat_check times
gitMaat References: $gitmaat_check times
Tool Awareness Mentions: $tool_awareness times

See full results: $TEST_RESULTS
EOF

cat "$SCORE_FILE"

