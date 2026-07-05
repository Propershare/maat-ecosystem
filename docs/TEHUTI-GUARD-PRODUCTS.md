# Tehuti Guard — standalone product

**Canonical repo:** https://github.com/Propershare/tehuti-guard

One product, two packages:

| Package | Path in repo | Role |
|---------|--------------|------|
| **decision-api** | `packages/decision-api/` | Python HTTP `:8013` — `/decision`, `/compile-decision` |
| **mcp-proxy** | `packages/mcp-proxy/` | npm MCP wrapper — optional `guardApiUrl` hook |
| **contracts** | `packages/contracts/` | Shared JSON schemas |

## Install (lab)

```bash
git clone https://github.com/Propershare/tehuti-guard.git
export TEHUTI_GUARD_ROOT=/path/to/tehuti-guard
export MAATBENCH_PATH=/mnt/ai_models/maatbench

cd "$TEHUTI_GUARD_ROOT/packages/decision-api"
pip install -e .
tehuti-guard-serve --port 8013
```

## maat-ecosystem path

[`tehuti-guard/`](../tehuti-guard/) in this monorepo is a **deprecated embedded copy**.
New work goes in the standalone repo. See [`tehuti-guard/CANONICAL.md`](../tehuti-guard/CANONICAL.md).

## Wire vocabulary

`allow` | `deny` | `review` | `quarantine` | `escalate`

## Ports (lab)

| Port | Service |
|------|---------|
| **8013** | Tehuti Guard decision API |
| **4242** | maat-sentinel (feeds v1 `/decision`) |

## See also

- Standalone [`ARCHITECTURE.md`](https://github.com/Propershare/tehuti-guard/blob/main/docs/ARCHITECTURE.md)
- [`TEHUTI_GUARD_V2_CONSTITUTIONAL_REBUILD.md`](TEHUTI_GUARD_V2_CONSTITUTIONAL_REBUILD.md)
- [`MAAT-AUDIT-TEHUTI-GUARD-REPO-STRUCTURE.md`](MAAT-AUDIT-TEHUTI-GUARD-REPO-STRUCTURE.md)
