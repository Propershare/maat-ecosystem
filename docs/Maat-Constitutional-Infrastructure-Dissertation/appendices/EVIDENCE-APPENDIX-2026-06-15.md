# Evidence Appendix — Tehuti Research Lab Case Study

**Date prepared:** 2026-06-15  
**Purpose:** Preserve dissertation-ready evidence for Section VI, "Tehuti Research Lab as a Ma'at-Governed AI Infrastructure Prototype."

This appendix captures operational evidence from the lab. It should be treated as an internal evidence record until public-redaction decisions are made for hostnames, ports, and correlation identifiers.

---

## 1. Current Health Sweep

**Timestamp:** 2026-06-15T14:29:51Z  
**Method:** local HTTP probes from the lab host to loopback service endpoints.

| Component | Endpoint | Result |
|---|---|---|
| Ka Discovery health | `http://127.0.0.1:8010/health` | Reachable, HTTP 200 |
| Ka Discovery manifest | `http://127.0.0.1:8010/manifest` | Reachable, HTTP 200 |
| Tehuti Guard | `http://127.0.0.1:8013/health` | Unreachable, connection refused |
| Tehuti Core | `http://127.0.0.1:8014/openapi.json` | Reachable, HTTP 200 |
| Filesystem MCP | `http://127.0.0.1:8016/openapi.json` | Reachable, HTTP 200 |
| Postgres MCP | `http://127.0.0.1:8017/openapi.json` | Reachable, HTTP 200 |
| Memory MCP | `http://127.0.0.1:8018/openapi.json` | Reachable, HTTP 200 |
| ComfyUI MCP | `http://127.0.0.1:8019/openapi.json` | Reachable, HTTP 200 |
| Maat Memory MCP | `http://127.0.0.1:8022/openapi.json` | Reachable, HTTP 200 |
| maat-sentinel | `http://127.0.0.1:4242/health` | Unreachable, connection refused |
| OpenClaw gateway | `http://127.0.0.1:18790/` | Reachable, HTTP 200 |
| Ollama | `http://127.0.0.1:11434/api/tags` | Reachable, HTTP 200 |

**Interpretation:** The shared-organ architecture is mostly live, but the policy/posture path is not: Tehuti Guard and Sentinel are not currently reachable. This supports the manuscript's "advertised-but-absent governance" finding and shows why Ma'at-governed infrastructure needs liveness checks, not just service manifests.

---

## 2. 2026-06-06 Guard Positive Control

**Source:** gitMaat / `maat_governance_events` table  
**Record ID:** `42c1c0d4-ce47-496c-b52f-66f51c5805d6`  
**Timestamp:** `2026-06-06T14:52:03.698102+00:00`  
**Record type:** `guard_decision`  
**Machine:** `staydangerous`  
**Agent/source:** `tehuti-guard-api`  
**Correlation ID:** `maat-security-stack:20260606T144720Z:3efa879b:guard-sentinel-smoke`  
**Policy version:** `1`

Key payload:

```json
{
  "decision": "allow",
  "severity": "info",
  "reason": "Operational posture; low-risk action allowed",
  "matched_rules": ["operational_low_risk_allow"],
  "agent_id": "cursor_staydangerous",
  "machine_id": "staydangerous",
  "source_service": "tehuti-guard-api",
  "explanation_id": "sha256:eef97e3dc83e8c9ff5502e340ef442dc45093d32f24a4c288291d5fbbdc02429"
}
```

**Interpretation:** This is the positive control for Tehuti Guard. It proves that the policy gate can issue an `allow` decision when posture context is available and the action is low-risk.

---

## 3. 2026-06-06 Fail-Safe Control

**Source:** gitMaat / `maat_governance_events` table  
**Record ID:** `d8d4e16d-5537-4d15-a681-92a6aaa6184c`  
**Timestamp:** `2026-06-06T14:51:21.785972+00:00`  
**Record type:** `guard_decision`  
**Machine:** `staydangerous`  
**Agent/source:** `tehuti-guard-api`  
**Correlation ID:** `maat-security-stack:20260606T144720Z:3efa879b:guard-smoke`

Key payload:

```json
{
  "decision": "review",
  "severity": "warning",
  "reason": "Sentinel unified view unavailable — cannot align posture",
  "matched_rules": ["sentinel_unreachable_review"],
  "agent_id": "cursor_staydangerous",
  "machine_id": "staydangerous",
  "source_service": "tehuti-guard-api",
  "explanation_id": "sha256:e8bc8d7e81c706ca69ef1f78aa74a2d80951615d0a1d662f8c58ca0f8970bb0d"
}
```

**Interpretation:** This demonstrates fail-safe behavior: when posture evidence is unavailable, Guard returns `review`, not silent `allow`.

---

## 4. 2026-06-06 Sentinel Posture Context

**Source:** gitMaat / `maat_governance_events` table  
**Record ID:** `f16c9717-a81b-4425-b729-8ab093205a0d`  
**Timestamp:** `2026-06-06T14:51:59.097377+00:00`  
**Record type:** `sentinel_posture_summary`  
**Machine:** `staydangerous`  
**Agent/source:** `maat-sentinel`

Key payload:

```json
{
  "machine_status": "operational",
  "risk_summary": "No elevated signals in recent window",
  "requires_human_review": false,
  "recent_blocked_count": 0,
  "recent_critical_count": 0,
  "blocking_actions_count": 0,
  "fingerprint_changed": false
}
```

**Interpretation:** This is the posture context that makes the later `allow` decision meaningful. Guard's behavior changes in relation to machine state; it is not a static allowlist.

---

## 5. Dissertation Finding Supported

This appendix supports the dissertation's claim that Ma'at-governed AI requires **liveness and conformance**:

- The 2026-06-06 records show the constitutional gate working when dependencies are healthy.
- The 2026-06-15 health sweep shows the policy/posture path currently absent while other organs remain live.
- The contrast demonstrates why a manifest entry or written policy is insufficient; constitutional infrastructure must continuously prove its gates are running and its contracts are being spoken.
