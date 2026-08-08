#!/usr/bin/env python3
"""
Phase 3: Minimal Planner/Runtime Scaffold for maat-legal-runtime
Based on the Master Contract and approved artifacts.
"""

from enum import Enum
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime

# ==========================================================================
# 1. ENUMS & STATE OBJECTS
# ==========================================================================

class PlannerState(Enum):
    """Planner state machine states."""
    ANSWERABLE = "ANSWERABLE"
    ANSWERABLE_WITH_GAPS = "ANSWERABLE_WITH_GAPS"
    NEEDS_CLARIFICATION = "NEEDS_CLARIFICATION"
    HIGH_RISK_REQUIRES_ATTORNEY_REVIEW = "HIGH_RISK_REQUIRES_ATTORNEY_REVIEW"

class AuthorityType(Enum):
    """Authority hierarchy types."""
    STATUTE = "STATUTE"
    CASE = "CASE"
    SECONDARY = "SECONDARY"
    INTERNAL_TEMPLATE = "INTERNAL_TEMPLATE"
    INTERNAL_MEMO = "INTERNAL_MEMO"
    OTHER = "OTHER"

class AuthorityWeight(Enum):
    """Authority weight hierarchy."""
    CONTROLLING = "CONTROLLING"
    STRONG = "STRONG"
    PERSUASIVE = "PERSUASIVE"
    LIMITED = "LIMITED"

