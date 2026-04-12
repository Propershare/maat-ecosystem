# MAAT Studio — UI Specification

Full web application. Dashboard for managing an AI ecosystem with 9 services (called organs), swappable memory backends, an evolution loop that makes the system smarter over time, installable apps, and modular packs.

---

## Theme

Dark mode only.

| Token | Hex | Usage |
|-------|-----|-------|
| `--bg` | `#0D0D0D` | Page background |
| `--bg-card` | `#1A1A1A` | Cards, panels |
| `--bg-elevated` | `#222230` | Hover, active, inputs |
| `--gold` | `#D4A843` | Primary accent, active nav, buttons |
| `--gold-dim` | `#8A7235` | Muted borders, icons |
| `--green` | `#2D8B46` | Healthy, online, success |
| `--red` | `#C41E3A` | Error, offline, critical |
| `--yellow` | `#E6A817` | Warning, degraded |
| `--blue` | `#4A90D9` | Links, info |
| `--purple` | `#8B5CF6` | Learning, evolution, confidence |
| `--text` | `#F5F0E8` | Primary text (warm, not pure white) |
| `--text-dim` | `#666666` | Secondary text, timestamps |
| `--border` | `#2A2A3A` | Card borders, dividers |

Font: Inter / system sans-serif. Monospace for ports, numbers, code: Courier New.
Corners: 8px cards, 6px buttons. Dark backgrounds, gold accents.

---

## Layout

```
┌──────────────────────────────────────────────────────┐
│  TOP BAR                                             │
│  [☰] 𓂀 MAAT Studio    ● Connected    [body ▼]  [⚙] │
├─────────┬────────────────────────────────────────────┤
│ SIDEBAR │            MAIN CANVAS                     │
│  64px   │                                            │
│  🏠     │  (scrollable content area)                 │
│  🛡     │                                            │
│  💾     │                                            │
│  🧠     │                                            │
│  🤲     │                                            │
│  📊     │                                            │
│  ⚙      │                                            │
├─────────┴────────────────────────────────────────────┤
│  STATUS BAR: Health: 7/7 │ Memory: 391 │ Score: 6.4 │
└──────────────────────────────────────────────────────┘
```

- Sidebar: icon-only, expands to show labels on hover
- Active page: gold icon + gold left border
- Status bar: updates every 30s from API polling
- Connection indicator in top bar: green/yellow/red dot

---

## Screen 1: Dashboard 🏠

Shows everything at a glance.

**Service Grid** — 9 cards in a grid:
| Service | Port | What It Does |
|---------|------|-------------|
| Soul | files | Stores identity, policies, and governance rules |
| Brain | 8014 | LLM access, reasoning, model management (reference body: fused with tools/memory paths — see `MANIFEST.ka`) |
| Memory | 8022 | Data storage, search, session management |
| Hands | 8016 | File operations, tool execution, MCP connections |
| Senses | — | Webhooks, triggers, inputs — no dedicated Senses MCP port in reference map |
| Voice | — | UI output, chat formatting (planned) |
| Ka | 8010 | Health monitoring, service discovery (HTTP, not MCP) |
| Skeleton | 8017 | Database, schemas, data structure |
| Blood | 8015 | n8n workflows / event bus |
| Blood | 8020 | MaatLangChain pipeline / RAG |

Each card: emoji icon, service name, status (✅ online with port / ❌ offline / ⏳ planned). Click → goes to that service's detail. Total count bottom right: "7/7 online".

**Memory Meter** — card showing:
- Progress bar (green < 60%, yellow 60-80%, red > 80%)
- Capacity %
- Row count, database size (MB), latency (ms), freshness (time since last write — warn if > 24h)

**Maat Score** — card showing:
- Score out of 10 (large gold number)
- 5 breakdown bars: Truth, Justice, Balance, Order, Reciprocity (each 0-10)

**Evolution Status** — card showing:
- Active/inactive indicator
- Total learnings count, average confidence
- Last cycle timestamp, next cycle ETA
- "Run Now" button

**Recent Activity** — card with last 5 events:
- Icon + description + relative timestamp per row
- "View All →" link

---

## Screen 2: Ka Health 🛡

Service monitoring and self-healing.

