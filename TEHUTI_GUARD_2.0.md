# TEHUTI_GUARD_2.0.md - Constitutional Control Plane Specification

## Doctrine Statement

Tehuti Guard (TGuard) is not a permission checker; it is the constitutional control plane that enforces Maat within the system. Any system component (Model, Agent, Tool, Workflow) output must be treated as a **Proposal** and must pass through TGuard before it can effect any change to the system state, memory, or environment.

**Core Rule:** The model may **PROPOSE**. The system **MUST VERIFY**.

**Enforcement Scope:** TGuard must intercept and validate *every* meaningful action path, including, but not limited to:
*   Tool Execution Calls
*   File Writes / Edits
*   Shell Commands Execution
*   MCP Calls
*   Memory Writes (Lesson Promotion, State Changes)
*   Policy/Config Mutations
*   Privileged Session Spawning

## Architectural Principles

1.  **The 4 D's:**
    *   **Dangerous** $\rightarrow$ Must be **Gated**.
    *   **Meaningful** $\rightarrow$ Must be **Logged**.
    *   **Durable** $\rightarrow$ Must be **Structured**.
    *   **Adaptive** $\rightarrow$ Must be **Reversible**.

2.  **Separation of Concerns:** The thinking/planning process must be functionally and architecturally separate from the doing/execution process.
    *   **Input:** Model/Agent $\rightarrow$ Proposal Space $\rightarrow$ TGuard $\rightarrow$ **Proposal Object**
    *   **Output:** TGuard Decision $\rightarrow$ Runtime Hooks $\rightarrow$ Action/State Change

## TGuard Operational Flow (The Six Gates)

The evaluation sequence is deterministic and cascaded. Failure at any stage results in an immediate decision override (Quarantine or Deny).

**Input:** Raw Model/Agent Output Stream

**Output:** Decision Object (ALLOW, DENY, ESCALATE, QUARANTINE, REVIEW) + Rich Metadata

### 1. Identity Gate
**Purpose:** Establishes accountability for the proposal.
**Checks:** Mandatory presence and validation of the following identity elements:
*   `agent_id` (Source/Initiator)
*   `device_id` (Execution Context)
*   `session_id` (Session Context)
*   `task_id` (Goal Context)
*   `product/app_identity` (Originating Software Context)
*   `runtime_identity` (Execution Environment Context)
**Failure:** No identity information $\rightarrow$ **DENY**.

### 2. Intent Gate
**Purpose:** Classifies the *purpose* of the attempted action.
**Classification Taxonomy:**
*   `retrieval` (Read/Search)
*   `reasoning` (Inference/Drafting)
*   `execution` (Running code/tools)
*   `propose_promo` (Suggesting new rules/memory entries)
*   `policy_escalate` (Requesting policy change)
*   `expo_report` (External data export/leak)
*   `spawn_connect` (Creating sessions/connections)
**Value:** Contextual risk assessment. An 'execution' call within a 'reasoning' intent is higher risk than the reverse.

### 3. Contract Gate
**Purpose:** Validates the structural integrity of the *payload*.
**Checks:**
*   **Schema Validation:** Must conform to canonical schemas for the declared action.
*   **Provenance Inclusion:** Must contain necessary source references (see Gate 6).
*   **State Transition:** Must represent a valid state move (e.g., `task_status: Pending` $\rightarrow$ `task_status: InProgress`).
*   **Canonical Event Name:** Must map to a recognized, typed event schema.
*   **Completeness:** No missing fields required by the target action schema.
**Failure:** Structural failure $\rightarrow$ **QUARANTINE**.

### 4. Policy Gate
**Purpose:** Governs access rights based on pre-defined rulesets.
**Mechanisms:** Strengthened Ring Model, governing the *potential* of the action.
**Scope:** Must cover more than file paths:
*   `tool_capability` access matrix.
*   `memory_class` write access (e.g., can this agent write to `MAAT_CORE` vs. `TEMP_LOGS`).
*   `event_class` permissions.
*   `config_domain` mutation rules.
*   `runtime_capabilities` elevation.
**Failure:** Policy violation $\rightarrow$ **DENY** (unless escalation bypass is explicitly authorized).

### 5. Risk Gate
**Purpose:** Detects complex, subtle, or emergent threats that bypass structural checks.
**Scoring Mechanism:** Assigns a quantitative risk score based on heuristic analysis of the entire proposal object.
**High-Risk Indicators (triggers increased scrutiny):**
*   Unusual tool chains (e.g., `read` $\rightarrow$ `write` $\rightarrow$ `exec` in sequence).
*   Multi-step destructive behavior patterns.
*   Shell usage in non-executable contexts (e.g., passing shell strings as configuration values).
*   Attempts to disable logging or intercept system calls.
*   Attempts to mutate TGuard/Policy/Constitution files.
**Outcome Mapping:** The score dictates the *minimum* required TGuard decision override (e.g., Score $> 0.8 \rightarrow$ **ESCALATE**).

