# MAAT Studio — UI Specification

> A teenager should be able to open this, plug in a model, and run an agent in under 2 minutes.

## Architecture: Ka Body Dashboard

MAAT Studio is the **voice organ** — the visual interface for a Ka Architecture body. It reads the discovery endpoint (`http://<host>:8010/manifest`) and renders the body's health, memory, evolution, and configuration in real-time.

**Data Source:** All data comes from the Ka Discovery API and organ MCP endpoints. The UI is a pure frontend — it reads the body, it doesn't contain the body.

---

## Design Philosophy

- **Zero clutter.** If it's not needed right now, hide it.
- **One screen, one job.** Never make the user guess where they are.
- **Config over code.** Everything is toggles, dropdowns, and text fields. No terminal required.
- **Progressive disclosure.** Simple by default, powerful when you dig in.
- **Ka-native.** Every view maps to an organ. The UI IS the body's face.

---

## Theme: Kemet

| Token | Value | Use |
|-------|-------|-----|
| `--maat-black` | `#0D0D0D` | Background, primary surfaces |
| `--maat-red` | `#C41E3A` | Alerts, active states, primary accent |
| `--maat-green` | `#2D8B46` | Success, online, healthy |
| `--maat-gold` | `#D4A843` | Highlights, badges, Maat Score |
| `--maat-white` | `#F5F0E8` | Text, papyrus tone (not pure white) |
| `--maat-gray` | `#1A1A1A` | Cards, panels, secondary surfaces |
| `--maat-dim` | `#666666` | Muted text, borders |
| `--maat-blue` | `#4A90D9` | Links, info states |
| `--maat-purple` | `#8B5CF6` | Evolution, learning indicators |

**Typography:** Inter or system sans-serif. Clean, no serifs.
**Corners:** Slightly rounded (6px). Not bubbly.
**Spacing:** Generous. Let it breathe.
**Icons:** Minimal line icons or organ emojis (🔮🧠💾🤲👁🗣🛡🦴🩸).
**Dark mode only.** The Kemet aesthetic is dark backgrounds with gold/papyrus accents.

---

## Layout: Three Zones

```
┌──────────────────────────────────────────────────┐
│  TOP BAR (thin)                                  │
│  [☰]  MAAT Studio    [host: staydangerous ▼]  ⚙ │
├────────┬─────────────────────────────────────────┤
│        │                                         │
│  SIDE  │           MAIN CANVAS                   │
│  NAV   │                                         │
│        │  (changes based on active section)       │
│  🏠    │                                         │
│  🛡    │                                         │
│  💾    │                                         │
│  🧠    │                                         │
│  🤲    │                                         │
│  📊    │                                         │
│  ⚙     │                                         │
│        │                                         │
├────────┴─────────────────────────────────────────┤
│  STATUS BAR: Health: 7/7 | Memory: 391 entries   │
│  Model: ollama/gemma | Maat Score: 6.4/10        │
└──────────────────────────────────────────────────┘
```

---

## Screens

### 1. Dashboard (🏠 Home)

The body at a glance. Everything the operator needs in one view.

```
┌─────────────────────────────────────────────────┐
│                                                 │
│  ┌─ BODY STATUS ──────────────────────────────┐ │
│  │  🔮 Soul    ✅    🧠 Brain   ✅  :8014    │ │
│  │  💾 Memory  ✅    🤲 Hands   ✅  :8016    │ │
│  │  👁 Senses  ✅    🗣 Voice   ⏳  planned  │ │
│  │  🛡 Ka      ✅    🦴 Skeleton ✅  :8017   │ │
│  │  🩸 Blood   ✅                             │ │
│  │                          Health: 7/7 ✅     │ │
│  └────────────────────────────────────────────┘ │
│                                                 │
│  ┌─ MEMORY METER ─┐  ┌─ MAAT SCORE ──────────┐ │
│  │  ████████░░ 80% │  │  ┌──────────────────┐ │ │
│  │  391 entries    │  │  │    6.4 / 10       │ │ │
│  │  595 MB         │  │  │    ████████░░     │ │ │
│  │  6.8ms latency  │  │  └──────────────────┘ │ │
│  │  78h stale ⚠️   │  │  Truth:  7  Justice: 6│ │
│  └─────────────────┘  │  Balance:5  Order:  8 │ │
│                       │  Reciprocity: 6       │ │
│  ┌─ EVOLUTION ────┐   └──────────────────────┘ │
│  │  Loop: active  │                            │
│  │  Last: 6h ago  │   ┌─ RECENT ACTIVITY ───┐  │
│  │  Learnings: 44 │   │  • Task logged 3h    │  │
│  │  Confidence:0.7│   │  • Decision 12h      │  │
│  │  Next: 2h      │   │  • Learning 18h      │  │
│  └────────────────┘   └──────────────────────┘  │
│                                                 │
└─────────────────────────────────────────────────┘
```

**Data sources:**
- Body status → `GET /health` from Ka Discovery (:8010)
- Memory meter → `memory_stats` tool from Maat Memory (:8022)
- Maat Score → calculated from audit data
- Evolution → read `ka/evolve.yaml` + last cycle timestamp
- Recent activity → `memory_get_recent_changes` from Maat Memory

