# MAAT Studio — Continuation Prompt

You already built the MAAT Studio dashboard (7 screens) and the Ka Architecture landing page (12 sections). This prompt fixes issues and finishes what was interrupted.

---

## 1. FIX: Landing Page Ports

The landing page has wrong port numbers everywhere. Update ALL references (body diagram, organ cards, Universal Body Plan table, discovery section, boot sequence) to these real values:

| Organ | Port | Protocol | Server Name |
|-------|------|----------|-------------|
| Soul | — (no port) | Files on disk | — |
| Brain | 8014 | MCP | tehuti-core (reference body also routes hands/memory paths here — see `MANIFEST.ka` `network:`) |
| Memory | 8022 | MCP | maat-memory |
| Hands | 8016 | MCP | filesystem |
| Senses | — | — | No dedicated MCP in reference map; webhooks, gateways, `senses/` apps |
| Voice | 3000 | HTTP | maat-studio (this app) |
| Ka | 8010 | HTTP | ka-discovery |
| Skeleton | 8017 | MCP | postgres |
| Blood | 8015 | MCP | n8n (workflows / event-shaped circulation) |
| Blood | 8020 | MCP | pipeline (MaatLangChain RAG) |

The discovery manifest endpoint is `GET http://<host>:8010/manifest`. Update the curl example in the Discovery section to show this.

---

## 2. FIX: Dashboard API Call Format

Memory organ calls should be POST to `http://<host>:8022/<tool_name>` with JSON body params. Update `src/lib/api.ts` if the current format uses `/call` with a method field — try both formats and use whichever the server accepts. The tools are:

```
POST http://<host>:8022/memory_stats        body: {}
POST http://<host>:8022/memory_health       body: {}
POST http://<host>:8022/memory_search       body: {"query": "...", "limit": 10}
POST http://<host>:8022/memory_get_tasks    body: {"limit": 20}
POST http://<host>:8022/memory_get_learnings body: {"limit": 20}
POST http://<host>:8022/memory_get_decisions body: {"limit": 20}
POST http://<host>:8022/memory_get_recent_changes body: {"limit": 10}
POST http://<host>:8022/memory_get_sessions body: {"limit": 20}
POST http://<host>:8022/memory_get_recent_work body: {"hours": 24}
```

All require header: `Authorization: Bearer <API_KEY>`

If the direct POST format fails with 404, fall back to the MCP format:
```
POST http://<host>:8022/call
body: {"method": "memory_stats", "params": {}}
```

---

## 3. FINISH: Landing Page 6 Enhancements

These were interrupted. Implement all 6:

### 3a. Parallax Star Field
- Background star particles that shift slightly with mouse movement
- Stars are tiny dots (1-2px), white, varying opacity (0.1-0.6)
- Parallax: different layers move at different speeds (foreground faster, background slower)
- Performance: use CSS transforms, not repainting. Cap at 100 stars.

### 3b. Interactive SVG Body Diagram
- In "The Body" section, replace the static organ list with an SVG human body outline
- Each organ is a clickable hotspot on the body at its anatomical position:
  - Soul → head/crown
  - Brain → forehead
  - Memory → left temple
  - Senses → eyes
  - Voice → throat
  - Ka → heart/chest center
  - Hands → both hands
  - Skeleton → spine/torso
  - Blood → veins/arteries radiating from heart
- Click an organ hotspot → tooltip shows: name, port, what it does, status
- Hover: organ region glows gold
- Gold lines connect organs like a nervous system
- The SVG should be simple line art, not detailed anatomy

