#!/usr/bin/env python3
"""
Convert fine-tuned PyTorch model to GGUF format and import into Ollama
"""

import sys
import subprocess
from pathlib import Path
import json
import shutil

project_root = Path(__file__).parent.parent
fine_tuned_dir = project_root / "fine-tuned-models" / "tehuti-lab-llama3.1-8b-maat-merged"
output_model_name = "tehuti-lab-llama3.1-8b-finetuned"

print("🔄 Converting fine-tuned model to Ollama format...")
print("=" * 60)

# Check if fine-tuned model exists
if not fine_tuned_dir.exists():
    print(f"❌ Fine-tuned model not found at: {fine_tuned_dir}")
    print("   Please run fine-tuning first: python3 scripts/fine_tune_maat.py")
    sys.exit(1)

print(f"✅ Fine-tuned model found at: {fine_tuned_dir}")
print("")

# Check for llama.cpp convert script
llama_cpp_paths = [
    Path.home() / "llama.cpp" / "convert.py",
    Path("/usr/local/bin/convert.py"),
    Path("/opt/llama.cpp/convert.py"),
]

convert_script = None
for path in llama_cpp_paths:
    if path.exists():
        convert_script = path
        print(f"✅ Found llama.cpp convert script at: {convert_script}")
        break

if not convert_script:
    print("⚠️  llama.cpp convert script not found")
    print("   Installing llama.cpp...")
    
    # Try to install llama.cpp
    llama_cpp_dir = Path.home() / "llama.cpp"
    if not llama_cpp_dir.exists():
        print("   Cloning llama.cpp repository...")
        subprocess.run([
            "git", "clone", "https://github.com/ggerganov/llama.cpp.git",
            str(llama_cpp_dir)
        ], check=False)
    
    if llama_cpp_dir.exists():
        convert_script = llama_cpp_dir / "convert.py"
        if not convert_script.exists():
            print("   Building llama.cpp...")
            # Try to build
            subprocess.run(["make"], cwd=llama_cpp_dir, check=False)
    else:
        print("   ⚠️  Could not install llama.cpp automatically")
        print("   Please install manually: https://github.com/ggerganov/llama.cpp")

# Method: Use transformers + llama.cpp Python bindings
print("\n📦 Method: Converting using transformers and GGUF export")
print("   This will convert the model to GGUF format...")

try:
    from transformers import AutoModelForCausalLM, AutoTokenizer
    import torch
    
    print("\n📥 Loading fine-tuned model...")
    print("   Note: Model may be quantized, will dequantize to FP16...")
    
    # Load with bitsandbytes disabled to dequantize
    model = AutoModelForCausalLM.from_pretrained(
        str(fine_tuned_dir),
        torch_dtype=torch.float16,
        device_map="auto",
        trust_remote_code=True,
        load_in_4bit=False,  # Disable 4-bit loading
        load_in_8bit=False,  # Disable 8-bit loading
    )
    tokenizer = AutoTokenizer.from_pretrained(str(fine_tuned_dir))
    
    print("✅ Model loaded successfully!")
    print(f"   Model type: {model.config.model_type}")
    print(f"   Model size: {sum(p.numel() for p in model.parameters()) / 1e9:.2f}B parameters")
    
    # Save in FP16 format for conversion
    print("\n💾 Preparing model for GGUF conversion...")
    output_prep_dir = project_root / "fine-tuned-models" / "tehuti-gguf-prep"
    output_prep_dir.mkdir(parents=True, exist_ok=True)
    
    # Save model in a format that can be converted
    print("   Saving model in FP16 format...")
    model.save_pretrained(
        str(output_prep_dir),
        safe_serialization=True,
        max_shard_size="5GB"
    )
    tokenizer.save_pretrained(str(output_prep_dir))
    
    print(f"✅ Model prepared at: {output_prep_dir}")
    
    # Now try to convert to GGUF
    if convert_script and convert_script.exists():
        print("\n🔄 Converting to GGUF format using llama.cpp...")
        output_gguf = project_root / "fine-tuned-models" / f"{output_model_name}.gguf"
        
        cmd = [
            "python3", str(convert_script),
            str(output_prep_dir),
            "--outfile", str(output_gguf),
            "--outtype", "f16"  # FP16 quantization
        ]
        
        print(f"   Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0 and output_gguf.exists():
            print(f"✅ GGUF file created: {output_gguf}")
            print(f"   Size: {output_gguf.stat().st_size / 1e9:.2f} GB")
            
            # Create Modelfile
            print("\n📝 Creating Modelfile for Ollama...")
            modelfile = project_root / "fine-tuned-models" / f"{output_model_name}.Modelfile"
            with open(modelfile, "w") as f:
                f.write(f"""# Fine-tuned Tehuti Lab Model
# This model was fine-tuned for Maat alignment

FROM {output_gguf}

SYSTEM \"\"\"
You are a fine-tuned AI assistant in **Tehuti Lab**, trained specifically for Maat alignment.
This model was fine-tuned on Maat-aligned examples for better tool calling and recommendations.
\"\"\"
""")
            
            print(f"✅ Modelfile created: {modelfile}")
            print("\n🔄 Importing into Ollama...")
            
            # Import to Ollama
            result = subprocess.run(
                ["ollama", "create", output_model_name, "-f", str(modelfile)],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print(f"✅ Model imported into Ollama as: {output_model_name}")
                print("\n📋 Next steps:")
                print(f"   1. Update setup script to use: FROM {output_model_name}")
                print(f"   2. Test the model: ollama run {output_model_name}")
            else:
                print(f"❌ Failed to import to Ollama:")
                print(result.stderr)
        else:
            print(f"❌ GGUF conversion failed:")
            if result.stderr:
                print(result.stderr)
            print("\n⚠️  Alternative: Use the base model with enhanced system prompt")
    else:
        print("\n⚠️  llama.cpp convert script not available")
        print("   Model prepared but not converted to GGUF")
        print("   Please install llama.cpp and convert manually:")
        print(f"   python3 convert.py {output_prep_dir} --outfile model.gguf")
        
except ImportError as e:
    print(f"❌ Missing dependency: {e}")
    print("   Install: pip3 install transformers torch")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    print("\n⚠️  Falling back to base model with enhanced system prompt")

print("\n" + "=" * 60)
print("📋 Summary:")
print(f"   Fine-tuned model: {fine_tuned_dir}")
print(f"   Target Ollama model: {output_model_name}")
print("\n   If conversion failed, the current approach uses:")
print("   - Base model (llama3.1:8b)")
print("   - Enhanced system prompt (from fine-tuning examples)")
print("   - This provides similar behavior without GGUF conversion")

