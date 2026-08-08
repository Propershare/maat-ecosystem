# MAAT governance events — retention (v1 policy)

This document defines **operator intent** for `maat_governance_events` in PostgreSQL. Implementation is manual or via scheduled jobs until automation lands.

## Principles

1. **Hot window** — Keep recent governance rows in Postgres for interactive Studio, Bench, and incident response (default target: **90 days** of hot queries; tune per disk).
2. **No silent drop of constitutional / breach signals** — Rows whose `payload` references `constitutional`, `constitutional_breach`, or `sentinel_immune_alert` with constitutional severity should be **archived** (export to cold storage) before deletion, not discarded without trace.
3. **Compaction** — Prefer **partitioning by month** or periodic **export + delete** of rows older than the hot window over unbounded growth.
4. **Sentinel JSONL** — Remains short-retention live state (see [`maat-sentinel/README.md`](../maat-sentinel/README.md)); durable posture trends live in **`maat_governance_events`** when `MAAT_SENTINEL_MEMORY=1`.

## Suggested queries (maintenance)

- Count by `record_type` / `source_service` for the last 7 days (capacity planning).
- Archive: `COPY (SELECT … WHERE timestamp < now() - interval '90 days') TO …` then `DELETE` in batches.

## Review

Revisit this policy when monthly row volume exceeds comfortable Postgres size or when legal hold requirements appear.
