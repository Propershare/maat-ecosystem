# Tehuti Guard — canonical source moved

**The Guard source of truth is now the standalone repo:**

https://github.com/Propershare/tehuti-guard

## Layout (standalone)

```
tehuti-guard/
├── packages/mcp-proxy/      ← npm MCP wrapper
├── packages/decision-api/   ← Python POST /decision, /compile-decision
└── packages/contracts/      ← shared wire schemas
```

## Lab usage

Clone or set:

```bash
export TEHUTI_GUARD_ROOT=/path/to/tehuti-guard
export MAATBENCH_PATH=/mnt/ai_models/maatbench
cd "$TEHUTI_GUARD_ROOT/packages/decision-api" && pip install -e .
tehuti-guard-serve --port 8013
```

## This folder

The embedded `guard/` tree here is **deprecated**. It remains temporarily for
backward compatibility until all lab scripts point at `TEHUTI_GUARD_ROOT`.

Do **not** add new Guard features here. Patch the standalone repo instead.

See [`docs/TEHUTI-GUARD-PRODUCTS.md`](../docs/TEHUTI-GUARD-PRODUCTS.md).
