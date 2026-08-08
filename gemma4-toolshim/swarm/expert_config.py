"""
🧠 Expert Model Configuration — Made Simple

This is where you define your AI experts. Each expert is like hiring
a specialist employee who's really good at one thing.

HOW TO USE:
1. Copy one of the examples below
2. Change the name, description, and what tools it can use
3. Run: python3 expert_config.py --test
4. That's it! Your new expert is ready.

No complex setup. No YAML nightmares. Just Python dictionaries.
"""

# ─── Your Experts ──────────────────────────────────────────────────
#
# Each expert needs:
#   name        → what you call it (no spaces, use dashes)
#   description → what it's good at (plain English)
#   tools       → which MCP tools it can use (see AVAILABLE TOOLS below)
#   keywords    → words that trigger this expert (helps the router)
#   model       → the fine-tuned model name (starts as "gemma4:e4b" for all)
#
# That's it. Five fields. Done.

EXPERTS = [

    # ── Scout / Analyst / Archivist (Maat triad) ───────────────
    # Operating line: Scout finds → Analyst decides → Archivist remembers.
    # Archivist is structured-first (JSON, tags, sources, timestamps); see
    # docs/SCOUT-ANALYST-ARCHIVIST.md
    {
        "name": "scout",
        "role": "scout",
        "description": (
            "Finds and gathers: search files, read sources, list evidence. "
            "Outputs pointers and raw findings, not final decisions."
        ),
        "model": "gemma4:e4b",
        "output_mode": "structured_json",
        "tools": [
            "read_file",
            "read_multiple_files",
            "search_files",
            "list_directory",
            "directory_tree",
            "grep",
            "glob",
            "query_gitmaat",
            "execute_command",
        ],
        "keywords": [
            "scout", "find", "gather", "discover", "list files", "search for",
            "where is", "pull up", "show me sources", "evidence", "locate",
        ],
    },
    {
        "name": "analyst",
        "role": "analyst",
        "description": (
            "Decides: tradeoffs, recommendations, risks, prioritization. "
            "Consumes scout output; produces clear judgment (not storage format)."
        ),
        "model": "gemma4:e4b",
        "output_mode": "structured_json",
        "tools": [
            "read_file",
            "grep",
            "glob",
            "query_gitmaat",
            "run_python_code",
        ],
        "keywords": [
            "analyst", "decide", "recommend", "should we", "tradeoff",
            "prioritize", "evaluate", "risk", "compare", "conclude",
            "what do you think",
        ],
    },
    {
        "name": "archivist",
        "role": "archivist",
        "description": (
            "Remembers: persist to gitMaat with STRUCTURED output first—valid JSON, "
            "canonical tags, ISO timestamps, source links, compact summaries—not chat. "
            "Behaves like a database interface."
        ),
        "model": "gemma4:e4b",
        "output_mode": "structured_json",
        "tools": [
            "log_gitmaat_task",
            "log_gitmaat_change",
            "log_gitmaat_decision",
            "log_gitmaat_learning",
            "query_gitmaat",
            "read_file",
        ],
        "keywords": [
            "archivist", "remember", "archive", "record", "persist", "store in maat",
            "log to gitmaat", "save this", "tag", "citation", "timestamp",
            "structured", "json record",
        ],
    },

    # ── 🧠 Knowledge Expert ─────────────────────────────────
    {
        "name": "rag-expert",
        "description": "Finds information, answers questions from documents and memory",
        "model": "gemma4:e4b",  # Change to "gemma4-rag:latest" after fine-tuning
        "tools": [
            "query_gitmaat",        # Search your knowledge base
            "read_file",            # Read documents
            "search_files",         # Find files by content
            "read_multiple_files",  # Read several files at once
        ],
        "keywords": [
            "find", "search", "look up", "what is", "tell me about",
            "remember", "document", "knowledge", "history", "context",
            "who", "when", "where", "why",
        ],
    },

    # ── 💻 Code Expert ───────────────────────────────────────
    {
        "name": "code-expert",
        "description": "Writes code, creates files, fixes bugs, builds things",
        "model": "gemma4:e4b",
        "tools": [
            "write_file",     # Create new files
            "edit_file",      # Modify existing files
            "bash",           # Run shell commands
            "read_file",      # Read source code
            "glob",           # Find files by pattern
            "grep",           # Search inside files
        ],
        "keywords": [
            "code", "program", "script", "function", "class", "bug",
            "fix", "create", "build", "python", "javascript", "file",
            "implement", "refactor", "test",
        ],
    },

    # ── ⚡ Ops Expert ────────────────────────────────────────
    {
        "name": "ops-expert",
        "description": "Manages servers, runs automations, monitors systems",
        "model": "gemma4:e4b",
        "tools": [
            "execute_command",   # Run system commands
            "get_system_info",   # Check CPU, memory, disk
            "bash",              # Shell access
            "list_directory",    # Browse files
        ],
        "keywords": [
            "server", "deploy", "monitor", "disk", "memory", "cpu",
            "service", "restart", "install", "update", "docker",
            "process", "log", "error", "status",
        ],
    },

    # ── 🎨 Creative Expert ───────────────────────────────────
    # Uncomment when you have ComfyUI set up
    # {
    #     "name": "creative-expert",
    #     "description": "Generates images, creates visual content",
    #     "model": "gemma4:e4b",
    #     "tools": [
    #         "comfyui_generate",    # Generate images
    #         "comfyui_workflows",   # List/run workflows
    #     ],
    #     "keywords": [
    #         "image", "picture", "draw", "generate", "art",
    #         "visual", "design", "photo", "illustration",
    #     ],
    # },

]


