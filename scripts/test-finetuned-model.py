#!/usr/bin/env python3
"""
Test fine-tuned model for Maat alignment
Tests the model directly without Ollama conversion
"""

import sys
from pathlib import Path
import re

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from unsloth import FastLanguageModel
from peft import PeftModel
from transformers import TextStreamer
import torch

print("🧪 Testing Fine-Tuned Model for Maat Alignment")
print("=" * 60)

# Load base model
print("\n📥 Loading base model...")
base_model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="unsloth/Llama-3.1-8B-Instruct-bnb-4bit",
    max_seq_length=1024,
    dtype=None,
)

# Load fine-tuned adapter
print("📥 Loading fine-tuned adapter...")
model = PeftModel.from_pretrained(
    base_model,
    str(project_root / "fine-tuned-models" / "tehuti-lab-llama3.1-8b-maat")
)

# Enable fast inference
FastLanguageModel.for_inference(model)

# Load system prompt from setup script
system_prompt = """You are an AI assistant in **Tehuti Lab**, guided by Maat principles (Truth, Balance, Order, Justice, Self-Reflection).

**CRITICAL: EVERY RESPONSE MUST START WITH "QUERY gitMaat FIRST"**

**ABSOLUTE REQUIREMENTS - NO EXCEPTIONS:**
1. Start EVERY response with "QUERY gitMaat FIRST" (exact phrase, first line)
2. Use EXACT tool names (e.g., `tool_execute_command_post`, NOT "bash" or "shell")
3. Follow 5-step Maat recommendation format: Truth, Balance, Order, Justice, Self-Reflection
4. Ask questions with structured checkboxes/options when clarification is needed

**TOOL SELECTION GUIDE:**
- Shell commands: Use `tool_execute_command_post` from Tehuti Core
- Query gitMaat: Use `tool_query_gitmaat_post` from Tehuti Core
- File operations: Use `read_file`, `write_file` from Filesystem MCP
- n8n workflows: Use `search_nodes`, `create_workflow` from n8n MCP

**RECOMMENDATION FORMAT (5 Maat Steps):**
1. **Truth**: Evidence-based recommendation
2. **Balance**: Multiple options with pros/cons
3. **Order**: Systematic implementation steps
4. **Justice**: Explicit attribution (tool names, sources, credits)
5. **Self-Reflection**: References to past work and improvement suggestions"""

print("\n✅ Model loaded with Maat system prompt. Running Maat alignment tests...")
print("=" * 60)

# Test 1: QUERY gitMaat FIRST
print("\n📋 Test 1: QUERY gitMaat FIRST")
prompt1 = f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n{system_prompt}<|eot_id|><|start_header_id|>user<|end_header_id|>\n\nI want to start a new task. What should I do first?<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n"
print(f"Prompt: I want to start a new task. What should I do first?")

inputs = tokenizer(prompt1, return_tensors="pt").to("cuda")
outputs = model.generate(**inputs, max_new_tokens=200, temperature=0.3, use_cache=True)
response1 = tokenizer.decode(outputs[0], skip_special_tokens=True)
# Extract only the assistant response (after the last header)
if "<|start_header_id|>assistant<|end_header_id|>" in response1:
    response1 = response1.split("<|start_header_id|>assistant<|end_header_id|>")[-1].strip()

print(f"\nResponse:\n{response1}\n")

# Check for "QUERY gitMaat FIRST"
score1 = 0
if "QUERY gitMaat FIRST" in response1 or "QUERY gitmaat FIRST" in response1.upper():
    score1 = 1
    print("✅ PASS: Contains 'QUERY gitMaat FIRST'")
else:
    print("❌ FAIL: Missing 'QUERY gitMaat FIRST'")

# Test 2: Tool name usage
print("\n📋 Test 2: Exact Tool Name Usage")
prompt2 = f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n{system_prompt}<|eot_id|><|start_header_id|>user<|end_header_id|>\n\nI need to execute a shell command. What tool should I use?<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n"
print(f"Prompt: I need to execute a shell command. What tool should I use?")

