# Maat Tool Audit and Training Documentation

**Created**: 2025-12-25  
**Purpose**: Comprehensive Maat-aligned documentation and training data for all MCP tools  
**Maat Alignment**: Truth, Balance, Order, Justice, Self-Reflection

## Overview

This directory contains complete documentation and training data for all 11 MCP servers (104 total tools) in the Tehuti Lab ecosystem. The documentation follows Maat principles and is structured for fine-tuning with Unsloth.

## Maat Audit Summary

### Tool Inventory

- **Total Servers**: 11
- **Total Tools**: 104
- **Training Examples**: 11+ (expandable)
- **Documentation**: Complete for all servers

### Server Breakdown

| Server | Port | Tools | Category |
|--------|------|-------|----------|
| Tehuti Core | 8014 | 6 | System Operations |
| Tehuti Curriculum | 8011 | 3 | Education |
| Tehuti Research | 8012 | 3 | Research |
| Tehuti Integration | 8013 | 4 | Integration |
| n8n MCP | 8015 | 20 | Workflow Automation |
| Filesystem MCP | 8016 | 14 | File Operations |
| Postgres MCP | 8017 | 1 | Database |
| Memory MCP | 8018 | 9 | Memory Management |
| ComfyUI Intelligent | 8019 | 30 | Image Generation |
| MaatLangChain Pipeline | 8020 | 7 | AI/RAG |
| Tehuti Audio | 8021 | 7 | Audio Generation |

## Directory Structure

```
training/
├── README.md                    # This file - Master index
├── mcp-servers/                 # Individual server documentation
│   ├── {server-id}/
│   │   ├── README.md           # Maat-aligned tool documentation
│   │   ├── openapi.json        # Full OpenAPI specification
│   │   └── maat-metadata.json  # Enhanced metadata with Maat principles
├── examples/                    # Training examples in Unsloth format
│   ├── tool-calling-examples.jsonl      # Single tool usage
│   ├── multi-tool-examples.jsonl        # Tool chaining
│   └── error-handling-examples.jsonl    # Error recovery
└── schemas/                     # Tool schemas and metadata
    ├── all-tools-index.json    # Complete tool index (104 tools)
    └── tool-relationships.json  # Tool dependencies and chains
```

## Maat Principles Applied

### Truth (Maat)
- **Accurate Documentation**: All tool descriptions verified from OpenAPI specs
- **Verified Parameters**: Parameter types and return values documented
- **Evidence-Based**: Use cases based on actual tool capabilities

### Balance (Maat)
- **Tool Selection Guidance**: When to use which tool
- **Alternative Recommendations**: Trade-offs documented
- **Appropriate Usage**: Balance between tool power and safety

### Order (Maat)
- **Systematic Organization**: Categorized structure (mcp-servers/, examples/, schemas/)
- **Clear Structure**: Each server has README, OpenAPI spec, and metadata
- **Workflow Patterns**: Common tool chaining patterns documented

### Justice (Maat)
- **Proper Attribution**: Tool sources and dependencies documented
- **Prerequisite Requirements**: Dependencies clearly stated
- **Credit Where Due**: MaatCode powers properly attributed

### Self-Reflection (Maat)
- **Common Error Patterns**: Error scenarios documented
- **Best Practices**: Learning from past usage
- **Continuous Improvement**: Training examples for learning

## Tool Categories

### System Operations
- **Tehuti Core**: Terminal, Python execution, gitMaat queries, file operations
- **Filesystem MCP**: Secure file operations with access control

### Workflow & Automation
- **n8n MCP**: Workflow discovery, validation, creation, execution
- **Tehuti Integration**: n8n, filesystem, database integration

### Data & Storage
- **Postgres MCP**: Database operations
- **Memory MCP**: Memory management and retrieval

### AI & Generation
- **MaatLangChain Pipeline**: RAG, agents, knowledge base
- **ComfyUI Intelligent**: Image generation and editing
- **Tehuti Audio**: Text-to-speech, multilingual, music generation

### Research & Education
- **Tehuti Research**: Research methodologies and analysis
- **Tehuti Curriculum**: Curriculum and learning paths

## Training Data Format

All training examples use **Unsloth-optimized format**:

```json
{
  "instruction": "User request",
  "input": "Context or additional info",
  "output": "Assistant response with tool calls",
  "tool_calls": [
    {
      "tool": "tool_name",
      "parameters": {...}
    }
  ],
  "maat_alignment": {
    "truth": "...",
    "balance": "...",
    "order": "...",
    "justice": "...",
    "self_reflection": "..."
  }
}
```

### Example Types

1. **Single Tool Examples** (`tool-calling-examples.jsonl`)
   - Basic tool usage
   - Parameter examples
   - Simple workflows

2. **Multi-Tool Examples** (`multi-tool-examples.jsonl`)
   - Tool chaining patterns
   - Complex workflows
   - Sequential operations

3. **Error Handling Examples** (`error-handling-examples.jsonl`)
   - Error recovery patterns
   - Graceful failure handling
   - User-friendly error messages

## Usage for Fine-Tuning

### Prerequisites

1. **Unsloth installed**: `pip install unsloth`
2. **Base model**: Your existing law-trained model
3. **Training data**: Use examples from `examples/` directory

