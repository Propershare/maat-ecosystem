#!/usr/bin/env python3
"""
Fine-tune Uncensored Llama 3.1:8b for Maat Alignment with Tool Training
This script fine-tunes the uncensored model with your tool calling examples
"""

import os
import sys
from pathlib import Path

# Set PyTorch memory optimization
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from unsloth import FastLanguageModel
from datasets import load_dataset
from trl import SFTTrainer
from transformers import TrainingArguments
import torch

print("🚀 Starting Maat Alignment Fine-Tuning for Uncensored Llama 3.1:8b")
print("   Training on tool calling examples for better Maat alignment")
print("=" * 60)

# Configuration
TRAINING_DATA_RAW = project_root / "fine-tuned-models" / "combined_training.jsonl"  # Original (has 2 errors)
TRAINING_DATA = project_root / "fine-tuned-models" / "combined_training_fixed.jsonl"  # Fixed version (clean)
OUTPUT_DIR = project_root / "fine-tuned-models" / "tehuti-lab-llama3.1-8b-uncensored-maat"

# For fine-tuning, we use HuggingFace format
# The uncensored model from Ollama is GGUF, so we use the base uncensored from HF if available
# Otherwise, use standard Llama 3.1 Instruct (uncensored behavior comes from training)
BASE_MODEL = "unsloth/Llama-3.1-8B-Instruct-bnb-4bit"  # Will try to find uncensored version

# Check if uncensored HuggingFace model exists
# Try uncensored version first, fallback to standard
UNCENSORED_MODELS = [
    "Duggles/Llama-3.1-8B-Instruct-Uncensored",  # If available on HF
    "unsloth/Llama-3.1-8B-Instruct-bnb-4bit",    # Standard (uncensored via training)
]

print("\n📋 Model Selection:")
print("   Note: Fine-tuning requires HuggingFace format, not GGUF")
print("   Using standard Llama 3.1 Instruct - uncensored behavior from training data")
print(f"   Base model: {BASE_MODEL}")

# Check and validate training data
if not TRAINING_DATA.exists():
    if TRAINING_DATA_RAW.exists():
        print(f"🔍 Cleaning training data from {TRAINING_DATA_RAW}...")
        import json
        valid_lines = []
        errors = []
        
        with open(TRAINING_DATA_RAW, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    # Validate required fields
                    if isinstance(data, dict) and ('instruction' in data or 'text' in data):
                        valid_lines.append(line)
                    else:
                        errors.append((line_num, "Missing required fields"))
                except json.JSONDecodeError as e:
                    errors.append((line_num, str(e)))
        
        if errors:
            print(f"⚠️  Found {len(errors)} errors, removing invalid lines...")
            for line_num, error in errors:
                print(f"   Line {line_num}: {error}")
        
        # Write cleaned file
        with open(TRAINING_DATA, 'w', encoding='utf-8') as f:
            for line in valid_lines:
                f.write(line + '\n')
        
        print(f"✅ Cleaned training data: {len(valid_lines)} valid lines")
        print(f"   Removed {len(errors)} invalid lines")
    else:
        print(f"❌ Training data not found: {TRAINING_DATA}")
        sys.exit(1)

# Validate cleaned training data
print(f"\n📚 Training data: {TRAINING_DATA} ({TRAINING_DATA.stat().st_size / 1024:.1f} KB)")
print("🔍 Validating JSON syntax...")
import json
validation_errors = []
with open(TRAINING_DATA, 'r', encoding='utf-8') as f:
    for line_num, line in enumerate(f, 1):
        line = line.strip()
        if not line:
            continue
        try:
            json.loads(line)
        except json.JSONDecodeError as e:
            validation_errors.append((line_num, str(e)))

if validation_errors:
    print(f"❌ Found {len(validation_errors)} JSON syntax errors in cleaned file:")
    for line_num, error in validation_errors:
        print(f"   Line {line_num}: {error}")
    sys.exit(1)
else:
    print("✅ All JSON lines are valid!")

# Load model with Unsloth optimizations
print("\n📥 Loading Llama 3.1:8b with Unsloth optimizations...")
print("⚠️  Using 4-bit pre-quantized model for memory efficiency...")

# Clear any cached models to avoid conflicts
torch.cuda.empty_cache()

model, tokenizer = FastLanguageModel.from_pretrained(
    model_name=BASE_MODEL,
    max_seq_length=2048,  # Reduced for memory
    dtype=None,  # Auto-detect
    load_in_4bit=True,  # Use 4-bit quantization
)

# Add LoRA adapters for efficient fine-tuning
print("\n🔧 Adding LoRA adapters for efficient fine-tuning...")
model = FastLanguageModel.get_peft_model(
    model,
    r=16,  # LoRA rank
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                    "gate_proj", "up_proj", "down_proj"],
    lora_alpha=16,
    lora_dropout=0.05,
    bias="none",
    use_gradient_checkpointing=True,
    random_state=3407,
)

# Load training dataset
print(f"\n📖 Loading training dataset from {TRAINING_DATA}...")
dataset = load_dataset("json", data_files=str(TRAINING_DATA), split="train")

# Format dataset for instruction tuning (same format as original fine_tune_maat.py)
print("📝 Formatting dataset for instruction tuning...")
def format_prompt(example):
    """Format training example for instruction tuning"""
    instruction = example.get("instruction", "")
    output = example.get("output", "")
    
    # Format as instruction-response pair
    formatted = f"""Below is an instruction that describes a task. Write a response that appropriately completes the request.

### Instruction:
{instruction}

### Response:
{output}"""
    return {"text": formatted}

dataset = dataset.map(format_prompt, remove_columns=dataset.column_names)

print(f"✅ Loaded and formatted {len(dataset)} training examples")

# Training arguments
training_args = TrainingArguments(
    per_device_train_batch_size=2,
    gradient_accumulation_steps=4,
    warmup_steps=5,
    num_train_epochs=3,
    learning_rate=2e-4,
    fp16=not torch.cuda.is_bf16_supported(),
    bf16=torch.cuda.is_bf16_supported(),
    logging_steps=1,
    optim="adamw_8bit",
    weight_decay=0.01,
    lr_scheduler_type="linear",
    seed=3407,
    output_dir=str(OUTPUT_DIR),
    save_strategy="epoch",
    save_total_limit=2,
)

# Create trainer
print("\n🏋️  Starting training...")
trainer = SFTTrainer(
    model=model,
    train_dataset=dataset,
    dataset_text_field="text",  # Adjust if your dataset uses different field
    max_seq_length=2048,
    tokenizer=tokenizer,
    args=training_args,
)

# Train
print("\n🚀 Training in progress...")
print("   This may take 30-60 minutes depending on GPU...")
trainer.train()

# Save model
print(f"\n💾 Saving fine-tuned model to {OUTPUT_DIR}...")
model.save_pretrained(str(OUTPUT_DIR))
tokenizer.save_pretrained(str(OUTPUT_DIR))

print("\n✅ Fine-tuning complete!")
print(f"📁 Model saved to: {OUTPUT_DIR}")
print("\n📋 Next steps:")
print("   1. Export to GGUF: python3 scripts/export-to-ollama.py")
print("   2. Convert to Ollama: Use convert-to-gguf-complete.py")
print("   3. Import to Ollama: ollama create tehuti-uncensored-maat -f Modelfile")
print("")

