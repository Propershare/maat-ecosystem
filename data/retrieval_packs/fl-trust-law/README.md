# fl-trust-law retrieval pack

Florida trust / probate law corpus used as a **test payload** for the MAAT
retrieval-pack mechanism. This is *one* pack behind *one* gateway
(`fl-trust-law` in [`registry.yaml`](../../../maat-ecosystem/skeleton/gateways/registry.yaml)).
It is **not** the point of the system — the point is that the mechanism works
the same for this pack as it would for any other.

## Contents

Canonically installed into `documents/` from either:

- **`Legal_AI_FL/`** at the lab root (preferred when `law_data_clean/` is present), or
- **`Legal_AI_FL.rar`** at the lab root (fallback: `unrar` into `documents/`).

- `documents/law_data_clean/fl_cases/` — Florida trust/probate case opinions (markdown).
- `documents/law_data_clean/fl_statutes/` — Florida Statutes chapter 731 etc.
- `documents/law_data_clean/fl_rules/` — Florida Probate Rules, Civil Procedure.
- `documents/law_data_raw/` — raw scrapes, kept for provenance; prefer `law_data_clean/` for retrieval.
- `documents/rag/` — pack-internal build artifacts (may be regenerated).

## Install / reinstall

```bash
bash data/retrieval_packs/fl-trust-law/scripts/install.sh
```

The script syncs from `Legal_AI_FL/` or extracts `Legal_AI_FL.rar` into
`documents/`, then prints the aggregate checksum, which should match
`aggregate_sha256` in `manifest.json`.
If it does not match, the pack is out of date — rebuild embeddings before
promoting any change through [`forge/retrieval_proposals.py`](../../../gemma4-toolshim/swarm/forge/retrieval_proposals.py).

## Guardrails

This pack is bound to a KA2-compliant gateway. The gateway is responsible for:

1. Tagging requests with `research_type: applied`, `level_of_analysis: institution`
   (defaults; [`ka2_router.py`](../../../gemma4-toolshim/swarm/ka2_router.py) can widen).
2. Emitting an RBL flag on scope drift — queries that are not about Florida
   trust/probate law. Agents must refuse to answer from this pack in that case.
3. Never issuing legal advice. Research and citation only.

The `guard_validator` in [`guard_validator.py`](../../../gemma4-toolshim/swarm/guard_validator.py)
will deny turns that surface this pack in response to out-of-scope questions,
once the scope-drift detector is wired to `rbl_flags_on_scope_drift`.

## Changing this pack

Do not hand-edit `documents/`. Propose changes through the Forge:

```python
from forge.retrieval_proposals import propose_pack_change
propose_pack_change(
    pack_id="fl-trust-law",
    change="add",           # or "retire" / "rerank"
    rationale="...",
)
```

The proposal goes through Maatbench → Tehuti Guard → registry update,
per [`MAAT-EVOLUTION-LANES.md`](../../../docs/MAAT-EVOLUTION-LANES.md).
