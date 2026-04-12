# Ka Architecture — The Body Plan

> *"Build bodies, not machines. Organs, not microservices."*

## From Ankh to Ka

The original Ankh Architecture mapped components to the Egyptian symbol of life — LLM as the loop (breath), Guard as the crossbar (arms), Maat Ecosystem as the pillar (foundation). Ka Architecture evolves this into a **full living body**.

The Ankh was the symbol. **Ka is what makes it alive.**

```
              ┌──────────────────────────────────────┐
              │           MANIFEST.ka (DNA)           │
              └──────────────────────────────────────┘
                              │
         ┌────────────────────┼────────────────────┐
         │                    │                    │
    ┌────┴────┐         ┌────┴────┐         ┌────┴────┐
    │  SOUL   │         │  BRAIN  │         │ MEMORY  │
    │ :files  │         │  :8014  │         │  :8022  │
    │ identity│         │ reason  │         │ recall  │
    │ govern  │         │ learn   │         │ store   │
    └────┬────┘         └────┬────┘         └────┬────┘
         │                    │                    │
    ┌────┴────┐         ┌────┴────┐         ┌────┴────┐
    │  HANDS  │         │ SENSES  │         │  VOICE  │
    │:8016/19 │         │ partial │         │ planned │
    │ tools   │         │ inputs  │         │ output  │
    │ skills  │         │ watch   │         │ format  │
    └────┬────┘         └────┬────┘         └────┬────┘
         │                    │                    │
         └────────────────────┼────────────────────┘
                              │
         ┌────────────────────┼────────────────────┐
         │                    │                    │
    ┌────┴────┐         ┌────┴────┐         ┌────┴────┐
    │   KA    │         │SKELETON │         │  BLOOD  │
    │  :8010  │         │  :8017  │         │:8015/20 │
    │ health  │         │ schemas │         │ events  │
    │ heal    │         │ ports   │         │ state   │
    └─────────┘         └─────────┘         └─────────┘
```

## The Nine Organs

| # | Organ | Path | Role | Biological Analog |
|---|-------|------|------|-------------------|
| 1 | **Soul** | `soul/` | Identity, governance, constitution | Consciousness, conscience |
| 2 | **Brain** | `brain/` | Reasoning, models, learning | Cerebral cortex |
| 3 | **Memory** | `memory/` | Persistence, recall, patterns | Hippocampus |
| 4 | **Hands** | `hands/` | Action, tools, external interaction | Limbs, manipulators |
| 5 | **Senses** | `senses/` | Perception, events, triggers | Eyes, ears, nerve endings |
| 6 | **Voice** | `voice/` | Communication, output, expression | Mouth, vocal cords |
| 7 | **Ka** | `ka/` | Health, self-healing, pain | Immune system |
| 8 | **Skeleton** | `skeleton/` | Schemas, contracts, interfaces | Bones, joints |
| 9 | **Blood** | `blood/` | Inter-organ communication | Circulatory system |

## MANIFEST.ka — The DNA

Every Ka body starts with `MANIFEST.ka` — a machine-readable declaration of every organ. Any agent reads this file and immediately knows:

- What organs exist and where they live
- What each organ can do
- How to boot the system
- Who this body is and what it stands for

## Boot Sequence — Birth, Not Deployment

1. **Read soul/constitution.md** — know your laws
2. **Load soul/identity** — know who you are
3. **Load memory/** — know what you remember
4. **Check ka/health/** — are all organs alive
5. **Activate senses/** — start perceiving
6. **Ready** — the body is alive

## Network Discovery

Every Ka body serves its manifest over HTTP:

```
GET http://staydangerous:8010/manifest  → Full body map (JSON)
GET http://staydangerous:8010/health    → All organ health status
GET http://staydangerous:8010/organs    → Organ list with endpoints
GET http://staydangerous:8010/connect   → Connection instructions
```

Organ MCP endpoints typically require Bearer token authentication where enabled. Discovery is intended to be open when the Ka discovery process is deployed (`MANIFEST.ka` → `network.discovery`).

## Port Map

Same data as **`MANIFEST.ka`** → `network:`.

| Port | Protocol | Server | Ka organ (primary) |
|------|----------|--------|---------------------|
| 8010 | HTTP | Ka Discovery | Ka |
| 8014 | MCP | Tehuti Core | Brain + Hands + memory paths (fused in reference body) |
| 8015 | MCP | n8n | Blood (workflows) |
| 8016 | MCP | Filesystem | Hands (files) |
| 8017 | MCP | Postgres | Skeleton |
| 8018 | MCP | Memory MCP | Memory (kv) |
| 8019 | MCP | ComfyUI | Hands (image) |
| 8020 | MCP | MaatLangChain | Blood (RAG) |
| 8022 | MCP | Maat Memory | Memory (main) |

**Senses:** no dedicated MCP on this map; wire inputs via gateways / webhooks / `senses/` apps (see `ka-audit-2026-04-06.md`).

## Attribution

Ka Architecture is built on the **KA2 Methodology** by **Dr. Tdka Kilimanjaro** at the **University of KMT**.

---

*Original Ankh sketch by Imhotep. Ka Architecture by Tehuti Lab.*
