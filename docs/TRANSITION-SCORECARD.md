# Transition Scorecard (Weekly)

Purpose: measure whether the lab is accumulating real transition capacity (quantitative buildup) or just producing activity noise.

## How to use

- Review once per week.
- Score each indicator `0` (off track), `1` (mixed), or `2` (on track).
- Keep evidence links for each score (logs, dashboards, reports, commits).
- Use trend over 4-8 weeks, not one-week spikes.

## Stage gates

- **Stage 1: Quantitative base** - total score < 12
- **Stage 2: Institutional crystallization** - total score 12-20
- **Stage 3: Federation and cross-node coordination** - total score 21-28
- **Stage 4: Superstructure readiness** - total score >= 29

## Indicators (0-2 each, max 32)

| # | Indicator | Measure | 0 | 1 | 2 |
|---|-----------|---------|---|---|---|
| 1 | Useful throughput | Completed governed tasks/week | < 10 | 10-30 | > 30 |
| 2 | Reliability | Critical-path success rate | < 85% | 85-95% | > 95% |
| 3 | Recovery discipline | Mean time to recover core service incidents | > 4h | 1-4h | < 1h |
| 4 | Memory durability | % substantive changes logged to gitMaat within 24h | < 50% | 50-85% | > 85% |
| 5 | Contract coverage | % high-impact flows with explicit schemas/contracts | < 40% | 40-75% | > 75% |
| 6 | Governance enforcement | % protected actions passing decision gates | < 60% | 60-90% | > 90% |
| 7 | Human override quality | % escalations resolved with documented rationale | < 60% | 60-90% | > 90% |
| 8 | Cross-node federation | # nodes interoperating via shared protocols this week | 0-1 | 2-3 | >= 4 |
| 9 | Economic efficiency | Cost per successful governed workflow (4-week trend) | rising > 10% | flat (+/-10%) | falling > 10% |
| 10 | Reuse vs reinvention | % new workflows built from existing components | < 40% | 40-70% | > 70% |
| 11 | Security posture | Count of unresolved high-risk findings > 7 days | > 5 | 1-5 | 0 |
| 12 | Learning velocity | # validated learnings converted to standards/playbooks | 0-1 | 2-4 | >= 5 |
| 13 | External legitimacy | # external stakeholders using outputs repeatedly | 0 | 1-2 | >= 3 |
| 14 | Institutional autonomy | % core operations executable without dominant external platforms | < 20% | 20-50% | > 50% |
| 15 | Labor transformation | % work shifted from ad hoc manual to reproducible pipelines | < 30% | 30-65% | > 65% |
| 16 | Mission alignment | % weekly outputs mapped to declared strategic priorities | < 60% | 60-85% | > 85% |

## Interpretation rules

- **Red flag:** any indicator at `0` for 3 consecutive weeks.
- **False progress check:** total score rises but Indicators 2, 4, or 6 do not improve.
- **Readiness signal:** 4-week average >= 24 with no red flags in 2, 4, 6, 11.
- **Transition signal:** 8-week trend shows sustained gains in 5, 8, 12, 14 together.

## Weekly review template

```text
Week of:
Total score:
Stage:

Top gains (why):
1)
2)

Top constraints (root cause):
1)
2)

Decisions for next week:
1)
2)
3)

Evidence links:
- 
- 
- 
```

## Minimal dashboard fields

- Week
- Indicator # and score
- Evidence URL/path
- Owner
- Next action

This scorecard should be treated as a decision instrument, not a reporting ritual.
