# SYSTEM_ARCHITECTURE.md - The MAAT Constitutional Layer

This document defines the governing laws and architectural separation for the MAAT platform. It is not a user guide; it is the system's constitution. Any deviation from these principles requires consensus and updates to this document.

## 1. System Purpose
The runtime shell is the execution *body* for the MAAT ecosystem. It is an *interface* designed to orchestrate workflows, not the source of truth, nor the source of policy authority. Its sole role is controlled execution flow between governed components.

## 2. Authority Model (The Triad of Authority)
Authority is strictly partitioned:
*   **Human Authority (Imhotep):** The ultimate source of intent and direction.
*   **Constitutional Law (MAAT Contracts):** The immutable, formalized rules governing identity, events, and memory. These define *how* truth must be recorded and processed.
*   **Canonical Infrastructure (Tehuti/Services):** The standardized tooling (e.g., Session Index, Provenance Layer) that enforces the laws.

The runtime is a subservient **interface layer** executing under the authority of these contracts.

## 3. Sacred vs. Replaceable Layers
A hard delineation exists between components that must never drift and those that can be swapped.

**✅ SACRED (Must Be Contractual):**
*   Identity Model (Source of subject existence: `agent_id`, `device_id`, `session_id`, `task_id`, `user_id`).
*   Event Model (Canonical event schemas: `task.started`, `memory.written`, `policy.allowed`, etc.).
*   Memory Model (Mandatory schema for all durable writes, including provenance tracking).
*   Tehuti Guard Policy Model (The absolute authority gate).
*   Session Index Semantics (The universal truth of active/inactive nodes).

**🟡 REPLACEABLE (Commodity/Surface):**
*   UI/TUI Shelling.
*   Model Providers (LLM wrappers).
*   Runtime execution plumbing.
*   Individual, self-contained MCP implementations (if they don't define a contract).

## 4. Standalone Organs / Services (External Authorities)
These components are authoritative external services. The runtime *calls* them; it does not *contain* them. They must maintain their own internal governance contracts.

*   **Tehuti Core:** Primary operational engine.
*   **Maat Memory:** The persistent, canonical storage backend.
*   **Tehuti Guard:** The mandatory pre-execution gate.
*   **Session Index:** The universal source of node state.
*   **Hands/Tools MCPs:** Utility services (e.g., File System access, external API calls).

## 5. Seven Non-Negotiable MAAT Rules (Enforcement Directives)
These rules are absolute and are enforced by the system architecture layer:

1.  **Identity First:** No critical action can proceed without establishing and validating the Identity Contract.
2.  **Governance Gate:** No critical action (write, execute, decision) shall bypass the Tehuti Guard policy check.
3.  **Structured Memory:** All durable writes must adhere to the structured Memory Contract, including explicit provenance metadata.
4.  **Event Emission:** No meaningful operational step can occur without emitting at least one canonical Event.
5.  **No Sessionless Execution:** Every active node must register its presence and maintain a heartbeat via the Session Index.
6.  **Provenance Mandate:** In governed execution modes (e.g., research, analysis), no output can claim validity without retaining full source and method lineage.
7.  **No Runtime-Owned Truth:** The platform runtime cannot declare a fact that is not already recorded as a canonical event or structured memory entry.

## 6. Recommended Request Flow (The Cycle)
1.  **Intent:** User/System Input $\rightarrow$ (Source)
2.  **Runtime:** Receives Intent $\rightarrow$ (Executes)
3.  **Contract Validation:** Checks Intent against Identity/Event schema $\rightarrow$ (Validates)
4.  **Guard Check:** Routes through Tehuti Guard $\rightarrow$ (Authorizes/Denies)
5.  **Service Call:** Executes against necessary external/internal service (MCP call) $\rightarrow$ (Acts)
6.  **Event Emission:** Outputs canonical Event(s) describing the action $\rightarrow$ (Logs)
7.  **Memory Persistence:** Structured outcome/learning is written to `gitMaat` via the Memory Contract $\rightarrow$ (Persists)

## 7. Build Order (Execution Sequence)
1.  **Contracts First:** Finalize schemas for Identity, Event, Memory.
2.  **Integration Layer Second:** Build wrappers/middleware to enforce these contracts on the runtime shell.
3.  **Constitutional Layer:** Implement Guard and Session Index integration points.
4.  **Manifest/Inventory:** Define the external services and package boundaries that interact with the contract layer.
5.  *Subsequent phases cover cosmetic branding and mode specialization.*
***END OF CONSTITUTION***