### Fine-Tuning Steps

1. **Prepare Training Data**:
   ```bash
   # Combine all examples
   cat examples/*.jsonl > combined_training.jsonl
   ```

2. **Load Model with Unsloth**:
   ```python
   from unsloth import FastLanguageModel
   model, tokenizer = FastLanguageModel.from_pretrained(
       model_name="your-model-name",
       max_seq_length=4096,
       dtype=None,
       load_in_4bit=True,
   )
   ```

3. **Prepare Dataset**:
   ```python
   from datasets import load_dataset
   dataset = load_dataset("json", data_files="combined_training.jsonl")
   ```

4. **Fine-Tune**:
   ```python
   from trl import SFTTrainer
   trainer = SFTTrainer(
       model=model,
       train_dataset=dataset,
       dataset_text_field="text",
       max_seq_length=4096,
       tokenizer=tokenizer,
   )
   trainer.train()
   ```

### Training Recommendations

- **Start with single tool examples**: Learn basic tool calling
- **Add multi-tool examples**: Learn tool chaining
- **Include error handling**: Learn graceful failure
- **Iterate based on results**: Add more examples as needed

## Tool Selection Decision Tree

1. **Identify Task Domain**
   - System operations → `tehuti-core`
   - Workflow automation → `n8n-mcp`
   - File operations → `filesystem-mcp`
   - Database queries → `postgres-mcp`
   - Image generation → `comfyui-intelligent`
   - Audio generation → `tehuti-audio`
   - RAG/Knowledge → `maatlangchain-pipeline`

2. **Check Tool Availability**
   - Verify server is running (port check)
   - Check OpenAPI spec for available operations

3. **Select Appropriate Tool**
   - Match user intent to tool capability
   - Consider tool chaining for complex tasks

4. **Execute with Maat Principles**
   - **Truth**: Accurate parameters
   - **Balance**: Appropriate tool selection
   - **Order**: Systematic execution
   - **Justice**: Proper attribution
   - **Self-Reflection**: Learn from results

## Common Tool Chains

### File Processing Chain
```
read_file → run_python_code → write_file
(filesystem-mcp → tehuti-core → filesystem-mcp)
```

### Workflow Creation Chain
```
search_nodes → get_docs → validate → create_workflow
(n8n-mcp → n8n-mcp → n8n-mcp → n8n-mcp)
```

### Task Coordination Chain
```
query_gitmaat → execute_command → log_result
(tehuti-core → tehuti-core → tehuti-core)
```

### Image Generation Chain
```
generate_workflow → execute_workflow → get_image
(comfyui-intelligent → comfyui-intelligent → comfyui-intelligent)
```

## Maintenance

### Adding New Tools

1. Fetch OpenAPI spec: `curl http://127.0.0.1:{port}/openapi.json > mcp-servers/{server-id}/openapi.json`
2. Run documentation generator: `python3 generate_documentation.py`
3. Update schemas: `python3 generate_schemas.py`
4. Add training examples: Add to `examples/*.jsonl` files

### Updating Documentation

1. Update `generate_documentation.py` with new server metadata
2. Regenerate: `python3 generate_documentation.py`
3. Update this README with new tool counts

### Expanding Training Examples

1. Add examples to appropriate `examples/*.jsonl` file
2. Follow Unsloth format
3. Include Maat alignment metadata
4. Test examples before training

## Files Reference

### Core Documentation
- `mcp-servers/{server-id}/README.md` - Per-server documentation
- `mcp-servers/{server-id}/openapi.json` - OpenAPI specification
- `mcp-servers/{server-id}/maat-metadata.json` - Enhanced metadata

### Training Data
- `examples/tool-calling-examples.jsonl` - Single tool examples
- `examples/multi-tool-examples.jsonl` - Tool chaining examples
- `examples/error-handling-examples.jsonl` - Error recovery examples

### Schemas
- `schemas/all-tools-index.json` - Complete tool index (104 tools)
- `schemas/tool-relationships.json` - Tool dependencies and chains

## Maat Alignment Verification

This documentation follows Maat principles:

- ✅ **Truth**: All tool descriptions verified from OpenAPI specs
- ✅ **Balance**: Tool selection guidance and alternatives documented
- ✅ **Order**: Systematic organization and clear structure
- ✅ **Justice**: Proper attribution and dependency documentation
- ✅ **Self-Reflection**: Error patterns and best practices included

## Next Steps

1. **Review Documentation**: Check each server's README.md
2. **Expand Examples**: Add more training examples (target: 50+)
3. **Fine-Tune Model**: Use examples with Unsloth
4. **Test Tool Calling**: Verify model understands tool selection
5. **Iterate**: Add examples based on model performance

## Contact & Support

For questions or issues:
- Check individual server README.md files
- Review `schemas/all-tools-index.json` for tool reference
- See `schemas/tool-relationships.json` for chaining patterns

---

**Maat Alignment**: This documentation embodies Maat principles of Truth, Balance, Order, Justice, and Self-Reflection in tool documentation and training data preparation.

**Sankofa Principle**: "Go back and get it" - Learn from past tool usage patterns to build better tool calling capabilities.

