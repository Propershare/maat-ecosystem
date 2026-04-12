# Tehuti Lab workspace

**What this is:** A monorepo for Maat-aligned AI infrastructure: constitutional schemas, Guard/Sentinel, agents, MCP, and operator docs. It is a **lab tree**, not a single installable product.

## One truth (canonical Ka-body)

The **canonical MAAT Ka-body** (organs, `MANIFEST.ka`, soul, skeleton schemas, MaatBench) lives here:

**[`maat-ecosystem/`](maat-ecosystem/)** — start with [`maat-ecosystem/README.md`](maat-ecosystem/README.md) and [`maat-ecosystem/MANIFEST.ka`](maat-ecosystem/MANIFEST.ka).

### Legacy / duplicate layout (read-only intent)

After a Git merge, **root-level** folders such as `maatbench/`, `maat-core/`, `maat-apps/` (standalone-era layout) may still exist beside `maat-ecosystem/`. Treat them as **legacy reference** unless you are explicitly maintaining them. **Do not** start new work there — use **`maat-ecosystem/`** and its subpaths. Details: [`archive/README.md`](archive/README.md).

---

## Where to start (entry paths)

| You are… | Open |
|----------|------|
| **A human** (no jargon) | [`docs/INITIATION.md`](docs/INITIATION.md) |
| **An operator** (first curl / health) | [`docs/FIRST-RUN.md`](docs/FIRST-RUN.md) |
| **Integrating HTTP / decisions** | [`docs/ENDPOINTS-AND-DECISIONS.md`](docs/ENDPOINTS-AND-DECISIONS.md) |
| **Mapping the whole lab** | [`docs/SYSTEM-CONNECTIONS.md`](docs/SYSTEM-CONNECTIONS.md) |
| **Repo vs product names** | [`docs/MAAT-PRODUCT-MAP.md`](docs/MAAT-PRODUCT-MAP.md) |

**Agent-assisted setup:** [`docs/SETUP-WITH-AGENT.md`](docs/SETUP-WITH-AGENT.md)

**Workspace home for Cursor/OpenClaw:** [`AGENTS.md`](AGENTS.md)

---

## Ma’at audit → action plan

Tracked checklist: [`docs/MAAT-AUDIT-ACTION-PLAN.md`](docs/MAAT-AUDIT-ACTION-PLAN.md)

---

## License

See [`maat-ecosystem/LICENSE`](maat-ecosystem/LICENSE) for ecosystem code; individual packages may declare their own.
