"""
MAAT Forge — adaptation lab.

Forge proposes changes; it never promotes them directly. The cycle is:

    Proposal -> sandbox -> maatbench -> Tehuti Guard -> registry

All three candidate paths (retrieval, router, LoRA) are sequenced through
:class:`Promoter`. Losers log a ``learning`` row to gitMaat; winners log
a ``decision`` row with the delta.

Stdlib only at module top level; optional deps (e.g. unsloth) are imported
lazily inside :mod:`lora_pipeline` so importing Forge never breaks the shim.
"""

from .base import Candidate, CandidateKind, PromotionResult, Promoter, guard_promote
from .retrieval_proposals import RetrievalPackProposal, propose_retrieval_pack
from .router_proposals import (
    RouterKeywordProposal,
    propose_add_keyword,
    propose_remove_keyword,
)
from .lora_pipeline import (
    DatasetFilterReport,
    LoRACandidate,
    build_dataset,
    is_training_eligible,
    propose_lora,
    run_finetune,
)

__all__ = [
    "Candidate",
    "CandidateKind",
    "PromotionResult",
    "Promoter",
    "guard_promote",
    "RetrievalPackProposal",
    "propose_retrieval_pack",
    "RouterKeywordProposal",
    "propose_add_keyword",
    "propose_remove_keyword",
    "DatasetFilterReport",
    "LoRACandidate",
    "build_dataset",
    "is_training_eligible",
    "propose_lora",
    "run_finetune",
]