# ─── Available MCP Tools ───────────────────────────────────────────
#
# These are the tools your experts can use. Copy tool names from here
# into an expert's "tools" list above.
#
# From Tehuti Core (port 8014):
#   execute_command       → Run any shell command
#   run_python_code       → Execute Python code
#   get_system_info       → CPU, memory, disk info
#   list_directory        → List files in a folder
#   read_file             → Read a single file
#   write_file            → Create/overwrite a file
#   edit_file             → Edit part of a file
#   create_directory      → Make a new folder
#   read_multiple_files   → Read several files at once
#   search_files          → Search for files
#   move_file             → Move/rename files
#   directory_tree        → Show folder structure
#   get_file_info         → File size, dates, etc.
#
# From gitMaat:
#   query_gitmaat         → Search knowledge base
#   log_gitmaat_task      → Log a task
#   log_gitmaat_change    → Log a change
#   log_gitmaat_decision  → Log a decision
#   log_gitmaat_learning  → Log something learned
#
# From OpenCode built-in:
#   bash                  → Shell commands
#   read                  → Read files
#   write                 → Write files
#   edit                  → Edit files
#   glob                  → Find files by pattern
#   grep                  → Search file contents
#   task                  → Spawn sub-tasks
#   webfetch              → Fetch web pages
#
# From n8n (port 8015):
#   (check your n8n MCP for available workflow triggers)
#
# From Postgres (port 8017):
#   (SQL query tools — check your postgres MCP)
#


# ─── Settings ──────────────────────────────────────────────────────

SETTINGS = {
    # Which Ollama model to use when a fine-tuned expert isn't ready yet
    "fallback_model": "gemma4:e4b",

    # Ollama connection
    "ollama_url": "http://localhost:11434",

    # Shim proxy (translates gemma4 thinking → tool calls)
    "shim_url": "http://localhost:11435",

    # How confident the router needs to be (0-100)
    # Lower = more likely to pick an expert (even if not sure)
    # Higher = more likely to use fallback general model
    "routing_confidence_threshold": 20,
}


# ─── Don't edit below unless you know what you're doing ────────────

def load_experts():
    """Load and validate expert configs."""
    validated = []
    for i, expert in enumerate(EXPERTS):
        # Check required fields
        required = ["name", "description", "model", "tools", "keywords"]
        missing = [f for f in required if f not in expert]
        if missing:
            print(f"⚠️  Expert #{i} missing fields: {missing} — skipping")
            continue

        # Clean up
        expert["name"] = expert["name"].strip().lower()
        expert["keywords"] = [k.lower().strip() for k in expert["keywords"]]
        expert["tools"] = [t.strip() for t in expert["tools"]]

        validated.append(expert)
        print(f"  ✅ {expert['name']}: {expert['description']}")

    return validated


def route_message(message: str, experts: list = None) -> dict:
    """
    Pick the best expert for a message.

    Args:
        message: What the user said
        experts: List of expert configs (uses EXPERTS if not provided)

    Returns:
        The best matching expert config
    """
    if experts is None:
        experts = EXPERTS

    message_lower = message.lower()
    best_score = 0
    best_expert = None

    for expert in experts:
        score = 0
        for keyword in expert["keywords"]:
            if keyword in message_lower:
                score += 1

        if score > best_score:
            best_score = score
            best_expert = expert

    # If no good match, return first expert as default
    if best_expert is None or best_score < 1:
        return experts[0] if experts else None

    return best_expert


# ─── Quick Test ────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    print("🧠 Expert Swarm — Configuration Check\n")
    print("Loading experts...")
    experts = load_experts()
    print(f"\n{len(experts)} expert(s) ready.\n")

    if "--test" in sys.argv:
        print("─── Routing Test ───\n")
        test_messages = [
            "What did we decide about the API last week?",
            "Create a Python script that sorts numbers",
            "Check how much disk space we have",
            "Search for all files about authentication",
            "Fix the bug in the login function",
            "Restart the nginx service",
            "What's in the knowledge base about Maat?",
            "Scout: gather sources on authentication configs",
            "Analyst: should we merge this PR given the risks?",
            "Archivist: persist this decision as a structured JSON record with tags",
        ]
        for msg in test_messages:
            expert = route_message(msg, experts)
            print(f"  [{expert['name']}] → {msg}")

        print("\n✅ All tests passed! Your experts are configured correctly.")

    if "--add" in sys.argv:
        print("\n─── Add New Expert (Interactive) ───\n")
        print("Edit the EXPERTS list in this file to add a new expert.")
        print("Copy one of the existing examples and change the values.")
        print("Then run: python3 expert_config.py --test")

    if len(sys.argv) == 1:
        print("Usage:")
        print("  python3 expert_config.py --test    Test your expert configs")
        print("  python3 expert_config.py --add     Help adding a new expert")