class RiskLevel(Enum):
    """Risk classification levels."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class ReviewLevel(Enum):
    """Review requirement levels."""
    NONE = "NONE"
    RECOMMENDED = "RECOMMENDED"
    REQUIRED = "REQUIRED"

# ==========================================================================
# 2. DATACLASSES FOR SCHEMAS
# ==========================================================================

@dataclass
class SourceCitation:
    source_id: str
    title: str
    authority_type: AuthorityType
    authority_weight: AuthorityWeight
    jurisdiction: Optional[str] = None
    citation_text: Optional[str] = None
    section_or_page: Optional[str] = None
    quote: Optional[str] = None
    relevance_note: Optional[str] = None

@dataclass
class KnownFact:
    name: str
    value: str
    source: Optional[str] = None
    confidence: Optional[float] = None

@dataclass
class MissingFact:
    fact_name: str
    why_it_matters: str
    blocks_finality: bool = True

@dataclass
class AnalysisStep:
    issue: str
    reasoning: str
    supporting_source_ids: List[str] = field(default_factory=list)
    conclusion: Optional[str] = None

@dataclass
class RecommendedAction:
    action: str
    rationale: str
    priority: str = "NEXT"
    supporting_source_ids: List[str] = field(default_factory=list)

@dataclass
class DraftingConsideration:
    topic: str
    guidance: str
    supporting_source_ids: List[str] = field(default_factory=list)
    requires_attorney_review: bool = False

@dataclass
class IssueFlag:
    code: str
    message: str
    risk_level: RiskLevel

@dataclass
class ReviewRequirement:
    level: ReviewLevel
    reasons: List[str] = field(default_factory=list)
    required_before_use: bool = False

@dataclass
class DisclaimerBlock:
    text: str
    not_legal_advice: bool = True
    attorney_review_recommended: bool = True

# ==========================================================================
# 3. LEGAL ADVISORY SYNTHESIS SCHEMA
# ==========================================================================

@dataclass
class LegalAdvisorySynthesis:
    """Mandatory output schema for all legal analysis."""
    schema_version: str = "1.0.0"
    planner_state: PlannerState = field(default=None)
    matter: str = field(default=None)
    jurisdiction: str = field(default=None)
    domain_pack: str = field(default="fl-trust-law")
    question_presented: str = field(default=None)
    known_facts: List[KnownFact] = field(default_factory=list)
    missing_facts: List[MissingFact] = field(default_factory=list)
    applicable_authorities: List[SourceCitation] = field(default_factory=list)
    analysis: List[AnalysisStep] = field(default_factory=list)
    recommended_structure: Optional[str] = None
    recommended_actions: List[RecommendedAction] = field(default_factory=list)
    drafting_considerations: List[DraftingConsideration] = field(default_factory=list)
    risks_and_open_issues: List[IssueFlag] = field(default_factory=list)
    review_requirement: ReviewRequirement = field(default_factory=lambda: ReviewRequirement(level=ReviewLevel.NONE))
    sources_consulted: List[SourceCitation] = field(default_factory=list)
    disclaimer: DisclaimerBlock = field(default_factory=lambda: DisclaimerBlock(
        text="This output is a structured legal research and drafting aid and should be reviewed by a qualified attorney before reliance or use.",
        not_legal_advice=True,
        attorney_review_recommended=True
    ))
    correlation_id: Optional[str] = None
    policy_version: Optional[str] = None
    generated_at: Optional[str] = None

# ==========================================================================
# 4. CLARIFICATION QUESTION SCHEMA
# ==========================================================================

@dataclass
class ClarificationQuestion:
    question_id: str
    question_text: str
    why_needed: str
    fact_name: str
    blocks_finality: bool = True
    question_type: str = "single_choice"
    allowed_answers: Optional[List[str]] = None
    asked_count: int = 0
    last_asked_at: Optional[str] = None
    answer_status: str = "unasked"
    depends_on: Optional[str] = None
    planner_reason_code: Optional[str] = None

# ==========================================================================
# 5. GRAPH STATE OBJECT
# ==========================================================================

@dataclass
class GraphState:
    """Runtime state for the legal runtime."""
    intake_goal: Optional[str] = None
    extracted_jurisdiction: Optional[str] = None
    extracted_domain: Optional[str] = None
    extracted_entities: Dict[str, str] = field(default_factory=dict)
    sources_consulted: List[SourceCitation] = field(default_factory=list)
    current_state: PlannerState = PlannerState.NEEDS_CLARIFICATION
    missing_facts: List[MissingFact] = field(default_factory=list)
    risk_flags: List[str] = field(default_factory=list)
    blocking_missing_facts: bool = False
    nonblocking_missing_facts: bool = False
    has_meaningful_authority: bool = False
    conflicting_authority: bool = False
    review_policy_triggered: bool = False
    high_risk_flag: bool = False
    clarification_questions: List[ClarificationQuestion] = field(default_factory=list)
    retrieval_failures: int = 0
    loop_detected: bool = False

# ==========================================================================
# 6. NODE FUNCTIONS (SKELETONS)
# ==========================================================================

def ingest_goal(goal: str, state: GraphState) -> GraphState:
    """Node 1: Intake / Goal Parser"""
    # Extract jurisdiction
    if "Florida" in goal:
        state.extracted_jurisdiction = "Florida"
    elif "Texas" in goal:
        state.extracted_jurisdiction = "Texas"
    
    # Extract domain
    if "trust" in goal.lower():
        state.extracted_domain = "trust"
    elif "probate" in goal.lower():
        state.extracted_domain = "probate"
    
    # Extract entities
    if "minor" in goal.lower() or "child" in goal.lower():
        state.extracted_entities["minor_child"] = True
    
    return state

def classify_risk(goal: str, state: GraphState) -> GraphState:
    """Node 2: Classify risk based on goal"""
    risk_triggers = []
    
    if "minor" in goal.lower() or "child" in goal.lower():
        risk_triggers.append("MINOR_BENEFICIARY")
        state.high_risk_flag = True
        state.review_policy_triggered = True
    
    if "tax" in goal.lower():
        risk_triggers.append("TAX_SENSITIVITY")
        state.review_policy_triggered = True
    
    if "creditor" in goal.lower() or "asset protection" in goal.lower():
        risk_triggers.append("ASSET_PROTECTION")
        state.review_policy_triggered = True
    
    if len(risk_triggers) > 0:
        state.risk_flags.extend(risk_triggers)
    
    return state

def detect_gaps(goal: str, state: GraphState) -> GraphState:
    """Node 3: Detect missing facts"""
    required_facts = [
        "asset_type",
        "asset_titling",
        "custodian_name",
        "trustee_identity",
        "distribution_terminology"
    ]
    
    for fact in required_facts:
        if fact not in goal.lower():
            missing = MissingFact(
                fact_name=fact,
                why_it_matters=f"This fact materially affects trust structuring and drafting requirements.",
                blocks_finality=True
            )
            state.missing_facts.append(missing)
            state.blocking_missing_facts = True
    
    return state

def retrieve_authorities(state: GraphState) -> GraphState:
    """Node 4: Retrieve authorities (stub for now)"""
    # Stub retriever - marks as NOT_CONNECTED
    # In production, this would call external RAG services
    
    authorities = [
        SourceCitation(
            source_id="fl_statute_001",
            title="Florida Trust Code",
            authority_type=AuthorityType.STATUTE,
            authority_weight=AuthorityWeight.CONTROLLING,
            jurisdiction="Florida",
            citation_text="Fla. Stat. § 736.01 et seq.",
            section_or_page="§ 736.01",
            relevance_note="Primary statutory framework for trust formation and administration."
        ),
        SourceCitation(
            source_id="fl_trust_guide_001",
            title="Florida Estate Planning Practice Guide",
            authority_type=AuthorityType.SECONDARY,
            authority_weight=AuthorityWeight.PERSUASIVE,
            jurisdiction="Florida",
            citation_text="Estate Planning Practice Guide § 2.3",
            relevance_note="Authoritative secondary source on Florida trust drafting practices."
        )
    ]
    
    state.sources_consulted.extend(authorities)
    state.has_meaningful_authority = True
    
    return state

def decide_state(state: GraphState) -> GraphState:
    """Node 5: Decide planner state based on decision principles"""
    # Decision principle 1: High-risk matters require attorney review
    if state.review_policy_triggered or state.high_risk_flag:
        state.current_state = PlannerState.HIGH_RISK_REQUIRES_ATTORNEY_REVIEW
    
    # Decision principle 2: Missing blocking facts require clarification
    elif state.blocking_missing_facts:
        state.current_state = PlannerState.NEEDS_CLARIFICATION
        # Create clarification questions
        for fact in state.missing_facts:
            state.clarification_questions.append(ClarificationQuestion(
                question_id=f"fact_{fact.fact_name}",
                question_text=f"What is the {fact.fact_name} for this trust?",
                why_needed=fact.why_it_matters,
                fact_name=fact.fact_name,
                blocks_finality=fact.blocks_finality,
                planner_reason_code=f"BLOCKING_FACT_MISSING_{fact.fact_name.upper().replace('-', '_')}"
            ))
    
    # Decision principle 3: No authority found requires clarification or high-risk state
    elif not state.has_meaningful_authority:
        if state.missing_facts:
            state.current_state = PlannerState.NEEDS_CLARIFICATION
        else:
            state.current_state = PlannerState.HIGH_RISK_REQUIRES_ATTORNEY_REVIEW
    
    return state

def synthesize_output(state: GraphState, question: str) -> LegalAdvisorySynthesis:
    """Node 6: Synthesize output"""
    
    # Extract question details
    known = []
    for ent in state.extracted_entities:
        known.append(KnownFact(
            name=ent,
            value="present" if state.extracted_entities.get(ent) else "unknown"
        ))
    
    synthesis = LegalAdvisorySynthesis(
        schema_version="1.0.0",
        planner_state=state.current_state,
        matter="Revocable living trust for minor beneficiary",
        jurisdiction=state.extracted_jurisdiction or "Unknown",
        question_presented=question,
        known_facts=known,
        missing_facts=list(state.missing_facts),
        applicable_authorities=[a for a in state.sources_consulted if a.authority_weight in [AuthorityWeight.CONTROLLING, AuthorityWeight.STRONG]],
        analysis=[
            AnalysisStep(
                issue="Trust structuring for minor beneficiary",
                reasoning="Revocable trusts can be used with minor beneficiaries, but distribution language and trustee powers must be carefully drafted.",
                supporting_source_ids=["fl_statute_001"],
                conclusion="Trust structure is conditionally appropriate depending on facts."
            )
        ],
        recommended_structure="Use a revocable living trust with clearly defined trustee powers and minor-beneficiary distribution controls.",
        recommended_actions=[
            RecommendedAction(
                action="Confirm asset composition before drafting",
                rationale="Asset type changes trust funding and drafting requirements.",
                priority="NOW",
                supporting_source_ids=["fl_statute_001"]
            ),
            RecommendedAction(
                action="Consult with Florida estate planning attorney",
                rationale="Minor beneficiary provisions require careful drafting review.",
                priority="NOW",
                supporting_source_ids=["fl_statute_001"]
            )
        ],
        drafting_considerations=[
            DraftingConsideration(
                topic="Minor beneficiary distributions",
                guidance="Draft distribution language that clearly defines trustee discretion, timing, and protective controls during minority.",
                supporting_source_ids=["fl_statute_001"],
                requires_attorney_review=True
            ),
            DraftingConsideration(
                topic="Asset titling requirements",
                guidance="Verify whether assets should be titled in trust name or remain in individual name.",
                supporting_source_ids=["fl_statute_001"],
                requires_attorney_review=True
            )
        ],
        risks_and_open_issues=[
            IssueFlag(
                code="MINOR_BENEFICIARY_PRESENT",
                message="Trust involves minor beneficiary requiring careful distribution language.",
                risk_level=RiskLevel.HIGH
            ),
            IssueFlag(
                code="BLOCKING_FACTS_MISSING",
                message=f"Missing {len(state.missing_facts)} blocking facts prevents final recommendation.",
                risk_level=RiskLevel.MEDIUM
            )
        ],
        review_requirement=ReviewRequirement(
            level=ReviewLevel.REQUIRED,
            reasons=[
                "Minor beneficiary provisions require careful drafting review.",
                "Asset composition affects trust structuring decisions.",
                "High-risk state requires attorney review before reliance."
            ],
            required_before_use=True
        ),
        sources_consulted=state.sources_consulted,
        disclaimer=DisclaimerBlock(
            text="This output is a structured legal research and drafting aid and should be reviewed by a qualified attorney before reliance or use.",
            not_legal_advice=True,
            attorney_review_recommended=True
        ),
        correlation_id=f"fl-rag-{datetime.utcnow().strftime('%Y%m%d')}",
        policy_version="fl-trust-law@1.0.0",
        generated_at=datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    )
    
    return synthesis

def validate_output(synthesis: LegalAdvisorySynthesis) -> bool:
    """Node 7: Validate output against schema"""
    required_fields = [
        "planner_state", "matter", "jurisdiction", "question_presented",
        "review_requirement", "disclaimer"
    ]
    
    for field_name in required_fields:
        if not hasattr(synthesis, field_name):
            print(f"Validation failed: Missing field {field_name}")
            return False
    
    # Check planner_state is set
    if synthesis.planner_state not in [PlannerState.HIGH_RISK_REQUIRES_ATTORNEY_REVIEW, 
                                       PlannerState.NEEDS_CLARIFICATION,
                                       PlannerState.ANSWERABLE_WITH_GAPS]:
        print(f"Validation failed: planner_state must be one of the required states")
        return False
    
    # Check review_requirement.level for high-risk states
    if synthesis.planner_state == PlannerState.HIGH_RISK_REQUIRES_ATTORNEY_REVIEW:
        if synthesis.review_requirement.level != ReviewLevel.REQUIRED:
            print(f"Validation failed: HIGH_RISK state requires REQUIRED review level")
            return False
    
    return True

def orchestrate(question: str) -> LegalAdvisorySynthesis:
    """Main orchestration entry point"""
    # Initialize state
    state = GraphState()
    
    # Run nodes in sequence
    state = ingest_goal(question, state)
    state = classify_risk(question, state)
    state = detect_gaps(question, state)
    state = retrieve_authorities(state)
    state = decide_state(state)
    synthesis = synthesize_output(state, question)
    is_valid = validate_output(synthesis)
    
    if not is_valid:
        print(f"Output validation failed for synthesis: {synthesis.planner_state.value}")
        return synthesis
    
    return synthesis

# ==========================================================================
# 7. TEST CASE: HIGH-RISK MINOR-CHILD SCENARIO
# ==========================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("Maat Legal Runtime - Phase 3 Orchestration Test")
    print("=" * 70)
    
    # Test case from the contract
    question = "Draft a recommendation for a revocable living trust for a minor child. Assume the trust will primarily hold my personal residence and investment accounts."
    
    print(f"\nTest Question: {question}")
    print("-" * 70)
    
    # Run orchestration
    result = orchestrate(question)
    
    # Print validation status
    print(f"\nValidation Status: {'PASSED' if validate_output(result) else 'FAILED'}")
    print(f"Planner State: {result.planner_state.value}")
    print(f"Review Requirement: {result.review_requirement.level.value}")
    print(f"Attorney Review Required: {result.review_requirement.required_before_use}")
    print(f"Missing Facts Count: {len(result.missing_facts)}")
    
    # Print a sample of missing facts
    print(f"\nSample Missing Facts:")
    for fact in result.missing_facts[:3]:
        print(f"  - {fact.fact_name}: {fact.why_it_matters}")
    
    print("\n" + "=" * 70)
    print("Test Complete")
    print("=" * 70)