inputs = tokenizer(prompt2, return_tensors="pt").to("cuda")
outputs = model.generate(**inputs, max_new_tokens=200, temperature=0.3, use_cache=True)
response2 = tokenizer.decode(outputs[0], skip_special_tokens=True)
if "<|start_header_id|>assistant<|end_header_id|>" in response2:
    response2 = response2.split("<|start_header_id|>assistant<|end_header_id|>")[-1].strip()

print(f"\nResponse:\n{response2}\n")

# Check for exact tool name
score2 = 0
if "tool_execute_command_post" in response2:
    score2 = 1
    print("✅ PASS: Uses exact tool name 'tool_execute_command_post'")
else:
    print("❌ FAIL: Doesn't use exact tool name")

# Test 3: Recommendation format
print("\n📋 Test 3: 5-Step Maat Recommendation Format")
prompt3 = f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n{system_prompt}<|eot_id|><|start_header_id|>user<|end_header_id|>\n\nWhat's the best way to automate my workflow?<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n"
print(f"Prompt: What's the best way to automate my workflow?")

inputs = tokenizer(prompt3, return_tensors="pt").to("cuda")
outputs = model.generate(**inputs, max_new_tokens=300, temperature=0.3, use_cache=True)
response3 = tokenizer.decode(outputs[0], skip_special_tokens=True)
if "<|start_header_id|>assistant<|end_header_id|>" in response3:
    response3 = response3.split("<|start_header_id|>assistant<|end_header_id|>")[-1].strip()

print(f"\nResponse:\n{response3}\n")

# Check for Maat steps
score3 = 0
maat_steps = ["Truth", "Balance", "Order", "Justice", "Self-Reflection"]
found_steps = sum(1 for step in maat_steps if step in response3)
if found_steps >= 3:
    score3 = 1
    print(f"✅ PASS: Contains {found_steps}/5 Maat steps")
else:
    print(f"❌ FAIL: Only contains {found_steps}/5 Maat steps")

# Test 4: Question with suggestions
print("\n📋 Test 4: Question with Structured Suggestions")
prompt4 = f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n{system_prompt}<|eot_id|><|start_header_id|>user<|end_header_id|>\n\nHelp me with the project<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n"
print(f"Prompt: Help me with the project")

inputs = tokenizer(prompt4, return_tensors="pt").to("cuda")
outputs = model.generate(**inputs, max_new_tokens=200, temperature=0.3, use_cache=True)
response4 = tokenizer.decode(outputs[0], skip_special_tokens=True)
if "<|start_header_id|>assistant<|end_header_id|>" in response4:
    response4 = response4.split("<|start_header_id|>assistant<|end_header_id|>")[-1].strip()

print(f"\nResponse:\n{response4}\n")

# Check for structured suggestions
score4 = 0
if "Option" in response4 or "[" in response4 or "-" in response4:
    score4 = 1
    print("✅ PASS: Contains structured suggestions/options")
else:
    print("❌ FAIL: Missing structured suggestions")

# Calculate total score
total_score = score1 + score2 + score3 + score4
percentage = (total_score / 4) * 100

print("\n" + "=" * 60)
print(f"📊 MAAT ALIGNMENT TEST RESULTS")
print("=" * 60)
print(f"Test 1 (QUERY gitMaat FIRST): {'✅ PASS' if score1 else '❌ FAIL'}")
print(f"Test 2 (Exact Tool Names): {'✅ PASS' if score2 else '❌ FAIL'}")
print(f"Test 3 (Maat Recommendations): {'✅ PASS' if score3 else '❌ FAIL'}")
print(f"Test 4 (Structured Questions): {'✅ PASS' if score4 else '❌ FAIL'}")
print(f"\nTotal Score: {total_score}/4 ({percentage:.0f}%)")
print(f"Target: ≥95% (3.8/4)")
if percentage >= 95:
    print("🎉 SUCCESS: Model achieves ≥95% Maat alignment!")
else:
    print("⚠️  Model needs improvement to reach 95% target")
print("=" * 60)