---

### 2. Ka Health (🛡)

The immune system dashboard. Every organ's vital signs.

```
┌─────────────────────────────────────────────────┐
│  🛡 KA — ORGAN HEALTH                          │
│                                                 │
│  Organ       Port  Status  Latency  Uptime      │
│  ──────────────────────────────────────────────  │
│  brain       8014  ✅      12ms     99.9%       │
│  memory      8022  ✅      6ms      99.8%       │
│  hands       8016  ✅      8ms      99.9%       │
│  senses      8015  ✅      15ms     99.7%       │
│  ka          8010  ✅      2ms      100%        │
│  skeleton    8017  ✅      4ms      99.9%       │
│  blood       8020  ✅      22ms     99.5%       │
│                                                 │
│  ┌─ PAIN LOG (last 24h) ─────────────────────┐  │
│  │  No pain events recorded.                 │  │
│  └───────────────────────────────────────────┘  │
│                                                 │
│  ┌─ HEALING RULES ───────────────────────────┐  │
│  │  brain.model.unreachable → fallback (3x)  │  │
│  │  hands.mcp.disconnected → reconnect (5x)  │  │
│  │  memory.storage.timeout → sqlite (2x)     │  │
│  └───────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

**Data sources:**
- Organ health → `GET /health` from Ka Discovery
- Pain log → `memory_get_tasks` filtered for errors
- Healing rules → read `ka/pulse.yaml`

---

### 3. Memory (💾)

The memory organ — browse, search, and manage all memory types.

**Sub-tabs:** Banks | Episodic | Semantic | Patterns | Tasks | Learnings

```
┌─────────────────────────────────────────────────┐
│  💾 MEMORY — Banks                              │
│                                                 │
│  ┌─ PRIMARY (postgres) ──────────────────────┐  │
│  │  ████████████████░░░░ 62%                 │  │
│  │  Rows: 391  |  Size: 595MB  |  6.8ms     │  │
│  │                                           │  │
│  │  conversations: 114   tasks: 117          │  │
│  │  decisions: 0         learnings: 44       │  │
│  │  sessions: 116        errors: 0           │  │
│  └───────────────────────────────────────────┘  │
│                                                 │
│  ┌─ ARCHIVE (sqlite) ───────────────────────┐   │
│  │  Empty — no archived data yet            │   │
│  └──────────────────────────────────────────┘   │
│                                                 │
│  ┌─ LIFECYCLE ──────────────────────────────┐   │
│  │  hot (0-7d) → warm (7-90d) → cold (90d+)│   │
│  │  Auto-archive: ON  |  Restore on access  │   │
│  └──────────────────────────────────────────┘   │
│                                                 │
│  [Search memory...]                    [🔍]     │
└─────────────────────────────────────────────────┘
```

**Data sources:**
- Bank stats → `memory_stats` and `memory_health` from Maat Memory (:8022)
- Search → `memory_search` tool
- Tasks/Learnings → `memory_get_tasks`, `memory_get_learnings`

---

### 4. Brain (🧠)

Model configuration, reasoning chains, learning history.

```
┌─────────────────────────────────────────────────┐
│  🧠 BRAIN — Models & Learning                  │
│                                                 │
│  Active Model: [ollama/gemma ▼]                 │
│  Fallback:     [openai/gpt-4o ▼]               │
│  Endpoint:     http://staydangerous:8014        │
│                                                 │
│  ┌─ LEARNINGS (44 total) ────────────────────┐  │
│  │  Confidence distribution:                 │  │
│  │  ▓▓▓▓▓▓░░░░  avg: 0.72                  │  │
│  │                                           │  │
│  │  Recent:                                  │  │
│  │  • "Git mv preserves history" (0.9)       │  │
│  │  • "Use trash over rm" (0.85)             │  │
│  │  • "GGUF Q4_K_M good balance" (0.8)       │  │
│  └───────────────────────────────────────────┘  │
│                                                 │
│  ┌─ DECISIONS (recent) ─────────────────────┐   │
│  │  No recent decisions logged.             │   │
│  └──────────────────────────────────────────┘   │
└─────────────────────────────────────────────────┘
```

---

### 5. Hands (🤲)

Apps, tools, skills, and MCP connections.

```
┌─────────────────────────────────────────────────┐
│  🤲 HANDS — Apps & Tools                        │
│                                                 │
│  ┌─ APPS ────────────────────────────────────┐  │
│  │  🤲 Receptionist  middle-ring  4 workflows│  │
│  │  🤲 Researcher    middle-ring  3 workflows│  │
│  │  🤲 Operator      outer-ring   2 workflows│  │
│  │  🤲 Teacher       middle-ring  2 workflows│  │
│  └───────────────────────────────────────────┘  │
│                                                 │
│  ┌─ MCP CONNECTIONS ─────────────────────────┐  │
│  │  Filesystem  :8016  ✅                    │  │
│  │  ComfyUI     :8019  ✅                    │  │
│  │  Tehuti Core :8014  ✅                    │  │
│  └───────────────────────────────────────────┘  │
│                                                 │
│  ┌─ PACKS ───────────────────────────────────┐  │
│  │  policy: maat-default, strict-safety      │  │
│  │  tool:   filesystem                       │  │
│  │  agent:  tehuti                           │  │
│  │  learn:  self-improve                     │  │
│  └───────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