**Service Status Table:**
| Column | Content |
|--------|---------|
| Service | emoji + name |
| Port | number (monospace) |
| Status | green/red/yellow dot |
| Latency | milliseconds |
| Server | server name |

Overall score below: "7/7 HEALTHY" or "DEGRADED" or "CRITICAL"

**Pain Log** — list of recent errors:
- Each: severity icon, timestamp, description, what auto-healing action was taken
- Empty state: "No pain events — the system is healthy"

**Healing Rules** — shows configured auto-recovery:
- Condition → action (e.g., "brain unreachable → retry 3x → fallback model")
- "Edit Rules" button

**Uptime Chart** — horizontal bars per service:
- Bar length = uptime % over last 24h
- Green > 99%, yellow 95-99%, red < 95%

---

## Screen 3: Memory 💾

Sub-tabs: **Banks | Episodic | Semantic | Patterns | Tasks | Learnings | Search**

### Banks tab (default):

**Primary Bank Card:**
- Adapter badge ("postgres" / "sqlite")
- Status badge ("Active 🟢")
- Capacity progress bar with %
- 4 stat boxes: row count, size (MB), latency (ms), freshness
- Type breakdown — stacked horizontal bar:
  - tasks (green), sessions (blue), learnings (purple), conversations (gold), errors (red)
  - Legend with counts below

**Archive Bank Card:**
- Same format, shows "Empty" if no archived data
- "Archive Now" button to manually trigger

**Lifecycle Flow:**
- 3 connected boxes: HOT (0-7d) → WARM (7-90d) → COLD (90d+)
- Entry count in each stage
- Auto-archive and restore-on-access toggle indicators

### Episodic / Semantic / Patterns / Tasks / Learnings tabs:
- Scrollable list of entries for that type
- Each row: type icon, content preview (2 lines), metadata (agent, timestamp), confidence score (if applicable)
- Click → expand to full detail in slide-over panel
- Pagination: "Load more" (20 at a time)

### Search tab:
- Full-width search input (debounced 500ms)
- Filter dropdowns: memory type, time range
- Results as card list with content preview, type badge, timestamp
- Empty: "No memories match your search"

---

## Screen 4: Brain 🧠

Model configuration and learning management.

**Model Configuration:**
- Active model dropdown (e.g., ollama/gemma)
- Fallback chain: ordered list with drag reorder, remove, add
- Endpoint display with status dot + latency
- "Test Model" button

**Learnings (44 total):**
- Confidence distribution: horizontal histogram bar
  - Purple gradient (light=low, dark=high confidence)
  - Vertical marker at 0.2 (archive threshold) and 0.8 (promote threshold)
- Recent learnings list:
  - Each row: content text, confidence score, thin purple bar proportional to score
  - Click to expand
- "View All →" link to Memory Learnings tab

**Decisions:**
- Timeline of decisions with rationale
- Empty: "No decisions logged yet"

---

## Screen 5: Hands 🤲

Installed apps, tool connections, packs.

**Apps** — card grid:
| App | What It Does | Ring |
|-----|-------------|------|
| Receptionist | Greets, routes inquiries, books appointments, answers FAQs | middle |
| Researcher | Web search, document analysis, citation, summarization | middle |
| Operator | Infrastructure management, deployment, monitoring | outer |
| Teacher | Tutoring, curriculum creation, quizzes, progress tracking | middle |

Each card: emoji, name, description (3 lines), ring badge (inner=red, middle=gold, outer=green pill)

**MCP Connections** — list:
- Server name, port, status dot, latency per row
- "Add Connection" button

**Packs** — grouped list:
| Type | Installed |
|------|-----------|
| Policy | maat-default, strict-safety |
| Tool | filesystem |
| Agent | tehuti |
| Learning | self-improve |

Click row → expand to toggle on/off

---

## Screen 6: Evolution 📊

How the system learns and gets smarter over time.

**Evolution Pipeline** — 7 connected stage boxes:

