#!/usr/bin/env python3
"""
Fine-tuning script for Gemma-3 tool-call capabilities using Unsloth.

Uses LoRA for efficient training and exports to GGUF Q4_K_M for Ollama deployment.

NOTE: This targets gemma-3 architecture (e.g., "unsloth/gemma-3-8b-it").
When gemma-4 is officially supported in transformers/unsloth, swap the
MODEL_NAME and potentially the chat template — search for "SWAP_FOR_GEMMA4"
comments below.

Requirements:
    pip install unsloth transformers datasets trl peft accelerate bitsandbytes

Usage:
    python finetune.py [--model unsloth/gemma-3-8b-it] [--data training_data/] [--output output/]
"""

import argparse
import json
import os
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

# SWAP_FOR_GEMMA4: Change this to the gemma-4 HuggingFace model ID when available
# e.g., "unsloth/gemma-4-12b-it" or your local Ollama GGUF path
DEFAULT_MODEL = "unsloth/gemma-3-8b-it"

LORA_CONFIG = {
    "r": 16,
    "lora_alpha": 32,
    "target_modules": ["q_proj", "k_proj", "v_proj", "o_proj"],
    "lora_dropout": 0.05,
    "bias": "none",
    "task_type": "CAUSAL_LM",
}

TRAINING_CONFIG = {
    "per_device_train_batch_size": 2,
    "gradient_accumulation_steps": 4,
    "warmup_steps": 10,
    "max_steps": 1000,
    "learning_rate": 2e-4,
    "fp16": True,
    "logging_steps": 10,
    "optim": "adamw_8bit",
    "weight_decay": 0.01,
    "lr_scheduler_type": "linear",
    "seed": 42,
    "output_dir": "output/checkpoints",
}

MAX_SEQ_LENGTH = 2048
GGUF_QUANT_METHOD = "q4_k_m"  # Q4_K_M for good quality/size balance

OLLAMA_MODELFILE_TEMPLATE = """# Ollama Modelfile for fine-tuned Gemma-3 tool-call model
# SWAP_FOR_GEMMA4: Update FROM path and TEMPLATE when using gemma-4

FROM {gguf_path}

TEMPLATE \"\"\"<bos><start_of_turn>system
{{ .System }}<end_of_turn>
{{ range .Messages }}<start_of_turn>{{ .Role }}
{{ .Content }}<end_of_turn>
{{ end }}<start_of_turn>model
\"\"\"

SYSTEM \"\"\"You are a helpful coding assistant with access to file system tools.
Use tools to read, write, and modify files as needed.
Always use the appropriate tool rather than guessing file contents.\"\"\"

PARAMETER stop "<end_of_turn>"
PARAMETER stop "<eos>"
PARAMETER temperature 0.1
PARAMETER top_p 0.9
PARAMETER num_ctx 4096
"""


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_jsonl(path: str) -> list:
    """Load a JSONL file, returning a list of dicts."""
    records = []
    with open(path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as e:
                print(f"Warning: Skipping malformed line {i+1} in {path}: {e}", file=sys.stderr)
    return records


def load_training_data(data_dir: str) -> list:
    """
    Load all JSONL training data from data_dir.
    Combines synthetic.jsonl (generated) and captures.jsonl (live captures).
    """
    data_dir = Path(data_dir)
    all_records = []

    sources = [
        ("synthetic.jsonl", "synthetic"),
        ("captures.jsonl", "captured"),
    ]

    for filename, source_name in sources:
        path = data_dir / filename
        if path.exists():
            records = load_jsonl(str(path))
            print(f"Loaded {len(records)} {source_name} examples from {path}")
            all_records.extend(records)
        else:
            print(f"Note: {path} not found, skipping.")

    if not all_records:
        raise ValueError(f"No training data found in {data_dir}. "
                         "Run generate_training.py first.")

    return all_records


def format_record_for_training(record: dict, tokenizer) -> dict:
    """
    Convert a training record to a formatted string using the model's chat template.

    Supports two formats:
    1. Synthetic format: {"conversations": [...], "tools": [...]}
    2. Capture format: {"messages": [...], "tools": [...], "response": {...}, ...}
    """
    # Normalize to messages list
    if "conversations" in record:
        messages = record["conversations"]
    elif "messages" in record:
        messages = record["messages"]
        # For captures, the response is the corrected message - ensure it's in messages
        # The capture already has the full conversation including the corrected assistant turn
    else:
        return None

    if not messages:
        return None

    # Apply chat template
    try:
        # SWAP_FOR_GEMMA4: The chat template may differ for gemma-4
        text = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=False,
        )
        return {"text": text}
    except Exception as e:
        print(f"Warning: Chat template failed: {e}", file=sys.stderr)
        return None


# ---------------------------------------------------------------------------
# Training
# ---------------------------------------------------------------------------

