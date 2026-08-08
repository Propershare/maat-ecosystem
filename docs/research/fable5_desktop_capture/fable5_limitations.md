# Fable 5 Capture — Known Limitations

**Maturity:** Research-validated governance prototype capture — not API-pure evaluation.

## Adapter limitations

1. **Desktop-assisted capture** — not a reproducible API endpoint.
2. **Claude Desktop wrapper** — hidden system prompt may affect behavior.
3. **Model version drift** — Fable 5 identifier and date must be recorded manually.
4. **No decoding control** — temperature / max tokens often unknown.
5. **Workspace access** — Fable may read local files; environment differs from API users.

## Evaluation limitations

1. **Not full 251-case eval** unless explicitly completed and manifest says so.
2. **Prompted vs default** — two arms; do not mix in one score without labeling.
3. **Refusals stay in denominator** — per cross-model design.
4. **Wire vocabulary** — models may emit `defer` / `escalate` instead of `allow` / `review` / `deny`.
5. **Compiler path** — scoring requires local MaatBench 0.3.2 (`MAATBENCH_PATH`).

## What this can prove

- Whether a frontier-class model improves **judgment** vs Ornith baseline.
- Whether **raw integrated covenant validity** improves with prompting.
- Whether **compiler-enforced governance** remains necessary.
- Whether repair **burden** drops on stronger models.

## What this cannot prove

- Enterprise production readiness of Tehuti Guard.
- Model promotion (gates remain closed).
- Elimination of constitutional runtime enforcement without passing raw gates.