---

### 6. Evolution (📊)

The learning loop — watch the body get smarter.

```
┌─────────────────────────────────────────────────┐
│  📊 EVOLUTION LOOP                              │
│                                                 │
│  SENSE → STORE → PATTERN → PROMOTE → APPLY →   │
│  MEASURE → DECAY                                │
│   ✅      ✅      ⏳        ─        ─          │
│                                                 │
│  Cycle: every 6h  |  Last: 6h ago  |  Next: 2h │
│  Min threshold: 10 entries                      │
│                                                 │
│  ┌─ PROMOTED LEARNINGS ─────────────────────┐   │
│  │  44 learnings  |  avg confidence: 0.72   │   │
│  │  12 above 0.8 threshold (promotable)     │   │
│  │  3 below 0.2 (candidates for archive)    │   │
│  └──────────────────────────────────────────┘   │
│                                                 │
│  ┌─ DECAY STATUS ───────────────────────────┐   │
│  │  Rate: 5%/cycle  |  Floor: 0.1           │   │
│  │  Strengthen: +10% on successful use      │   │
│  │  Archive threshold: 0.2                  │   │
│  └──────────────────────────────────────────┘   │
│                                                 │
│  [Run Evolution Now]                            │
└─────────────────────────────────────────────────┘
```

---

### 7. Settings (⚙)

Body configuration — discovery, auth, connections.

```
┌─────────────────────────────────────────────────┐
│  ⚙ SETTINGS                                    │
│                                                 │
│  Body Name:     [maat-ecosystem          ]      │
│  Discovery URL: [http://192.168.4.21:8010]      │
│  API Key:       [••••••••••••••••••] [👁]       │
│                                                 │
│  ┌─ ORGAN ENDPOINTS ────────────────────────┐   │
│  │  Brain:    [http://192.168.4.21:8014]    │   │
│  │  Memory:   [http://192.168.4.21:8022]    │   │
│  │  Hands:    [http://192.168.4.21:8016]    │   │
│  │  Blood(n8n): [http://192.168.4.21:8015]  │   │
│  │  Skeleton: [http://192.168.4.21:8017]    │   │
│  │  Blood(RAG): [http://192.168.4.21:8020]   │   │
│  │  Senses:   (via gateways / discovery — no fixed MCP in reference map) │
│  └──────────────────────────────────────────┘   │
│                                                 │
│  ┌─ MEMORY BANKS ───────────────────────────┐   │
│  │  Primary adapter: [postgres ▼]           │   │
│  │  Archive adapter: [sqlite ▼]             │   │
│  │  Auto-archive:    [ON/OFF toggle]        │   │
│  │  Warn at:         [80]% capacity         │   │
│  └──────────────────────────────────────────┘   │
│                                                 │
│  ┌─ EVOLUTION LOOP ─────────────────────────┐   │
│  │  Enabled:         [ON/OFF toggle]        │   │
│  │  Cycle interval:  [6h ▼]                │   │
│  │  Auto-promote:    [ON/OFF toggle]        │   │
│  │  Decay rate:      [5]%                   │   │
│  └──────────────────────────────────────────┘   │
│                                                 │
│  [Save]  [Reset to Defaults]                    │
└─────────────────────────────────────────────────┘
```

---

## API Endpoints (Backend Data)

The UI reads ALL data from these HTTP endpoints. No database access needed.

| Endpoint | Purpose | Returns |
|----------|---------|---------|
| `GET :8010/manifest` | Full body map | JSON with all organs, endpoints, boot sequence |
| `GET :8010/health` | Organ health | Status, latency for each organ |
| `GET :8010/connect` | Connection info | Instructions for new agents |
| `POST :8022/memory_stats` | Memory stats | Counts, capacity, confidence |
| `POST :8022/memory_health` | Memory health | Connection, latency |
| `POST :8022/memory_search` | Search memory | Results by query |
| `POST :8022/memory_get_tasks` | Tasks | Task list with status |
| `POST :8022/memory_get_learnings` | Learnings | Learning list with confidence |
| `POST :8022/memory_get_decisions` | Decisions | Decision log |
| `POST :8022/memory_get_recent_changes` | Changes | File change log |
| `POST :8022/memory_get_sessions` | Sessions | Session history |

**Auth:** All :8022 and other organ endpoints require `Authorization: Bearer <KA_API_KEY>`.
Discovery (:8010) is open.

---

## Implementation Notes

- **Framework:** React, Next.js, or plain HTML+JS — whatever Replit generates best
- **State:** Poll `:8010/health` every 30s for live organ status
- **Responsive:** Must work on mobile (sidebar collapses to hamburger)
- **No backend needed:** The UI is a pure frontend that reads existing Ka Architecture APIs
- **Deployment:** Static files served by any web server, or as a Replit app
