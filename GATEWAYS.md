# MAAT Gateways — What They Are (Plain Language)

**One sentence:** a gateway is a named expert you can talk to over HTTP, with
governance, memory, and scoring built in.

If you are a human, skim the five bullets below and you are done.
If you are an agent new to this workspace, read this file top to bottom.

---

## Five-bullet version

- There is an HTTP server at `http://127.0.0.1:8040`. It has one useful
  endpoint: `POST /ask` with a JSON body `{"message": "..."}`. It replies
  with `{"reply": "...", ...}`.
- Behind that server is the **gateway registry** — a list of named experts
  declared in `maat-ecosystem/skeleton/gateways/registry.yaml`. Today:
  `scout`, `analyst`, `archivist`, `ka2-research`, `fl-trust-law`.
- Each gateway may bind a **retrieval pack** (a corpus it is an expert on).
  Adding an expert is a YAML edit, not a code change.
- Every turn you run through the server produces a **structured record** in
  `logs/archivist/records.jsonl` *and* in gitMaat (if Postgres is up) *and*
  passes through a **scorecard + guard validator**. You don't have to do any
  of that; the server does.
- **Telegram, Discord, n8n, cron, curl** — they all hit the same endpoint.
  No channel-specific code. See
  [`docs/USING-GATEWAYS-FROM-ANY-CHANNEL.md`](docs/USING-GATEWAYS-FROM-ANY-CHANNEL.md).

## What the system is doing while you are doing nothing

- **Routing** — `gemma4-toolshim/swarm/ka2_router.py` reads your message,
  tags it with `research_grade`, `level_of_analysis`, `research_type`, picks
  the expert.
- **Dispatching** — the server calls Ollama at `:11434` with the right model.
- **Archiving** — every reply is wrapped in a `maat.archivist_record.v1`
  envelope and written to disk + Postgres.
- **Validating** — `guard_validator.py` recomputes the scorecard, detects
  RBL flags, forbidden vocabulary, and decides `allow` / `review` / `deny`.
- **Watching** — `sentinel_stream.py` follows the JSONL stream and notices
  patterns across turns (stalls, streaks of failure, RBL waves).
- **Learning** — `forge/` proposes changes (retrieval pack, router keywords,
  LoRA fine-tune) that have to pass Maatbench and Tehuti Guard before they
  can take effect.

Nothing in that list requires you to run a CLI command. You talk to the
gateway; it does its own hygiene.

## The two Sentinels (important disambiguation)

There are two things called "Sentinel" in this lab. They don't conflict;
they operate at different layers.

| Name | Watches | Lives in |
|------|---------|----------|
| **MAAT Sentinel** (the older one) | **Machines / runtimes** — doctor snapshots, presence heartbeats, immune events; unified live view per host | `maat-sentinel/`, HTTP on **:4242** |
| **Sentinel Stream** (new, added with the evolving gateways) | **Sessions / turns** — per-session state from archivist records, stalls, scorecard streaks, RBL streaks | `gemma4-toolshim/swarm/sentinel_stream.py` |

Rule of thumb:

- If the question is *"is that host alive and healthy?"* → **maat-sentinel** on 4242.
- If the question is *"is that conversation going off the rails?"* → **sentinel_stream** (library, consumed by Bench and Forge, not its own daemon yet).

Both feed the immune system; they just see different sensors. See
[`docs/MAAT-IMMUNE-SYSTEM.md`](docs/MAAT-IMMUNE-SYSTEM.md) for the organ
map.

## "Easy for any agent to overstand" checklist

If you are onboarding as a new agent and want to be useful in thirty seconds:

1. Read `GET http://127.0.0.1:8040/info`.
2. Read `GET http://127.0.0.1:8040/gateways` to see what experts are live.
3. To answer any user question, POST to `/ask`. Don't try to be clever.
4. If you must add a new expert or a new corpus, stop. Read
   [`docs/MAAT-GATEWAY-REGISTRY.md`](docs/MAAT-GATEWAY-REGISTRY.md) —
   it is a five-minute read and it will save you from wrong assumptions.
5. If you want to know what can and cannot evolve, read
   [`docs/MAAT-EVOLUTION-LANES.md`](docs/MAAT-EVOLUTION-LANES.md).

That's the whole orientation.

## If something is wrong

| Symptom | Probably the cause |
|---------|--------------------|
| `curl :8040/health` refused | Server not running. `bash scripts/start-gateway-server.sh` or `systemctl start maat-gateway-server` |
| Reply is empty, `model_error` is set | Ollama is down. Check `curl :11434/api/tags`. |
| `persist.gitmaat_status` starts with `not_connected` | Postgres / `PGVECTOR_DB_URL` not reachable. JSONL is still being written; gitMaat will catch up when DB is back. |
| Decision is always `review` | Scorecard failing. Usually means the reply is too short or the server's heuristic scorecard is penalising unfairly. Fine-tuned experts emit their own. |
| New gateway not showing up | You added `registry.yaml` but did not restart the server. It loads once on boot. |

## What this replaces

Before: to test anything through Telegram you had to go to a laptop, open a
terminal, run a Python script, read JSON. Now: you send a Telegram message.
The server does the rest.

Before: to add a new expert you had to edit routing code. Now: you add a
line to a YAML file.

Before: there was no way to know whether a Telegram reply was "research
grade" or scored or governed. Now: every reply has a `correlation_id` you
can query gitMaat for and get the full structured record back.
