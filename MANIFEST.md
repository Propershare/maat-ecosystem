# MANIFEST.md - Operational Declaration of the MAAT Body

This document inventories the measurable components, addresses, and roles within the MAAT operational surface. It details the *machinery* that executes according to the laws set in SYSTEM_ARCHITECTURE.md.

## 1. Core Services & Endpoints (MCP Boundaries)
These services expose primary functionality and must adhere to canonical contracts.

*   **Tehuti Core:** Primary execution gateway. (Port: 8014)
*   **Maat Memory:** Durable persistence organ. (Port: 8022)
*   **Tehuti Guard:** Policy enforcement microservice. (Port: 8015)
*   **Session Index:** State management service. (Endpoint: /v1/session-index)
*   **External Tools:** Handled via registered, contract-validated MCP adapters.

## 2. Canonical Packages & Modules (Code Boundaries)
These are the primary, required code repositories/modules that must be built and versioned together.

*   **`maat-ecosystem/`**: Ka-body platform — soul, skeleton schemas, maatbench, organs; constitutional truth and governance artifacts live here (not to be confused with the user TS runtime below).
*   **`maat-runtime/`**: TypeScript monorepo — user-facing agent **runtime** (coding agent CLI, TUI, web-ui, pods fork). GitHub: `Propershare/Maat-runtime`. This is **execution surface**, not the same as “MAAT Core” doctrine in `soul/` / `skeleton/`.
*   **`maat_core/`** (underscore): Small **Python** path locator to schemas/soul/bench contracts only — does not run agents. See `maat_core/README.md` and `docs/MAAT-PRODUCT-MAP.md`.
*   **`maatlangchain/`**: Spine — agents, RAG, `maat_memory/` (gitMaat PostgreSQL).
*   *Aspirational / future split modules (when extracted):* `maat-contracts/`, `maat-guard-client/`, `session-index-client/`, `provenance/` — align with `maat-ecosystem/skeleton/` and Tehuti Guard as implemented today.

## 3. Roles & Profiles (Agent Context)
Defines the expected behavior and tool access scope for different logical identities.

*   **Human (Imhotep):** Full write access (via explicit command/intent).
*   **Tehuti (Assistant):** Orchestrator. High read/write capacity, restricted by explicit request.
*   **Scout Role:** Read-heavy access. Limited write permissions, focused on discovery and raw material collection.
*   **Analyst Role:** Read/Write (Decision-write). Requires *both* Scout output and a final decision payload before committing memory.
*   **Archivist Role:** Write-only. Focuses on structured recording of completed work and history persistence.

## 4. Environment & Profile Map
Defines operational profiles for deployments.

*   **`lab` (Default):** Development/Research. High write allowance, low deployment friction. Testing of new contracts.
*   **`governed`:** Primary operational profile. All writes require Guard approval. Standard workload.
*   **`SaaS`:** External-facing profile. Heaviest reliance on role separation (User/Tenant boundaries).
*   **`education`:** Read-only/Demonstration mode. Writes are logged as 'Simulation' and do not affect `gitMaat` state.

## 5. Runtime State Management
*   **Default State Store:** `gitMaat` (The primary source of truth for durable facts).
*   **Transient State:** Handled by the OpenClaw/Session Index state.
*   **Session State:** Managed by `SessionIndex` (Ephemeral, active context).

---
*This manifest is an inventory of the necessary, interconnected components required to build the MAAT operating surface.*