# MAAT Gateway Registry

> **"Adding a gateway is a data change, not a code change."**
> One of the replaceable-lane invariants from [`MAAT-EVOLUTION-LANES.md`](MAAT-EVOLUTION-LANES.md).

**Canon vs domain packs:** Governance stays in-repo; subject-matter corpora (e.g. Florida law) should live **outside** the canonical tree long-term — see [`MAAT-CANON-VS-DOMAIN-KNOWLEDGE.md`](MAAT-CANON-VS-DOMAIN-KNOWLEDGE.md).

---

## What is a gateway?

A **gateway** is a named expert surface that:

- Speaks the `maat.archivist_record.v1` contract
 ([`maat-ecosystem/skeleton/schemas/archivist_record.schema.json`](../maat-ecosystem/skeleton/schemas/archivist_record.schema.json))
- Has a KA2-aware default research type and level of analysis
- Uses a base model (evolvable via the LoRA pipeline in
  [`forge/lora_pipeline.py`](../gemma4-toolshim/swarm/forge/lora_pipeline.py))
- Optionally binds to one or more **retrieval packs**
- Is exposed to users via an OpenClaw preset
- Is discovered by other agents through Ka Discovery (`:8010/manifest`)

The registry file is the single source of truth. It lives at:

```
maat-ecosystem/skeleton/gateways/registry.yaml
```

and is consumed by [`gemma4-toolshim/swarm/gateway_registry.py`](../gemma4-toolshim/swarm/gateway_registry.py).

---

## Three layers, one gateway

| Layer | Responsibility | File(s) |
|-------|----------------|---------|
| **Registry** | Canonical declaration: id, default expert, packs, tools, schema | `maat-ecosystem/skeleton/gateways/registry.yaml` |
| **OpenClaw preset** | User-facing surface: model fallbacks, tools profile, heartbeat | `openclaw/presets/<id>/openclaw.agents.<id>.json5` |
| **Ka Discovery organ** | Network identity + liveness for cross-machine agents | `GET http://<host>:8010/manifest` |

**Merge rule, in priority order:**

1. `registry.yaml` — authoritative for: `id`, `default_expert`, `archivist_schema`,
   `retrieval_packs`, `research_type_default`, `level_of_analysis_default`, `tools` (declared intent).
2. OpenClaw preset — authoritative for: `model.primary`, `model.fallbacks`,
   `tools.profile`, `heartbeat`, `subagents`, `workspace`.
3. Ka Discovery manifest — authoritative for: endpoint, host, liveness.

If these disagree, the registry wins for contract, OpenClaw wins for runtime,
Ka Discovery wins for address. **No other component may resolve the disagreement** —
see [`MAAT-EVOLUTION-LANES.md`](MAAT-EVOLUTION-LANES.md) (Sacred Lane 0).

---

## Adding a gateway

### 1. Declare it (registry)

Append a block to `maat-ecosystem/skeleton/gateways/registry.yaml`:

```yaml
- id: my-new-gateway
  description: One-line purpose.
  default_expert: scout          # must match gemma4-toolshim/swarm/expert_config.py EXPERTS[*].name
  archivist_schema: maat.archivist_record.v1
  research_type_default: applied
  level_of_analysis_default: institution
  model: ollama/gemma4:e4b
  retrieval_packs:
    - my-pack
  tools:
    - read_file
    - grep
    - query_gitmaat
  preset_file: openclaw/presets/my-new-gateway/openclaw.agents.my-new-gateway.json5
  ka_discovery_organ: knowledge
```

### 2. (Optional) Build the retrieval pack

A pack is a directory under `data/retrieval_packs/<pack-id>/` with:

- `manifest.json` — pack id, version, sources, license, checksum
- `documents/` — the source material (read-only for agents)
- `embeddings/` — (optional) pre-built vector index

Packs are proposed and promoted through
[`forge/retrieval_proposals.py`](../gemma4-toolshim/swarm/forge/retrieval_proposals.py),
never hand-edited into a live gateway.

### 3. Register the OpenClaw preset

Drop a JSON5 fragment at the path named in `preset_file`, following the pattern in
[`openclaw/presets/ka2-research/README.md`](../openclaw/presets/ka2-research/README.md).
Then append the fragment to `agents.list` in your host's `~/.openclaw/openclaw.json`
and restart the gateway.

### 4. Verify

```bash
cd gemma4-toolshim/swarm
python3 gateway_registry.py         # lists ids, reports missing presets/packs
python3 -m unittest tests/test_gateway_registry.py
```

If the registry probe reports `missing packs:` for a gateway you just added,
either create the pack or remove the reference — do not silence the check.

---

## What the registry is **not**

- **Not a router.** Routing tags (`research_grade`, `level_of_analysis`,
  `research_type`) are computed by
  [`ka2_router.py`](../gemma4-toolshim/swarm/ka2_router.py) at request time.
  The registry supplies defaults, not decisions.
- **Not a model registry.** Base model ids start here; LoRA winners flow
  through [`forge/lora_pipeline.py`](../gemma4-toolshim/swarm/forge/lora_pipeline.py)
  and are applied to `expert_config.py` via a Guard-mediated patch.
- **Not a policy file.** Tool intent is declared here so presets and
  Tehuti Guard can cross-check. **Tehuti Guard** is the enforcer; the
  registry is the manifest.
- **Not runtime state.** Liveness lives on Ka Discovery. The registry
  describes what *should* exist; `/manifest` reports what *is* up.

---

## Why this exists

Before the registry, adding a gateway required edits to:

- `expert_config.py` (new expert + keywords)
- `ka2_router.py` (new signals)
- OpenClaw host JSON (new preset)
- Some markdown somewhere explaining the binding

…and the retrieval pack was usually just bolted onto an existing expert,
polluting its routing keywords. That is exactly the failure mode Lane 0
of the evolution lanes forbids: core contracts and method mutate to
accommodate a single use case.

With the registry, the path is:

```
registry.yaml  +  optional retrieval pack  +  optional preset fragment
=  new gateway, shipped.
```

No router edit. No expert-keyword edit. No code change.
