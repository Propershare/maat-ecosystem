#!/usr/bin/env python3
"""
Complete conversion of fine-tuned model to GGUF format
Handles dequantization and GGUF conversion with Q4_K_M quantization
"""

import sys
import subprocess
from pathlib import Path
import json
import torch
import os

# Free GPU memory before starting
print("🔍 Checking GPU memory...")
result = subprocess.run(
    ["nvidia-smi", "--query-compute-apps=pid,process_name,used_memory", "--format=csv,noheader"],
    capture_output=True,
    text=True
)

if result.stdout.strip():
    print("⚠️  GPU processes detected. Freeing GPU memory...")
    pids = []
    for line in result.stdout.strip().split('\n'):
        if line:
            pid = line.split(',')[0].strip()
            if pid.isdigit():
                pids.append(pid)
    
    if pids:
        print(f"   Found {len(pids)} GPU process(es)")
        print("   ⚠️  These processes will be killed to free GPU memory")
        print("   You may need to restart them manually after conversion")
        
        for pid in pids:
            try:
                subprocess.run(["kill", "-9", pid], check=False, capture_output=True)
                print(f"   ✅ Killed PID {pid}")
            except:
                pass
        
        print("   ⏳ Waiting 10 seconds for GPU memory to free...")
        import time
        time.sleep(10)
        
        # Clear PyTorch cache
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            print("   ✅ GPU memory freed")
else:
    print("   ✅ No GPU processes found")

project_root = Path(__file__).parent.parent
# Use uncensored model if it exists, otherwise use standard
uncensored_dir = project_root / "fine-tuned-models" / "tehuti-lab-llama3.1-8b-uncensored-maat"
standard_dir = project_root / "fine-tuned-models" / "tehuti-lab-llama3.1-8b-maat"
lora_dir = uncensored_dir if uncensored_dir.exists() else standard_dir
output_gguf = project_root / "fine-tuned-models" / "tehuti-lab-llama3.1-8b-uncensored-finetuned-f16.gguf"
output_model_name = "tehuti-lab-llama3.1-8b-uncensored-finetuned"

print("🔄 Converting fine-tuned model to GGUF format...")
print("=" * 60)

# Step 1: Load and dequantize model
print("\n📥 Step 1: Loading base model and LoRA adapter...")
print("   This will dequantize from 4-bit to FP16...")

try:
    import unsloth
    from unsloth import FastLanguageModel
    from peft import PeftModel
    
    # Load base model WITHOUT quantization
    # Use CPU for conversion to avoid GPU memory issues
    print("   Loading base model in FP16 (no quantization)...")
    print("   Using CPU for conversion (GPU memory limited)...")
    
    base_model, tokenizer = FastLanguageModel.from_pretrained(
        model_name="unsloth/Llama-3.1-8B-Instruct-bnb-4bit",
        max_seq_length=2048,
        dtype=torch.float16,
        load_in_4bit=False,  # NO quantization
        load_in_8bit=False,  # NO quantization
        device_map="cpu",  # Use CPU to avoid GPU memory issues
    )
    
    print("   ✅ Base model loaded in FP16")
    
    # Load LoRA adapter
    print(f"   Loading LoRA adapter from: {lora_dir}")
    model = PeftModel.from_pretrained(
        base_model, 
        str(lora_dir),
        device_map="cpu"  # Use CPU
    )
    
    print("   ✅ LoRA adapter loaded")
    
    # Merge adapter
    print("   Merging LoRA adapter...")
    model = model.merge_and_unload()
    
    print("   ✅ Model merged!")
    
    print("   ✅ Model merged and dequantized!")
    
    # Save dequantized model temporarily
    temp_dir = project_root / "fine-tuned-models" / "tehuti-gguf-temp"
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\n💾 Saving dequantized model to: {temp_dir}")
    print("   This may take a few minutes...")
    
    model.save_pretrained(
        str(temp_dir),
        safe_serialization=True,
        max_shard_size="5GB",
    )
    tokenizer.save_pretrained(str(temp_dir))
    
    # Remove quantization config
    config_path = temp_dir / "config.json"
    if config_path.exists():
        with open(config_path, "r") as f:
            config = json.load(f)
        if "quantization_config" in config:
            del config["quantization_config"]
        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)
        print("   ✅ Removed quantization config")
    
    print(f"   ✅ Dequantized model saved")
    