| Stage | What It Does | Key Metric |
|-------|-------------|-----------|
| SENSE | Collects recent conversations, errors, decisions | 24h window |
| STORE | Saves raw experience to episodic memory | 391 entries |
| PATTERN | Finds clusters of similar events | 3 found |
| PROMOTE | Moves high-confidence patterns to long-term memory | threshold: 0.8 |
| APPLY | Injects learnings into reasoning | max 5 per turn |
| MEASURE | Tracks if learnings improved outcomes | success rate |
| DECAY | Reduces unused learning confidence, strengthens used ones | -5%/cycle |

Each box: stage name, status icon (✅ done / ⏳ running / ─ pending), key metric.
Arrows between boxes pulse gold when loop is running.
Below: cycle interval, last run, next run.
"Run Evolution Now" button with confirmation.

**Confidence Map:**
- Histogram of all learnings by confidence (0.0 to 1.0)
- Vertical lines at 0.2 (archive) and 0.8 (promote)
- Stats: count above 0.8, count below 0.2, average

**Decay Simulator:**
- Input: starting confidence (number)
- Slider: cycles unused (0-50)
- Output: calculated result with visual bar showing the drop
- Config display: decay rate 5%, strengthen +10%, floor 0.1, archive at 0.2

**Cycle History:**
- List of last 10 cycles: number, timestamp, patterns found, learnings promoted, status
- Click to expand detail

---

## Screen 7: Settings ⚙

**Connection:**
- Body name (text)
- Discovery URL (text)
- API key (password with reveal toggle)
- "Test Connection" + "Disconnect" buttons

**Service Endpoints:**
- Text input per service: Brain, Memory, Hands, Senses, Skeleton, Blood
- "Auto-detect from Discovery" button (fetches /manifest, fills all fields)

**Memory Banks:**
- Primary adapter dropdown (PostgreSQL / SQLite)
- Archive adapter dropdown
- Auto-archive toggle
- Warn at % (number), Critical at % (number)

**Evolution Loop:**
- Enabled toggle
- Cycle interval dropdown (1h / 3h / 6h / 12h / 24h)
- Auto-promote toggle
- Decay rate %, strengthen rate %, archive threshold, promote threshold

**Buttons:** "Save Changes" (gold), "Reset to Defaults" (outlined)

---

## First-Run Screen

Full-screen when no host is saved.

1. Title: "Connect to MAAT Ecosystem"
2. Input: Discovery URL (e.g., http://192.168.4.21:8010)
3. "Discover" button → fetches /manifest → shows body name, service count, health
4. Input: API Key
5. "Connect" → tests auth → saves to localStorage → goes to Dashboard
6. Footer: "MAAT Ecosystem™ · Built on Ka Architecture · KA2 Methodology by Dr. Tdka Kilimanjaro · University of KMT" (link: https://universityofkmt.myshopify.com)

---

## Responsive

**Mobile (< 768px):** sidebar → bottom tab bar (5 icons). Single column. Tables → card lists. Pipeline → vertical.
**Tablet (768-1024px):** thin icon sidebar. 2-column grids.
**Desktop (> 1024px):** full sidebar with hover expand. 3-4 column grids.

---

## States

**Loading:** skeleton shimmer placeholders matching content shape.
**Error:** muted card + red dot + "Unreachable" + Retry button. Discovery down = full-width banner.
**Empty:** dim icon + helpful text explaining what will appear and when.

---

## API Endpoints (Data Sources)

**No auth needed:**
- `GET http://<host>:8010/manifest` → full body map
- `GET http://<host>:8010/health` → all service status

**Requires `Authorization: Bearer <key>` header:**
All memory calls POST to `http://<host>:8022`:
- `/memory_health` → health check
- `/memory_stats` → counts, capacity
- `/memory_search` → `{"query": "...", "limit": 10}`
- `/memory_get_tasks` → `{"limit": 20}`
- `/memory_get_learnings` → `{"limit": 20}`
- `/memory_get_decisions` → `{"limit": 20}`
- `/memory_get_recent_changes` → `{"limit": 10}`
- `/memory_get_sessions` → `{"limit": 20}`

Poll `/health` every 30s. Store host + key in localStorage.

---

## Footer (Dashboard only)

MAAT Ecosystem™ · Ka Architecture · KA2 Methodology by Dr. Tdka Kilimanjaro · [University of KMT](https://universityofkmt.myshopify.com)

Truth · Justice · Balance · Order · Reciprocity

𓂀
