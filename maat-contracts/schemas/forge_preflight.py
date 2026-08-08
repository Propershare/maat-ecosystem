# Schema Definition: forge_preflight

This schema formalizes the record written to the `maat_governance_events` table when `maat-forge` executes a preflight check, regardless of the final outcome. It serves as the direct link between the Governance layer and the structured Memory Contract.

**Target Module:** `maat-contracts/schemas/forge_preflight.py`
**Purpose:** To record the audit trail of the preflight decision, not the experimental result itself.

## Structure Definition

| Field Name | Data Type | Description | Constraints |
| :--- | :--- | :--- | :--- |
| `record_id` | UUID | Unique ID for this specific preflight execution log. | Mandatory. |
| `timestamp` | ISO 8601 | Time the decision was received by the system. | Mandatory. |
| `correlation_id` | String | Stable ID linking this log to the original high-level task/intent. | Mandatory. |
| `job_type` | Enum | The nature of the attempt (e.g., `preflight_check`, `system_repair`, `model_update`). | Mandatory (Use `maat-contracts/Enums.py`). |
| `risk_class` | Enum | The assessed risk of the *intended* operation (`low_risk`, `medium_risk`, `high_risk`, `constitutional_risk`). | Mandatory. |
| `guard_decision` | Enum | The explicit outcome from Tehuti Guard (`allow`, `deny`, `blocked_constitutional`, `unknown`). | Mandatory. |
| `guard_details` | JSON | Detailed payload returned by Guard, including all violation details (`{...}`). | Mandatory (Contains all rule failures). |
| `guard_message` | String | A human-readable summary of the Guard's reasoning. | Mandatory. |
| `outcome` | Enum | The resulting execution status based on the decision (`allowed_to_proceed`, `halted_by_guard`, `unknown_state`). | Mandatory. |
| `triggered_contracts` | Array[SchemaRef] | List of contracts that were *checked* (e.g., `Identity`, `Memory`). | Mandatory (For provenance). |
| `source_metadata` | JSON | Contextual metadata (e.g., source of the intent, originating tool). | Optional. |

### Mandatory Contract Implementation Details:
1.  **Enums:** We must define `job_type`, `risk_class`, `guard_decision`, and `outcome` in `maat-contracts/Enums.py`.
2.  **Schema Enforcement:** We must use a library (like Pydantic or Marshmallow) to ensure serialization adheres to this structure.

---
This file defines the structure; the next step is to test this structure in action.