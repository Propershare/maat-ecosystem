#!/usr/bin/env python3
"""
Fine-tune Llama 3.1:8b for 95% Maat Alignment using Unsloth
This script fine-tunes the model locally with training examples
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

print("🚀 Starting Maat Alignment Fine-Tuning for Llama 3.1:8b")
print("   (Note: Llama 3.1 only has 8B, 70B, 405B - no 3B model exists)")
print("=" * 60)

# Configuration
# Use Maat judgment training data (natural examples + existing examples)
TRAINING_DATA = project_root / "fine-tuned-models" / "combined_training_maat_judgment.jsonl"
# Fallback to old data if new doesn't exist
if not TRAINING_DATA.exists():
    TRAINING_DATA = project_root / "fine-tuned-models" / "combined_training_fixed.jsonl"
OUTPUT_DIR = project_root / "fine-tuned-models" / "tehuti-lab-llama3.1-8b-maat"
# Use Unsloth's pre-quantized 8B model (official Llama 3.1 only has 8B, 70B, 405B - no 3B)
# This model is already 4-bit quantized and optimized for fine-tuning
BASE_MODEL = "unsloth/Llama-3.1-8B-Instruct-bnb-4bit"

# Check training data exists
if not TRAINING_DATA.exists():
    print(f"❌ Training data not found: {TRAINING_DATA}")
    sys.exit(1)

print(f"📚 Training data: {TRAINING_DATA} ({TRAINING_DATA.stat().st_size / 1024:.1f} KB)")

# Load model with Unsloth optimizations (more aggressive memory settings)
print("\n📥 Loading Llama 3.1:8b with Unsloth optimizations...")
print("⚠️  Using 4-bit pre-quantized model for memory efficiency...")

# Clear any cached models to avoid conflicts
import torch
torch.cuda.empty_cache()

model, tokenizer = FastLanguageModel.from_pretrained(
    model_name=BASE_MODEL,
    max_seq_length=1024,  # Reduced to 1024 to save memory during training
    dtype=None,  # Auto-detect
    # Model is already 4-bit quantized, don't specify load_in_4bit
)

# Add LoRA adapters for efficient fine-tuning (reduced rank to save memory)
print("🔧 Adding LoRA adapters...")
model = FastLanguageModel.get_peft_model(
    model,
    r=8,  # Reduced LoRA rank from 16 to 8 to save memory
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj",
                    "gate_proj", "up_proj", "down_proj"],
    lora_alpha=8,  # Reduced to match rank
    lora_dropout=0.1,
    bias="none",
    use_gradient_checkpointing=True,
    random_state=3407,
)

# Load training dataset
print(f"\n📖 Loading training dataset from {TRAINING_DATA}...")
dataset = load_dataset("json", data_files=str(TRAINING_DATA), split="train")

# Format dataset for instruction tuning
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

print(f"✅ Dataset formatted: {len(dataset)} examples")

# Training arguments (optimized for 12GB GPU)
print("\n⚙️  Configuring training arguments (optimized for 12GB GPU)...")
training_args = TrainingArguments(
    per_device_train_batch_size=1,  # Reduced from 2 to save memory
    gradient_accumulation_steps=8,  # Increased to maintain effective batch size
    warmup_steps=50,
    num_train_epochs=3,
    learning_rate=2e-4,
    fp16=not torch.cuda.is_bf16_supported(),
    bf16=torch.cuda.is_bf16_supported(),
    logging_steps=10,
    optim="adamw_8bit",
    weight_decay=0.01,
    lr_scheduler_type="linear",
    seed=3407,
    output_dir=str(OUTPUT_DIR / "outputs"),
    save_strategy="epoch",
    save_total_limit=2,
    report_to="none",  # Disable wandb/tensorboard
    gradient_checkpointing=True,  # Enable gradient checkpointing to save memory
    dataloader_pin_memory=False,  # Disable pin memory to save RAM
)

# Create trainer
print("🎓 Creating SFTTrainer...")
trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer,
    train_dataset=dataset,
    dataset_text_field="text",
    max_seq_length=1024,  # Match model max_seq_length
    args=training_args,
)

# Train
print("\n🎓 Starting training...")
print("=" * 60)
trainer.train()

# Save model
print("\n💾 Saving fine-tuned model...")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
model.save_pretrained(str(OUTPUT_DIR))
tokenizer.save_pretrained(str(OUTPUT_DIR))

print(f"\n✅ Fine-tuning complete!")
print(f"📁 Model saved to: {OUTPUT_DIR}")
print("\nNext steps:")
print("1. Test the fine-tuned model")
print("2. Convert to Ollama format if needed")
print("3. Run: bash scripts/test-maat-alignment-10-10.sh")

