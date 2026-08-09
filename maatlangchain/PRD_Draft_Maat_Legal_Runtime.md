# Proposal: Legal Runtime Toolkit on top of Maat-runtime (Florida Trust Law first)

**Target Repository:** `Propershare/Maat-runtime`
**Author:** Tehuti / Imhotep
**Status:** Draft - Requires Review

## 🚀 1. Overview & Product Statement

**One-Sentence Product Statement:** Maat Legal Runtime is a planner-first, citation-grounded legal research and drafting system that turns domain law packs into review-aware legal work products, starting with Florida trust law and expanding over time.

**Goal:** To create a governed legal workbench that elevates output quality by enforcing process, authority, and review flags, rather than simply summarizing documents.

## 💡 2. The Core Architectural Thesis (Why this design?)

We are moving beyond the limitations of a simple 'Chatbot' or 'Router'.

*   **Problem:** Simple RAG bots answer too early, mix law with generic drafting, and fail to separate fact from authority.
*   **Solution:** Implementation of a **Planner-Governor** layer over specialist Retrieval Nodes.
*   **Maat-runtime Fit:** We leverage `maat-runtime` because it provides the necessary primitives—agent state management, multi-LLM abstraction, and a robust execution surface—allowing us to build a *service* on top of it, rather than a *feature* inside it.

## 🧠 3. System Architecture (The Flow)

The system must follow a mandatory, sequential planning flow, managed by the Planner Node:

**User Goal $\rightarrow$ Planner Node $\rightarrow$ [Call RAG Node A] $\rightarrow$ [Call RAG Node B] $\rightarrow$ Authority Ranker $\rightarrow$ Synthesis $\rightarrow$ Review & Flagging**

**Key Components:**

1.  **Intake / Goal Parser:** (Node 1) Extracts jurisdiction, matter type, entities, and detects missing facts.
2.  **Maat Legal Planner:** (Node 2) Decomposes the goal into a sequenced, executable plan, determining which specialist nodes are required and in what order.
3.  **Domain Retrieval Nodes:** (Node 3) Specialized, read-only endpoints/tools for `FL_TRUST_LAW_RAG`, `FL_PROBATE_RAG`, etc.
4.  **Authority Ranker:** (Node 4) Ranks results by source credibility (Statute > Case Law > Secondary > Internal Template).
5.  **Synthesis Node:** (Node 5) Generates the final, structured memo based only on ranked evidence.
6.  **Risk / Gap Checker:** (Node 6) Final mandatory review of the output for gaps, necessary disclaimers, and review flags.

## 📂 4. Domain Packing & Expansion Strategy

The entire system will be built on the **Domain-Pack Model**. This enforces modularity.

*   **Initial Domain Pack:** `fl-trust-law`
*   **Growth Strategy:** Future domains (`fl-probate`, `ga-trust-law`) will be implemented as self-contained, interchangeable domain packs, requiring only the Planner Node to be updated to call the new tool/node.

## 📝 5. Mandatory Output Contract (Legal Advisory Synthesis)

Every substantive answer *must* conform to the following structured format, ensuring nothing is assumed or missed.

**Legal Advisory Synthesis**
*   **Matter:** [Text]
*   **Jurisdiction:** [Text]
*   **Question Presented:** [Text]
*   **Known Facts:** [List, sourced]
*   **Missing Facts:** [List of critical gaps]
*   **Applicable Authorities:** [List of statutes/cases cited]
*   **Analysis:** [Structured prose]
*   **Recommended Structure / Next Step:** [Actionable plan]
*   **Drafting Considerations:** [Caveats/Templates]
*   **Risks / Open Issues:** [List of potential liabilities/ambiguities]
*   **Review Requirement:** [Mandatory flag: e.g., `HIGH_RISK_REQUIRES_ATTORNEY_REVIEW`]
*   **Sources Consulted:** [Citation list matching authority type]
*   **Disclaimer:** [Mandatory boilerplate disclaimer]

## ✅ 6. Required States & Safety (The Gatekeepers)

The Planner *must* classify its output into one of these states before proceeding to Synthesis:

*   **ANSWERABLE:** All required facts are present, and the law is clear.
*   **ANSWERABLE\_WITH\_GAPS:** Core answer is formed, but X, Y, and Z facts/authorities are missing.
*   **NEEDS\_CLARIFICATION:** The initial goal is ambiguous and cannot proceed without asking the user 1-3 targeted questions.
*   **HIGH\_RISK\_REQUIRES\_ATTORNEY\_REVIEW:** The topic (e.g., tax planning, estate execution) mandates human sign-off regardless of certainty.

***

**Conclusion:** I believe this document accurately captures the vision. I recommend we file this as `docs/LEGAL-RUNTIME-PRD.md` within the proposed `maat-legal-runtime` repo structure.

**Are there any sections you feel need more detail before we finalize this PR document?**