### 6. Provenance Gate
**Purpose:** Ensures knowledge claims are auditable and non-self-corrupting.
**Checks (For any action affecting Knowledge, Memory, or Policy):**
*   **Source References:** Must cite specific sources ($\text{path\#line}$, URL, DB ID).
*   **Method Provenance:** Must tag the method by which knowledge was acquired (e.g., `[Observation]`, `[Simulation]`, `[UserInput]`).
*   **Confidence:** Must provide a confidence score relative to the evidence base.
*   **Contradiction Flags:** Must flag any conflicting evidence found in the proposed data.
**Failure:** Lack of provenance $\rightarrow$ **QUARANTINE** (unless the action is purely self-contained/internal reasoning).

## TGuard Decision Outcomes (State Machine)

The decision is a defined state, not a binary yes/no.

*   **ALLOW:** Fully verified across all 6 gates. The proposed action is safe to execute.
*   **DENY:** Failed a core constitutional check (e.g., Identity missing, Policy violation). Execution halted immediately.
*   **QUARANTINE:** Suspicious behavior detected (e.g., Schema drift, Missing Provenance, Unusual Tool Chain). Requires human review or automated challenge before execution.
*   **ESCALATE:** High-risk behavior detected (e.g., Potential data exfiltration, Unknown vulnerability path). Requires layered escalation (e.g., Notify Human *and* Log to Audit Sink *and* Halt).
*   **REVIEW:** Requires an explicit, human-validated approval before proceeding (e.g., changing global policy).

## Operationalization: The Module Build (Phased Approach)

The implementation must follow the following incremental build order for stability:

**Phase 1: Foundational Integrity**
1.  **Identity Gate** (Minimal implementation)
2.  **Policy Gate** (Basic Ring Model checks)
3.  **Audit/Event Emission** (Logging the Gate result: `guard_events.py`)

**Phase 2: Structure Enforcement**
1.  **Contract Gate** (Schema validation for write/read payloads)
2.  **Runtime Hooks** (Hooking into system APIs: `runtime_hook.py`)
3.  **Memory Hooks** (Intercepting `memory_write` calls)

**Phase 3: Risk Management**
1.  **Risk Gate Engine** (Initial scoring logic on tool chains)
2.  **Quarantine Flow** (Handling the intermediate state)
3.  **Sentinel Integration** (Making TGuard aware of live session state)

**Phase 4: Truth & Permanence**
1.  **Provenance Gate** (Mandating source attribution for all knowledge modification)
2.  **Constitutional Memory Protection** (Hardcoding the rules against self-mutation)

**Phase 5: Adaptation**
1.  **Pattern Learning:** Analyzing `guard_events` to propose permanent hardening rules and schema updates.

## Implementation Modules (Skeleton)

The structure should reflect these functional modules:

```
tehuti-guard/
├── contracts/
│   ├── identity.py       # Schema for Identity metadata
│   ├── policy_input.py   # Schema for policy context inputs
│   └── policy_output.py  # Schema for policy decision outputs
├── evaluators/
│   ├── identity_gate.py
│   ├── intent_gate.py
│   ├── contract_gate.py
│   ├── policy_gate.py
│   ├── risk_gate.py
│   └── provenance_gate.py
├── engines/
│   ├── policy_engine.py
│   ├── risk_engine.py
│   ├── escalation_engine.py
│   └── quarantine_engine.py
├── integrations/
│   ├── runtime_hook.py   # Primary execution interception point
│   ├── memory_hook.py    # Intercepting memory/lesson writes
│   ├── sentinel_hook.py  # Checking live session/device state
│   └── mcp_hook.py       # Intercepting MCP/API calls
├── logs/
│   └── guard_events.py   # Canonical decision logging (the audit sink)
└── tests/
    ├── test_identity.py
    ├── test_policy.py
    ├── test_quarantine.py
    └── test_promotion_protection.py
```

---
**FINAL INSTRUCTION FOR THE TEAM:**
Tehuti Guard must evolve from a permission helper into a constitutional control plane. Every meaningful action must pass identity, intent, contract, policy, risk, and provenance checks before it can affect runtime, memory, tools, or configuration. Mythos-class systems render ungated intelligence unacceptable; Guard must be the hard boundary between model output and real-world consequence.