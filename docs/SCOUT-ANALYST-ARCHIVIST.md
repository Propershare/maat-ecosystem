# Scout, Analyst, Archivist — operating principle and Archivist contract

This doc is the production-facing companion to the triad in [`AGENTS.md`](../AGENTS.md).

## Operating line

**Scout finds.** **Analyst decides.** **Archivist remembers.**

Scout output should be easy to filter and trace (pointers, quotes with file:line or URL). Analyst output should be explicit about decisions, confidence, and open risks. Archivist output should be **append-friendly** and **schema-stable** so Maat Memory, events, and future fine-tunes do not depend on parsing chat tone.

## Archivist: structured-first

When an agent is acting as Archivist (or when persisting anything that must be retrieved later), default to **valid JSON** matching the shape below unless a stricter project schema supersedes it. Prose is allowed only inside `summary` (compact) or `notes` (optional). No markdown tables in the JSON payload itself.

### Recommended record shape (v1)

```json
{
  "schema": "maat.archivist_record.v1",
  "record_id": "uuid-or-monotonic-id",
  "created_at": "2026-04-08T12:00:00Z",
  "tags": ["domain:tehuti-lab", "topic:swarm", "confidence:high"],
  "summary": "One to three sentences, factual, no hedge soup.",
  "sources": [
    { "kind": "file", "ref": "/path/or/repo-relative/path", "line_start": 0, "line_end": 0 },
    { "kind": "url", "ref": "https://example.com/page" },
    { "kind": "gitmaat", "ref": "task_id_or_session_id_if_any" }
  ],
  "related_events": ["task.created", "memory.write"],
  "payload": {}
}
```

- **`tags`:** lowercase, `namespace:value` or agreed enums; keep a small shared vocabulary in the team.
- **`sources`:** every non-obvious claim should have at least one entry when possible.
- **`payload`:** optional structured extra (tool results snippets, hashes, links to full blobs elsewhere).

Align eventually with [`maat-ecosystem/skeleton/schemas/`](../maat-ecosystem/skeleton/schemas/) (e.g. task, memory, event) so records can be losslessly mapped into gitMaat rows and canonical events.

## Swarm routing (Ollama / shim)

Default expert definitions live in [`gemma4-toolshim/swarm/expert_config.py`](../gemma4-toolshim/swarm/expert_config.py): `scout`, `analyst`, `archivist` plus existing specialists. Routing is keyword-based today; a Python orchestrator can replace `route_message()` with a small planner that runs **Scout → Analyst → Archivist** in order for ingest workflows.

## Why this matters for Maat

The spine (MaatLangChain + gitMaat) needs **events and memory** that do not require an LLM to re-read chat logs. Structured Archivist output is the bridge between “the model said something” and “the system can replay and bench it.”

**Last updated:** 2026-04-08