### 3c. Typewriter Curl Terminal
- In the Discovery section, the curl command types out character by character
- After the command finishes typing, the JSON response "prints" line by line
- Terminal styling: black bg (#0A0A0F), green (#2D8B46) monospace text, blinking cursor
- Speed: 30ms per character for command, 50ms per line for response
- Triggers when scrolled into view (IntersectionObserver)
- After completing, stays static — no loop

### 3d. Ambient Audio Toggle
- Small speaker icon (🔊/🔇) in top-right corner of landing page
- Toggles ambient background audio (Web Audio API)
- Audio: subtle low-frequency drone/hum — synthesized, not a file
  - Use OscillatorNode: sine wave at ~60Hz, very low gain (0.02-0.05)
  - Add a second oscillator at ~90Hz, even lower, for depth
  - Filter with lowpass at 200Hz
- Default: OFF (muted). User clicks to enable.
- Fade in over 2 seconds when enabled, fade out over 1 second when disabled

### 3e. Gradient Section Bridges
- Between each landing page section, add a subtle gradient transition
- Instead of hard edges between sections, the backgrounds blend
- Implementation: 80px tall gradient div between sections
- Gradient from section-above-bg to section-below-bg
- This makes scrolling feel continuous rather than blocky

### 3f. Animated MaatBench Score Ring
- In the MaatBench section, the "49/49" score is inside an SVG ring
- Ring draws itself clockwise on scroll (stroke-dashoffset animation)
- Takes 2 seconds to complete the circle
- Ring color: gold (#D4A843) on dark background
- Ring thickness: 4px, radius: ~60px
- Number counts up from 0 to 49 as ring draws
- Triggers once when scrolled into view

### 3g. Maat Ecosystem section (Tehuti Lab reference body)

Add a full-width landing section and nav item so Ka Architecture (story) and Maat Ecosystem (code) are explicitly tied.

**Canonical copy:** paste from [`docs/UI-MAAT-ECOSYSTEM-STRIP.md`](UI-MAAT-ECOSYSTEM-STRIP.md). Do not rewrite marketing separately on Replit — sync with that file.

**Landing page (Ka intro):**

1. **Nav:** add link `Ecosystem` → anchor `#ecosystem` (after Apps, before Bench).
2. **New section** between Apps & Packs and MaatBench:
   - **H2:** `Maat Ecosystem — reference body`
   - **Subtitle:** `Ka Architecture (framework) · Maat Ecosystem (implementation)`
   - **Body:** one short paragraph = Ka is the pattern; Maat Ecosystem is the living codebase (`MANIFEST.ka`, nine organ dirs, `maatbench/`).
   - **Card grid (4 items):** MANIFEST.ka, LAB-WORKSPACE.md, maatbench/README.md, parent `docs/WORKSPACE-KA-MAP.md` — each with one line + link. Use `GITHUB_REPO_URL` or “private monorepo” for the primary CTA until a public repo exists.
   - **Footer line:** attribution — framework lineage stays Dr. Tdka Kilimanjaro / University of KMT; Maat Ecosystem is the reference implementation.

**React / styling:**

- Reuse tokens from REPLIT-PROMPTS (`--gold` `#D4A843`, `--bg-card` `#1A1A1A`, `--text` `#F5F0E8`, `--text-dim` `#666666`, `--blue` for links).
- Match existing card component used in Apps & Packs.
- **Do not** clone the full monorepo into Replit — links only (raw GitHub URLs when public, or instructions to open paths in Tehuti Lab).

**MAAT Studio (dashboard app):** optional duplicate strip on an “About” or footer area using the same copy; keep one source file (`UI-MAAT-ECOSYSTEM-STRIP.md`) for both.

---

## 4. ADD: Dashboard — Live Data Indicators

The dashboard currently shows static/mock data in several places. Add visual indicators for what's live vs pending:

### 4a. Connection-Aware Components
- Every data card checks if the API is actually reachable
- If connected: show real data
- If disconnected: show the card structure but with a muted overlay and "Connect to see live data" text
- If loading: skeleton shimmer (dark `--bg-card` with left-to-right sweep, 1.5s cycle)
- If error: red-tinted border + "Failed to load — Retry" button

### 4b. Last Updated Timestamps
- Each data section shows "Updated 30s ago" in dim text (bottom-right of card)
- Updates on each poll cycle
- If stale (> 2 minutes): shows yellow warning "Data may be stale"

### 4c. Memory Meter Alerts
- When capacity > 80%: yellow pulsing border on the memory meter card
- When capacity > 95%: red pulsing border + alert banner at top of dashboard "⚠️ Memory near capacity (95%)"

---

## 5. ADD: Dashboard — Organ Detail Drill-Down

When you click an organ card on the Dashboard or a row in Ka Health table, show a slide-over panel from the right (400px wide, dark bg) with:

- Organ name + emoji (large, top)
- Status: alive/dead with colored dot
- Port and server name
- What it does (one paragraph)
- Endpoint URL
- Current latency
- Uptime % (24h)
- If memory organ: show bank stats inline
- If brain organ: show active model + fallback chain
- "View Full Page →" link to the relevant screen (Memory, Brain, etc.)

Panel slides in from right with 200ms ease transition. Click outside or X button to close.

---

## 6. ADD: Memory Bank Swap UI

In Settings → Memory Banks section, add the ability to switch backends:

- Current active bank shown with green "Active" badge
- "Switch to SQLite" / "Switch to PostgreSQL" button (shows the other option)
- Clicking shows confirmation modal:
  - "Migrate 391 entries from postgres to sqlite?"
  - "This may take a few minutes for large databases."
  - [Cancel] [Migrate & Switch]
- During migration: progress bar in the modal
- After: success toast "Memory migrated to sqlite — 391 entries"
- This calls a backend endpoint (if available) or shows instructions for manual migration

---

## 7. ADD: App Management in Hands Screen

The Hands screen shows app cards but they're display-only. Add:

- Each app card gets an "Active" / "Inactive" toggle
- Click toggle → confirmation → calls API to enable/disable
- "Install New App" button at bottom of grid → opens a modal:
  - Text input for app manifest URL or local path
  - [Install] button
  - Shows install progress
- Each card also shows: version number, workflow count, tool count
- Click card → expands to show: full description, system prompt preview, workflow list, policy list

---

## 8. ADD: Evolution — Cycle Detail View

When you click a cycle in the Cycle History list on Evolution screen:

- Expand inline (accordion style) to show:
  - What was sensed: list of inputs (conversations, errors, decisions)
  - Patterns found: each pattern with description and confidence score
  - What was promoted: learnings that crossed the 0.8 threshold
  - What decayed: learnings that lost confidence this cycle
  - Cycle duration
  - Success/failure status with reason

---

## 9. POLISH

### Animations
- Organ status dots: subtle pulse (opacity 0.7→1.0, 2s cycle)
- Progress bars: animate from 0 to value on render (ease-out, 800ms)
- Route changes: main canvas fades in (150ms)
- Sidebar expand: width 200ms ease
- Cards on hover: border brightens, translateY(-1px)

### Keyboard Shortcuts
- `1-7` keys: navigate to screens (Dashboard, Ka Health, Memory, Brain, Hands, Evolution, Settings)
- `Esc`: close any open panel/modal
- `/`: focus search (when on Memory screen)

### Page Title
- Update browser tab title per screen: "MAAT Studio — Dashboard", "MAAT Studio — Memory", etc.
- Favicon: use 𓂀 or 🔮 emoji
