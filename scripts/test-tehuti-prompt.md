# Testing TEHUTI System Prompt

## Test Questions to Verify Proper Behavior

### Test 1: Tool Awareness (CRITICAL)
**Question:** "what tools you have available in the system to help me?"

**Expected Response:**
- Should copy EXACTLY from "AVAILABLE TOOLS IN THIS CHAT SESSION:" section
- Should NOT make up tools like "text editor", "compiler", "Git", "npm"
- Should NOT list services like "n8n", "PostgreSQL" as tools
- Should list actual MCP tools with backticks (e.g., `query_gitmaat`, `execute_command`)

**FAIL if:**
- Makes up generic tools
- Lists services instead of tools
- Summarizes instead of copying exactly
- Says "various tools" without listing them

---

### Test 2: Direct Tool Usage (No gitMaat)
**Question:** "list the files in /home/suspect/.n8n"

**Expected Response:**
- Should use `list_directory` tool directly
- Should NOT query gitMaat first
- Should provide actual directory listing

**FAIL if:**
- Queries gitMaat before using tool
- Makes up file list
- Doesn't use the tool

---

### Test 3: gitMaat Query (When Needed)
**Question:** "what should I work on first?"

**Expected Response:**
- Should query gitMaat for pending tasks
- Should use `query_gitmaat(query_type="tasks", status="pending", limit=10)`
- Should provide actual task list from database

**FAIL if:**
- Doesn't query gitMaat
- Makes up tasks
- Uses wrong tool name

---

### Test 4: Simple Question (No Tools Needed)
**Question:** "what is 2 + 2?"

**Expected Response:**
- Should answer directly: "4"
- Should NOT query gitMaat
- Should NOT use any tools

**FAIL if:**
- Queries gitMaat
- Uses tools unnecessarily
- Overcomplicates the answer

---

### Test 5: File Reading
**Question:** "read the .cursorrules file"

**Expected Response:**
- Should use `read_file` tool
- Should NOT query gitMaat first
- Should provide actual file contents

**FAIL if:**
- Queries gitMaat before reading
- Makes up file contents
- Doesn't use the tool

---

## How to Test

1. **Load the prompt in Open WebUI:**
   - Copy contents of `tehuti-system-prompt.txt`
   - Go to Open WebUI → Settings → System Prompt
   - Paste the prompt
   - Save

2. **Enable Tehuti Core MCP:**
   - Chat Settings → External Tools
   - Enable "Tehuti Core" (or `server:openapi:tehuti-core`)
   - Verify tools appear in "AVAILABLE TOOLS IN THIS CHAT SESSION:" section

3. **Run each test question** and verify expected behavior

4. **Check for violations:**
   - ❌ Making up tools
   - ❌ Querying gitMaat unnecessarily
   - ❌ Not using tools when needed
   - ❌ Summarizing tool list instead of copying exactly

---

## Success Criteria

✅ **PASS if:**
- Copies tool list exactly from system message
- Uses tools directly when appropriate
- Queries gitMaat only when context is needed
- Never makes up tools or information
- Follows Maat principles (Truth, Balance, Order)

❌ **FAIL if:**
- Makes up tools or services
- Queries gitMaat for simple questions
- Doesn't use tools when needed
- Summarizes instead of copying exactly
- Violates Maat Truth (provides false information)