def run_training(args):
    """Main training function."""
    print("Loading Unsloth and dependencies...")
    try:
        from unsloth import FastLanguageModel
    except ImportError:
        print("ERROR: unsloth not installed. Run: pip install unsloth", file=sys.stderr)
        sys.exit(1)

    try:
        from trl import SFTTrainer
        from transformers import TrainingArguments
        from datasets import Dataset
    except ImportError as e:
        print(f"ERROR: Missing dependency: {e}", file=sys.stderr)
        print("Run: pip install trl transformers datasets", file=sys.stderr)
        sys.exit(1)

    # Load model
    model_name = args.model
    print(f"\nLoading model: {model_name}")
    print("NOTE: This targets gemma-3 architecture.")
    print("SWAP_FOR_GEMMA4: Change --model to gemma-4 HuggingFace ID when available.\n")

    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=model_name,
        max_seq_length=MAX_SEQ_LENGTH,
        dtype=None,          # Auto-detect
        load_in_4bit=True,   # QLoRA
    )

    # Apply LoRA
    print(f"Applying LoRA (r={LORA_CONFIG['r']}, alpha={LORA_CONFIG['lora_alpha']})...")
    model = FastLanguageModel.get_peft_model(
        model,
        r=LORA_CONFIG["r"],
        target_modules=LORA_CONFIG["target_modules"],
        lora_alpha=LORA_CONFIG["lora_alpha"],
        lora_dropout=LORA_CONFIG["lora_dropout"],
        bias=LORA_CONFIG["bias"],
        use_gradient_checkpointing="unsloth",
        random_state=42,
        use_rslora=False,
        loftq_config=None,
    )

    # Load data
    print(f"\nLoading training data from {args.data}...")
    raw_records = load_training_data(args.data)
    print(f"Total examples: {len(raw_records)}")

    # Format for training
    formatted = []
    for rec in raw_records:
        result = format_record_for_training(rec, tokenizer)
        if result:
            formatted.append(result)

    print(f"Successfully formatted: {len(formatted)} examples")
    if not formatted:
        print("ERROR: No valid training examples after formatting.", file=sys.stderr)
        sys.exit(1)

    dataset = Dataset.from_list(formatted)

    # Training config
    output_dir = os.path.join(args.output, "checkpoints")
    os.makedirs(output_dir, exist_ok=True)

    training_args = TrainingArguments(
        per_device_train_batch_size=TRAINING_CONFIG["per_device_train_batch_size"],
        gradient_accumulation_steps=TRAINING_CONFIG["gradient_accumulation_steps"],
        warmup_steps=TRAINING_CONFIG["warmup_steps"],
        max_steps=args.max_steps or TRAINING_CONFIG["max_steps"],
        learning_rate=TRAINING_CONFIG["learning_rate"],
        fp16=TRAINING_CONFIG["fp16"],
        logging_steps=TRAINING_CONFIG["logging_steps"],
        optim=TRAINING_CONFIG["optim"],
        weight_decay=TRAINING_CONFIG["weight_decay"],
        lr_scheduler_type=TRAINING_CONFIG["lr_scheduler_type"],
        seed=TRAINING_CONFIG["seed"],
        output_dir=output_dir,
        report_to="none",
    )

    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=dataset,
        dataset_text_field="text",
        max_seq_length=MAX_SEQ_LENGTH,
        dataset_num_proc=2,
        packing=True,
        args=training_args,
    )

    print("\n--- Training ---")
    trainer_stats = trainer.train()
    print(f"\nTraining complete.")
    print(f"  Training loss: {trainer_stats.training_loss:.4f}")

    # Save LoRA adapter
    lora_output = os.path.join(args.output, "lora_adapter")
    print(f"\nSaving LoRA adapter to {lora_output}...")
    model.save_pretrained(lora_output)
    tokenizer.save_pretrained(lora_output)

    # Export to GGUF
    if not args.skip_gguf:
        gguf_output = os.path.join(args.output, f"model_{GGUF_QUANT_METHOD}.gguf")
        print(f"\nExporting to GGUF ({GGUF_QUANT_METHOD}) → {gguf_output}")
        print("This requires llama.cpp to be installed.")
        model.save_pretrained_gguf(
            os.path.join(args.output, "gguf"),
            tokenizer,
            quantization_method=GGUF_QUANT_METHOD,
        )
        # The actual file will be in the gguf/ subdir
        gguf_actual = os.path.join(args.output, "gguf", f"model-{GGUF_QUANT_METHOD.upper()}.gguf")
        print(f"GGUF exported.")

        # Write Ollama Modelfile
        modelfile_path = os.path.join(args.output, "Modelfile")
        modelfile_content = OLLAMA_MODELFILE_TEMPLATE.format(
            gguf_path=os.path.abspath(gguf_actual)
        )
        with open(modelfile_path, "w") as f:
            f.write(modelfile_content)
        print(f"\nOllama Modelfile written to {modelfile_path}")

        print("\n--- Ollama Import Steps ---")
        print(f"1. ollama create gemma3-toolcall -f {modelfile_path}")
        print(f"2. ollama run gemma3-toolcall")
        print(f"3. Update SHIM's model config to use 'gemma3-toolcall'")
    else:
        print("Skipping GGUF export (--skip-gguf)")

    print("\nDone!")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Fine-tune Gemma-3 for tool-call capabilities",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Full training run
  python finetune.py

  # Custom model and data
  python finetune.py --model unsloth/gemma-3-4b-it --data training_data/ --output output/

  # Quick test run (100 steps)
  python finetune.py --max-steps 100 --skip-gguf

  # SWAP_FOR_GEMMA4: When gemma-4 is in unsloth:
  # python finetune.py --model unsloth/gemma-4-12b-it
        """
    )
    parser.add_argument("--model", default=DEFAULT_MODEL,
                        help=f"HuggingFace model ID (default: {DEFAULT_MODEL})")
    parser.add_argument("--data", default=os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "training_data"
    ), help="Directory with training JSONL files")
    parser.add_argument("--output", default=os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "output"
    ), help="Output directory for model artifacts")
    parser.add_argument("--max-steps", type=int, default=None,
                        help="Override max training steps")
    parser.add_argument("--skip-gguf", action="store_true",
                        help="Skip GGUF export (faster for testing)")
    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)
    run_training(args)


if __name__ == "__main__":
    main()
