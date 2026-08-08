#!/usr/bin/env python3
"""
Dequantize the fine-tuned model to full precision for GGUF conversion
"""

import sys
from pathlib import Path
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import json

project_root = Path(__file__).parent.parent
fine_tuned_dir = project_root / "fine-tuned-models" / "tehuti-lab-llama3.1-8b-maat-merged"
output_dir = project_root / "fine-tuned-models" / "tehuti-gguf-prep"

print("🔄 Dequantizing fine-tuned model to full precision...")
print("=" * 60)

print(f"\n📥 Loading base model and LoRA adapter...")

# Load base model without quantization
from unsloth import FastLanguageModel
from peft import PeftModel

base_model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="unsloth/Llama-3.1-8B-Instruct-bnb-4bit",
    max_seq_length=2048,
    dtype=torch.float16,  # Use FP16
    load_in_4bit=False,  # NO quantization
    load_in_8bit=False,  # NO quantization
)

print("✅ Base model loaded in FP16 (no quantization)")

# Load LoRA adapter
lora_dir = project_root / "fine-tuned-models" / "tehuti-lab-llama3.1-8b-maat"
print(f"\n📥 Loading LoRA adapter from: {lora_dir}")

model = PeftModel.from_pretrained(base_model, str(lora_dir))

print("✅ LoRA adapter loaded")

# Merge adapter
print("\n🔧 Merging LoRA adapter with base model...")
model = model.merge_and_unload()

print("✅ Model merged and dequantized!")

print("✅ Model dequantized!")

# Remove quantization config from config.json
print("\n📝 Removing quantization config...")
config_path = fine_tuned_dir / "config.json"
if config_path.exists():
    with open(config_path, "r") as f:
        config = json.load(f)
    
    # Remove quantization config
    if "quantization_config" in config:
        del config["quantization_config"]
        print("   Removed quantization_config from config")
    
    # Save updated config
    output_dir.mkdir(parents=True, exist_ok=True)
    with open(output_dir / "config.json", "w") as f:
        json.dump(config, f, indent=2)

print(f"\n💾 Saving dequantized model to: {output_dir}")
print("   This may take a while...")

# Save model in full precision (FP16)
model.save_pretrained(
    str(output_dir),
    safe_serialization=True,
    max_shard_size="5GB",
)
tokenizer.save_pretrained(str(output_dir))

print(f"\n✅ Dequantized model saved to: {output_dir}")
print("   Model is now ready for GGUF conversion!")

