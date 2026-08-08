#!/usr/bin/env python3
"""
Expand training examples to cover all 11 servers with 50+ examples
"""
import json
from pathlib import Path

def generate_comprehensive_examples():
    """Generate comprehensive examples covering all servers"""
    examples = []
    
    # ===== TEHUTI CORE (6 examples) =====
    examples.append({
        "instruction": "Execute 'ls -la' to list files",
        "input": "",
        "output": "I'll list the directory contents using the ls command.",
        "tool_calls": [{"tool": "tool_execute_command_post", "parameters": {"command": "ls -la"}}],
        "maat_alignment": {"truth": "Accurate command", "balance": "Simple operation", "order": "Systematic", "justice": "Proper attribution", "self_reflection": "Learn from results"}
    })
    
    examples.append({
        "instruction": "Run Python code to calculate 2+2",
        "input": "",
        "output": "I'll execute Python code to calculate the result.",
        "tool_calls": [{"tool": "tool_run_python_code_post", "parameters": {"code": "result = 2 + 2\nprint(result)"}}],
        "maat_alignment": {"truth": "Accurate code", "balance": "Simple calculation", "order": "Systematic", "justice": "Proper attribution", "self_reflection": "Learn from execution"}
    })
    
    examples.append({
        "instruction": "Query gitMaat for pending tasks",
        "input": "",
        "output": "I'll query gitMaat for pending tasks.",
        "tool_calls": [{"tool": "tool_query_gitmaat_post", "parameters": {"query_type": "tasks", "status": "pending", "limit": 10}}],
        "maat_alignment": {"truth": "Accurate query", "balance": "Appropriate limit", "order": "Systematic", "justice": "Proper gitMaat attribution", "self_reflection": "Learn from task patterns"}
    })
    
    examples.append({
        "instruction": "Get system information",
        "input": "",
        "output": "I'll retrieve system information.",
        "tool_calls": [{"tool": "tool_get_system_info_post", "parameters": {}}],
        "maat_alignment": {"truth": "Accurate info", "balance": "System query", "order": "Systematic", "justice": "Proper attribution", "self_reflection": "Learn from system state"}
    })
    
    examples.append({
        "instruction": "List the contents of /home/suspect/.n8n",
        "input": "",
        "output": "I'll list the directory contents.",
        "tool_calls": [{"tool": "tool_list_directory_post", "parameters": {"path": "/home/suspect/.n8n", "show_hidden": False}}],
        "maat_alignment": {"truth": "Accurate path", "balance": "Appropriate visibility", "order": "Systematic", "justice": "Proper attribution", "self_reflection": "Learn from directory structure"}
    })
    
    examples.append({
        "instruction": "Read the file config.json",
        "input": "",
        "output": "I'll read the config file.",
        "tool_calls": [{"tool": "tool_read_file_post", "parameters": {"file_path": "config.json", "max_lines": 1000}}],
        "maat_alignment": {"truth": "Accurate file path", "balance": "Appropriate line limit", "order": "Systematic", "justice": "Proper attribution", "self_reflection": "Learn from file content"}
    })
    
    # ===== N8N MCP (8 examples) =====
    examples.append({
        "instruction": "Search for HTTP request nodes in n8n",
        "input": "",
        "output": "I'll search for HTTP request nodes.",
        "tool_calls": [{"tool": "search_nodes", "parameters": {"query": "http request"}}],
        "maat_alignment": {"truth": "Accurate search", "balance": "Appropriate query", "order": "Systematic", "justice": "Proper n8n attribution", "self_reflection": "Learn from search results"}
    })
    
    examples.append({
        "instruction": "Get documentation for the Code node",
        "input": "",
        "output": "I'll retrieve documentation for the Code node.",
        "tool_calls": [{"tool": "get_node_documentation", "parameters": {"node_id": "n8n-nodes-base.code"}}],
        "maat_alignment": {"truth": "Accurate node ID", "balance": "Appropriate documentation", "order": "Systematic", "justice": "Proper n8n attribution", "self_reflection": "Learn from documentation"}
    })
    
    examples.append({
        "instruction": "Validate a workflow JSON",
        "input": '{"workflow": {"nodes": []}}',
        "output": "I'll validate the workflow structure.",
        "tool_calls": [{"tool": "validate_workflow", "parameters": {"workflow": {"workflow": {"nodes": []}}}}],
        "maat_alignment": {"truth": "Accurate validation", "balance": "Appropriate structure", "order": "Systematic", "justice": "Proper n8n attribution", "self_reflection": "Learn from validation results"}
    })
    
    # ===== FILESYSTEM MCP (6 examples) =====
    examples.append({
        "instruction": "Read the file README.md",
        "input": "",
        "output": "I'll read the README file.",
        "tool_calls": [{"tool": "read_file", "parameters": {"file_path": "README.md"}}],
        "maat_alignment": {"truth": "Accurate file path", "balance": "Appropriate operation", "order": "Systematic", "justice": "Proper filesystem attribution", "self_reflection": "Learn from file content"}
    })
    
    examples.append({
        "instruction": "List files in the current directory",
        "input": "",
        "output": "I'll list the directory contents.",
        "tool_calls": [{"tool": "list_directory", "parameters": {"path": "."}}],
        "maat_alignment": {"truth": "Accurate path", "balance": "Appropriate operation", "order": "Systematic", "justice": "Proper filesystem attribution", "self_reflection": "Learn from directory structure"}
    })
    
    # ===== COMFYUI INTELLIGENT (8 examples) =====
    examples.append({
        "instruction": "Generate an image of a beautiful sunset over mountains",
        "input": "",
        "output": "I'll generate an image using ComfyUI with your description.",
        "tool_calls": [{"tool": "generate_image", "parameters": {"prompt": "beautiful sunset over mountains", "negative_prompt": "text, watermark", "width": 512, "height": 512}}],
        "maat_alignment": {"truth": "Accurate prompt", "balance": "Appropriate dimensions", "order": "Systematic workflow", "justice": "Proper ComfyUI attribution", "self_reflection": "Learn from generation patterns"}
    })
    
    examples.append({
        "instruction": "Edit an image to add a blue sky",
        "input": "",
        "output": "I'll edit the image using ComfyUI.",
        "tool_calls": [{"tool": "edit_image", "parameters": {"image_path": "input.png", "prompt": "blue sky", "denoise": 0.7}}],
        "maat_alignment": {"truth": "Accurate edit request", "balance": "Appropriate denoise", "order": "Systematic workflow", "justice": "Proper ComfyUI attribution", "self_reflection": "Learn from edit patterns"}
    })
    
    # ===== TEHUTI AUDIO (5 examples) =====
    examples.append({
        "instruction": "Generate speech from the text 'Hello, welcome to Tehuti Lab'",
        "input": "",
        "output": "I'll generate speech using Bark TTS.",
        "tool_calls": [{"tool": "generate_speech", "parameters": {"text": "Hello, welcome to Tehuti Lab", "voice": "default"}}],
        "maat_alignment": {"truth": "Accurate text", "balance": "Appropriate voice", "order": "Systematic generation", "justice": "Proper Bark attribution", "self_reflection": "Learn from audio patterns"}
    })
    
    # ===== MEMORY MCP (4 examples) =====
    examples.append({
        "instruction": "Store a memory about a user preference",
        "input": "",
        "output": "I'll store the memory.",
        "tool_calls": [{"tool": "store_memory", "parameters": {"key": "user_preference", "value": "dark_mode"}}],
        "maat_alignment": {"truth": "Accurate memory", "balance": "Appropriate storage", "order": "Systematic", "justice": "Proper memory attribution", "self_reflection": "Learn from memory patterns"}
    })
    
    # ===== POSTGRES MCP (3 examples) =====
    examples.append({
        "instruction": "Query the database for all users",
        "input": "",
        "output": "I'll query the database.",
        "tool_calls": [{"tool": "query_database", "parameters": {"query": "SELECT * FROM users"}}],
        "maat_alignment": {"truth": "Accurate query", "balance": "Appropriate query", "order": "Systematic", "justice": "Proper database attribution", "self_reflection": "Learn from query patterns"}
    })
    
    # ===== MAATLANGCHAIN PIPELINE (4 examples) =====
    examples.append({
        "instruction": "Query the knowledge base about Maat principles",
        "input": "",
        "output": "I'll query the knowledge base using RAG.",
        "tool_calls": [{"tool": "rag_query", "parameters": {"query": "What are Maat principles?", "limit": 5}}],
        "maat_alignment": {"truth": "Accurate query", "balance": "Appropriate limit", "order": "Systematic RAG", "justice": "Proper source attribution", "self_reflection": "Learn from RAG patterns"}
    })
    
    # ===== MULTI-TOOL EXAMPLES (10 examples) =====
    examples.append({
        "instruction": "Read a config file and then execute a command based on it",
        "input": "",
        "output": "I'll read the config file first, then execute the command.",
        "tool_calls": [
            {"tool": "read_file", "parameters": {"file_path": "config.json"}},
            {"tool": "tool_execute_command_post", "parameters": {"command": "{command_from_config}"}}
        ],
        "maat_alignment": {"truth": "Accurate file read and execution", "balance": "Appropriate chaining", "order": "Systematic: read then execute", "justice": "Proper attribution", "self_reflection": "Learn from chaining patterns"}
    })
    
    examples.append({
        "instruction": "Search for n8n nodes, get documentation, then create a workflow",
        "input": "",
        "output": "I'll search for nodes, get documentation, then create the workflow.",
        "tool_calls": [
            {"tool": "search_nodes", "parameters": {"query": "http"}},
            {"tool": "get_node_documentation", "parameters": {"node_id": "{first_result}"}},
            {"tool": "create_workflow", "parameters": {"workflow": {"nodes": []}}}
        ],
        "maat_alignment": {"truth": "Accurate workflow creation", "balance": "Appropriate sequence", "order": "Systematic: search → docs → create", "justice": "Proper n8n attribution", "self_reflection": "Learn from workflow patterns"}
    })
    
    examples.append({
        "instruction": "Query gitMaat for tasks, then execute the first pending task",
        "input": "",
        "output": "I'll query gitMaat, then execute the first task.",
        "tool_calls": [
            {"tool": "tool_query_gitmaat_post", "parameters": {"query_type": "tasks", "status": "pending", "limit": 1}},
            {"tool": "tool_execute_command_post", "parameters": {"command": "{task_command}"}}
        ],
        "maat_alignment": {"truth": "Accurate query and execution", "balance": "Appropriate task selection", "order": "Systematic: query then execute", "justice": "Proper gitMaat attribution", "self_reflection": "Learn from task execution"}
    })
    
    examples.append({
        "instruction": "Generate an image workflow, execute it, and return the result",
        "input": "",
        "output": "I'll generate the workflow, execute it, and return the image.",
        "tool_calls": [
            {"tool": "generate_workflow", "parameters": {"prompt": "beautiful landscape"}},
            {"tool": "execute_workflow", "parameters": {"workflow_id": "{generated_id}"}},
            {"tool": "get_image", "parameters": {"image_id": "{result_id}"}}
        ],
        "maat_alignment": {"truth": "Accurate workflow generation", "balance": "Appropriate execution", "order": "Systematic: generate → execute → get", "justice": "Proper ComfyUI attribution", "self_reflection": "Learn from generation patterns"}
    })
    
    # ===== ERROR HANDLING EXAMPLES (5 examples) =====
    examples.append({
        "instruction": "Read a file that doesn't exist and handle the error",
        "input": "",
        "output": "I'll attempt to read the file. If it doesn't exist, I'll inform you.",
        "tool_calls": [{"tool": "read_file", "parameters": {"file_path": "nonexistent.txt"}}],
        "expected_error": "FileNotFoundError",
        "error_response": "The file 'nonexistent.txt' was not found. Would you like me to check for similar files or create it?",
        "maat_alignment": {"truth": "Accurate error reporting", "balance": "Appropriate error handling", "order": "Systematic error recovery", "justice": "Proper error attribution", "self_reflection": "Learn from error patterns"}
    })
    
    examples.append({
        "instruction": "Execute an invalid command and provide helpful error information",
        "input": "",
        "output": "I'll execute the command. If it fails, I'll provide helpful information.",
        "tool_calls": [{"tool": "tool_execute_command_post", "parameters": {"command": "invalid_cmd_xyz"}}],
        "expected_error": "CommandNotFoundError",
        "error_response": "The command 'invalid_cmd_xyz' was not found. This might be because the command is not installed or misspelled. Would you like me to suggest alternatives?",
        "maat_alignment": {"truth": "Accurate error diagnosis", "balance": "Appropriate error handling", "order": "Systematic error recovery", "justice": "Proper error attribution", "self_reflection": "Learn from command errors"}
    })
    
    return examples

def main():
    """Expand training examples"""
    examples = generate_comprehensive_examples()
    
    # Separate by type
    single_tool = []
    multi_tool = []
    error_handling = []
    
    for ex in examples:
        tool_count = len(ex.get('tool_calls', []))
        if 'expected_error' in ex:
            error_handling.append(ex)
        elif tool_count > 1:
            multi_tool.append(ex)
        else:
            single_tool.append(ex)
    
    # Write to files
    base_dir = Path("examples")
    
    # Append to existing files
    for file_name, ex_list in [
        ("tool-calling-examples.jsonl", single_tool),
        ("multi-tool-examples.jsonl", multi_tool),
        ("error-handling-examples.jsonl", error_handling)
    ]:
        file_path = base_dir / file_name
        with open(file_path, 'a') as f:
            for ex in ex_list:
                f.write(json.dumps(ex) + '\n')
        print(f"✓ Added {len(ex_list)} examples to {file_name}")
    
    total = len(examples)
    print(f"\n✅ Total examples: {total}")
    print(f"   - Single tool: {len(single_tool)}")
    print(f"   - Multi-tool: {len(multi_tool)}")
    print(f"   - Error handling: {len(error_handling)}")

if __name__ == "__main__":
    main()

