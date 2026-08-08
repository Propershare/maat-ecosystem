# Ma’at Toolkit Blueprint

Use this blueprint to define, build, govern, and ship MAAT-native toolkits that can stand alone as products, operate inside the lab ecosystem, or serve as governed runtime organs.

**How to use:** copy this file (or duplicate the repo path), replace bracketed placeholders, and version the filled document alongside the toolkit repo.

---

# 1. Toolkit Identity

## Toolkit Name

`[NAME]`

## Version

`v0.1.0`

## One-Sentence Description

`[What this toolkit does in one sentence]`

## Core Promise

`[What problem it solves and why it matters]`

## Toolkit Role

Choose one primary role:

- Standalone product
- Standalone service/API
- Ecosystem organ
- Adapter / proxy / bridge
- Internal lab tool
- Premium / enterprise enhancement

## Product Boundary

This toolkit is:

`[What it is]`

This toolkit is not:

`[What it is not]`

## Target User

- Solo user
- Family / household
- Small business
- Legal / professional practice
- Research lab
- Enterprise team
- Developer platform
- Other: `[SPECIFY]`

## Delivery Model

- Offline / local-first
- Hosted SaaS
- Hybrid local + cloud
- Self-hosted enterprise
- API-only

---

# 2. Ma’at Initiation (Human First)

> The system understands the human. The human does not need to understand the system.

## Entry Questions

The toolkit must begin in plain language, not internal jargon.

### What is the user trying to do?

`[Describe]`

### What could go wrong if it fails?

- nothing serious
- could break something
- could cost money
- could affect real people
- regulated / high-risk

### Where is it running?

- my computer
- server
- cloud
- mobile
- not sure

### Should the system pause before risky actions?

- yes
- no
- only for major actions

### What is the user bringing?

- their own database
- their own tools
- their own model
- documents / corpora
- nothing yet

## Initiation Summary Format

What the system should say back in 1–2 sentences:

`[Short plain-language summary of what the user is doing and how cautious the system will be]`

## Internal Translation (for builders only)

Map human answers to runtime behavior, policy mode, risk level, and required components.

---

# 3. Product Definition

## Primary Use Cases

1. `[USE CASE 1]`
2. `[USE CASE 2]`
3. `[USE CASE 3]`

## Jobs To Be Done

- `[JOB 1]`
- `[JOB 2]`
- `[JOB 3]`

## Out of Scope

List what this toolkit will NOT do.

- `[OUT OF SCOPE 1]`
- `[OUT OF SCOPE 2]`
- `[OUT OF SCOPE 3]`

## Success Criteria

- `[METRIC / OUTCOME 1]`
- `[METRIC / OUTCOME 2]`
- `[METRIC / OUTCOME 3]`

---

# 4. Ma’at Positioning

## Why This Toolkit Exists In The Ma’at Ecosystem

`[Explain how this toolkit fits the larger MAAT vision]`

## Required Ma’at Principles

- [ ] Truth
- [ ] Order
- [ ] Balance
- [ ] Justice
- [ ] Reciprocity
- [ ] Integrity
- [ ] Stewardship
- [ ] Responsibility
- [ ] Discernment
- [ ] Righteousness

## Governance Mode

- Strict
- Standard
- Flexible

## Trust Level

- High-trust / governed outputs required
- Medium-trust / reviewable outputs
- Low-trust / exploratory outputs only

---

# 5. Truth, Verification, and Learning

## Truth Construction

What counts as truth in this toolkit?

- human-reviewed records
- domain sources
- policy documents
- labeled cases
- structured memory
- other: `[SPECIFY]`

## Truth Review Process

How is truth checked before becoming canonical?

- `[REVIEW STEP 1]`
- `[REVIEW STEP 2]`
- `[REVIEW STEP 3]`

## Evaluation

How do we test whether the toolkit aligns with truth?

- benchmark / eval set
- human review
- disagreement review
- golden cases
- regression suite

## Verification

How is correctness checked repeatedly over time?

- benchmark reruns
- CI suite
- runtime logs
- contract validation
- periodic review

## Learning Loop

How does the toolkit improve?

- reviewer corrections
- eval failures
- policy updates
- retrieval fixes
- playbooks
- approved memory updates

## What May Change Automatically

`[What can adapt without human approval]`

## What Must Never Change Automatically

`[What requires human review / approval]`

---

# 6. Runtime Model

## Runtime Base

- Maat runtime
- Custom runtime
- Other: `[SPECIFY]`

## Role Model

- Single-agent
- Scout / Analyst / Archivist
- Multi-specialist
- Human + agent copilot
- Planner + specialists

## Authority Model

- User is final authority
- Admin team is final authority
- Policy engine is final gate before execution
- Human review required for high-risk actions

## Deployment Surface

- CLI
- TUI
- Web app
- Desktop app
- Mobile companion
- API only

---

# 7. Toolkit Architecture

## Components Used

- [ ] Tehuti Core
- [ ] Tehuti Guard
- [ ] Maat Memory
- [ ] Session Index
- [ ] RAG subsystem
- [ ] Voice subsystem
- [ ] Filesystem / Hands MCP
- [ ] Senses / automation
- [ ] Blood / event pipeline
- [ ] Sentinel
- [ ] Other MCPs: `[LIST]`

## External vs Internal

### External Standalone Services

- `[SERVICE 1]`
- `[SERVICE 2]`

### Runtime-Embedded Features

- `[FEATURE 1]`
- `[FEATURE 2]`

## Source of Truth

Which component is authoritative?

- `[COMPONENT / CONTRACT / SERVICE]`

## Request Flow

```text
User → Initiation → Runtime → Contract Validation → Guard / Planner → Tool / Memory / Model → Event Log → Result
```

## Data & Event Boundaries (optional)

`[Where data may leave the trust boundary; what gets logged; retention]`

---

# 8. Ship Checklist (fill before release)

- [ ] Initiation copy reviewed (plain language, no jargon)
- [ ] Guard / policy paths tested for high-risk actions
- [ ] Source of truth and fallbacks documented
- [ ] Eval or golden cases for regressions
- [ ] Operator runbook (install, upgrade, backup, restore)
