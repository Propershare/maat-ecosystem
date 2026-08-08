# Maat Legal Runtime - Florida Trust Law Runtime

## 📋 **System Overview**

A **Planner-First**, **Citation-Grounded** legal research and drafting system for Florida trust law, built on the Maat Legal Runtime architecture.

**Key Features:**
- ✅ **Planner State Machine** - Enforces rigorous analysis before answering
- ✅ **Authority Hierarchy** - Statutes > Cases > Secondary > Internal
- ✅ **Structured Output** - Schema-conformant legal memos
- ✅ **Risk Escalation** - Auto-flags high-risk matters for attorney review
- ✅ **Gap Detection** - Identifies missing facts that block finality
- ✅ **Review Queue** - Bridges AI analysis with professional review

## 🏛️ **Architecture**

```
User Goal → Planner State Machine → [RAG Retrieval] → Authority Ranker → Synthesis → Review Flags
```

### **State Machine**

| State | When |
|-------|------|
| `ANSWERABLE` | All facts present, law clear |
| `ANSWERABLE_WITH_GAPS` | Provisional answer with missing facts |
| `NEEDS_CLARIFICATION` | Ambiguous goal or blocking facts missing |
| `HIGH_RISK_REQUIRES_ATTORNEY_REVIEW` | Minors, tax, asset protection, or high-risk triggers |

### **Authority Hierarchy**

1. **Controlling Authority** - Florida statutes, controlling case law
2. **Strong Authority** - Persuasive case law, secondary sources
3. **Persuasive Authority** - Practice guides, commentary
4. **Internal Templates** - Internal drafting checklists

## 📁 **File Structure**

```
.
├── maat_legal_runtime_phase3.py      # Main runtime implementation
├── README.md                          # This file
├── CHANGELOG.md                       # Version history
└── test_provisional_plan_high_risk.py # Integration test
```

## 🚀 **Quick Start**

```bash
# Install dependencies
pip install pydantic dataclasses

# Run the runtime
python3 maat_legal_runtime_phase3.py

# Or run the integration test
python3 test_provisional_plan_high_risk.py
```

## 🧪 **Test Cases**

| Test Case | Description | Expected Outcome |
|-----------|-------------|------------------|
| **Minor Child Trust** | Revocable living trust for minor beneficiary | `HIGH_RISK_REQUIRES_ATTORNEY_REVIEW` |
| **Adult Beneficiary** | Trust for adult beneficiary | `ANSWERABLE_WITH_GAPS` (with appropriate facts) |
| **Cross-Jurisdiction** | Out-of-state assets, Florida trustee | `HIGH_RISK_REQUIRES_ATTORNEY_REVIEW` |
| **Tax-Sensitive** | Irrevocable trust for tax planning | `HIGH_RISK_REQUIRES_ATTORNEY_REVIEW` |

## 📝 **Output Contract**

Every output conforms to the **Legal Advisory Synthesis** schema:

- **Matter** - Short matter label
- **Jurisdiction** - Primary governing jurisdiction
- **Question Presented** - User's legal question
- **Known Facts** - What we know
- **Missing Facts** - What we need
- **Applicable Authorities** - Governing law
- **Analysis** - Structured reasoning
- **Recommended Structure** - Legal structure recommendation
- **Drafting Considerations** - Caveats and templates
- **Risks / Open Issues** - Potential liabilities
- **Review Requirement** - Attorney review flags
- **Sources Consulted** - Full citation list
- **Disclaimer** - Mandatory legal disclaimer

## 🔒 **Safety & Disclaimers**

- ❌ **NOT legal advice** - Always reviewed by qualified attorney
- ✅ **Citation-grounded** - Every conclusion tied to authority
- ✅ **Risk-escalated** - High-risk matters require attorney review
- ✅ **Fact-classified** - Blocking facts identified upfront

## 📚 **Domain Packs**

| Pack | Jurisdiction | Status |
|------|--------------|--------|
| `fl-trust-law` | Florida Trust Code | ✅ v1.0.0 |
| `fl-probate` | Florida Probate Code | 📋 Coming |
| `fl-guardianship` | Florida Guardianship | 📋 Coming |

## 🔧 **Configuration**

| Setting | Value | Description |
|---------|-------|-------------|
| `PGVECTOR_DB_URL` | `postgresql://...` | Postgres vector database |
| `DOMAIN_PACKS_ROOT` | `/fl-trust-law/` | Florida trust corpus |
| `PLANNER_MODEL` | `ollama/gemma4:e4b` | LLM for planner decisions |
| `RETRIEVER_MODEL` | `sentence-transformers/all-MiniLM-L6-v2` | Embedding model |

## 📖 **References**

- [Master Contract](ARCHITECTURE-V2-Roadmap.md)
- [Planner State Machine](PLANNER-STATE-MACHINE-SPEC.md)
- [Legal Advisory Synthesis Schema](LegalAdvisorySynthesis.py)
- [Clarification Question Schema](ClarificationQuestionSchema.py)

## 🤝 **Contributing**

To add a new domain pack:
1. Follow the [Domain Pack Model](PACK-MODEL.md)
2. Include corpus manifest, authority order, issue taxonomy
3. Add eval set and risk policies

## 📮 **License**

This is a governed legal research tool, not a legal advice service. Use in compliance with professional standards.

## 🪶 **Version**

v1.0.0 — April 2026

---

**Built with Maat Alignment** — Truth, Balance, Order.