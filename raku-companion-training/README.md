# Raku Companion Training

Training data scaffold for the StayDangerous AI companion NPC model.

This reuses the existing `.n8n/gemma4-toolshim/finetune.py` style:

- JSONL records use `conversations`.
- Each conversation is `system -> user observation JSON -> assistant action JSON`.
- The model learns a narrow task: read an observation and emit one validated action JSON object.

## Generate Data

```bash
cd /home/suspect/.n8n/raku-companion-training
python3 generate_companion_training.py --count 500
```

Outputs:

- `training_data/golden.jsonl` - hand-authored seed examples.
- `training_data/synthetic.jsonl` - generated examples for Unsloth SFT.

## Train Smoke Test

Use the existing trainer after selecting a supported small uncensored base model:

```bash
python3 /home/suspect/.n8n/gemma4-toolshim/finetune.py \
  --data /home/suspect/.n8n/raku-companion-training/training_data \
  --output /home/suspect/.n8n/raku-companion-training/output \
  --max-steps 100 \
  --skip-gguf
```

The model target is intentionally not hardcoded here. The dataset should work with a 1B, 1.5B, or 3B uncensored roleplay/instruct base.
