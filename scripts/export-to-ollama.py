#!/usr/bin/env python3
"""
Export fine-tuned Unsloth model to Ollama-compatible format
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from unsloth import FastLanguageModel
from peft import PeftModel
import torch

print("🔄 Exporting fine-tuned model to Ollama format...")
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

# Merge adapter with base model and save in FP16 (dequantized)
print("\n🔧 Merging LoRA adapter with base model...")
model = model.merge_and_unload()

# Save merged model in FP16 format (dequantized) for GGUF conversion
output_dir = project_root / "fine-tuned-models" / "tehuti-lab-llama3.1-8b-maat-merged-fp16"
output_dir.mkdir(parents=True, exist_ok=True)

print(f"\n💾 Saving merged model in FP16 format (dequantized) to {output_dir}...")
print("   This may take a while...")

# Use Unsloth's save function which handles dequantization
FastLanguageModel.save_pretrained_merged(
    model,
    str(output_dir),
    tokenizer,
    save_method="merged_16bit",  # Save as FP16 (dequantized)
)

print("\n✅ Model exported successfully in FP16 (dequantized)!")
print(f"📁 Location: {output_dir}")
print("\nNext: Convert to GGUF format using llama.cpp convert_hf_to_gguf.py")