except Exception as e:
    print(f"   ❌ Error in dequantization: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 2: Convert to GGUF
print("\n📦 Step 2: Converting to GGUF format...")
print("   Using llama.cpp convert script...")

convert_script = Path.home() / "llama.cpp" / "convert_hf_to_gguf.py"

if not convert_script.exists():
    print("   ❌ llama.cpp convert script not found!")
    print("   Please ensure llama.cpp is cloned at: ~/llama.cpp")
    sys.exit(1)

print(f"   Using converter: {convert_script}")

# Convert to GGUF FP16 first, then we'll quantize
print("   Converting to GGUF FP16 format first...")
print("   This will take several minutes...")

temp_gguf = project_root / "fine-tuned-models" / "tehuti-lab-llama3.1-8b-finetuned-f16.gguf"

cmd = [
    "python3",
    str(convert_script),
    str(temp_dir),
    "--outfile", str(temp_gguf),
    "--outtype", "f16",  # FP16 first
]

print(f"   Running: {' '.join(cmd)}")

try:
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        check=True
    )
    
    if temp_gguf.exists():
        size_gb = temp_gguf.stat().st_size / 1e9
        print(f"\n   ✅ GGUF FP16 file created!")
        print(f"   📁 Location: {temp_gguf}")
        print(f"   📊 Size: {size_gb:.2f} GB")
        
        # Now quantize to Q4_K_M using llama.cpp quantize tool
        print("\n   Quantizing to Q4_K_M format...")
        quantize_tool = Path.home() / "llama.cpp" / "build" / "bin" / "llama-quantize"
        
        if not quantize_tool.exists():
            # Try alternative location
            quantize_tool = Path.home() / "llama.cpp" / "llama-quantize"
        
        if quantize_tool.exists():
            print(f"   Using quantize tool: {quantize_tool}")
            quantize_cmd = [
                str(quantize_tool),
                str(temp_gguf),
                str(output_gguf),
                "Q4_K_M"
            ]
            
            print(f"   Running: {' '.join(quantize_cmd)}")
            quantize_result = subprocess.run(
                quantize_cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            if output_gguf.exists():
                final_size_gb = output_gguf.stat().st_size / 1e9
                print(f"   ✅ Quantized GGUF file created!")
                print(f"   📁 Location: {output_gguf}")
                print(f"   📊 Size: {final_size_gb:.2f} GB (reduced from {size_gb:.2f} GB)")
                # Remove temp FP16 file
                temp_gguf.unlink()
            else:
                print("   ⚠️  Quantization failed, using FP16 version")
                output_gguf = temp_gguf
        else:
            print("   ⚠️  Quantize tool not found, using FP16 version")
            print("   Install: cd ~/llama.cpp && mkdir build && cd build && cmake .. && make")
            output_gguf = temp_gguf
    else:
        print("   ❌ GGUF file not created")
        print(result.stderr)
        sys.exit(1)
        
except subprocess.CalledProcessError as e:
    print(f"   ❌ Conversion failed:")
    print(e.stderr)
    sys.exit(1)

# Step 3: Create Modelfile and import to Ollama
print("\n📝 Step 3: Creating Modelfile and importing to Ollama...")

modelfile = project_root / "fine-tuned-models" / f"{output_model_name}.Modelfile"

with open(modelfile, "w") as f:
    f.write(f"""# Fine-tuned Tehuti Lab Model
# This model was fine-tuned for Maat alignment and converted to GGUF Q4_K_M format

FROM {output_gguf}

SYSTEM \"\"\"
You are a fine-tuned AI assistant in **Tehuti Lab**, trained specifically for Maat alignment.
This model was fine-tuned on Maat-aligned examples for better tool calling and recommendations.
The model has been optimized in GGUF Q4_K_M format for fast inference.
\"\"\"
""")

print(f"   ✅ Modelfile created: {modelfile}")

# Import to Ollama
print(f"\n🔄 Importing to Ollama as: {output_model_name}")
print("   This may take a moment...")

try:
    result = subprocess.run(
        ["ollama", "create", output_model_name, "-f", str(modelfile)],
        capture_output=True,
        text=True,
        check=True
    )
    
    print(f"   ✅ Model imported successfully!")
    print(f"\n📋 Model is now available in Ollama:")
    print(f"   Name: {output_model_name}")
    print(f"   Test it: ollama run {output_model_name}")
    
except subprocess.CalledProcessError as e:
    print(f"   ⚠️  Import to Ollama failed:")
    print(e.stderr)
    print(f"\n   You can import manually:")
    print(f"   ollama create {output_model_name} -f {modelfile}")

# Cleanup
print("\n🧹 Cleaning up temporary files...")
try:
    import shutil
    shutil.rmtree(temp_dir)
    print("   ✅ Temporary files removed")
except:
    print("   ⚠️  Could not remove temp files (you can delete manually)")

print("\n" + "=" * 60)
print("✅ Conversion complete!")
print(f"   GGUF file: {output_gguf}")
print(f"   Ollama model: {output_model_name}")
print("\n📋 Next steps:")
print(f"   1. Test: ollama run {output_model_name}")
print(f"   2. Update setup script to use: FROM {output_model_name}")

