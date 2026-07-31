# MAAT Multi-Agent App — PR Build Document

> **Version:** 1.0.0  
> **Status:** Planning  
> **Lab:** Tehuti Lab (192.168.4.36)  
> **Repo:** `Propershare/maat-ecosystem`  
> **License:** Apache 2.0 / Proprietary  

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [System Architecture](#2-system-architecture)
3. [Multi-Agent Design](#3-multi-agent-design)
4. [Component Breakdown](#4-component-breakdown)
5. [Build Phases](#5-build-phases)
6. [Data Flow](#6-data-flow)
7. [Security & Privacy](#7-security--privacy)
8. [Deployment](#8-deployment)
9. [Roadmap](#9-roadmap)
10. [Appendix](#10-appendix)

---

## 1. Executive Summary

### 1.1 Vision
A members-only, privacy-first, multi-agent iOS application that runs **entirely on-device** with optional lab sync. Users interact via **voice** (Meta glasses or phone mic) to access trading tools, constitutional safety features, note-taking, book writing, and lab knowledge — all processed by on-device Gemma 4 with zero cloud dependency.

### 1.2 Core Principles
| Principle | Description |
|-----------|-------------|
| **Zero Cloud** | All inference, storage, and processing on-device |
| **Voice-First** | Hands-free operation via Meta glasses or phone |
| **Members-Only** | Invite-code gated, lab-verified |
| **Constitutional Safety** | Encrypted recordings, auto-delete, rights recitation |
| **Local-First** | Data syncs to lab only when user opts in |

### 1.3 Target Users
- **Traders** — Easy E / ICT community needing hands-free chart analysis, trade journaling, position sizing
- **Activists** — Need constitutional safety tools, encrypted recording, know-your-rights
- **Writers** — Voice-to-book, note-taking, idea capture
- **Lab Members** — Query MAAT memory, search artifacts, check trading system status

---

## 2. System Architecture

### 2.1 High-Level Topology

```
┌─────────────────────────────────────────────────────────────┐
│                     iPhone (On-Device)                       │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                   MAAT App (SwiftUI)                  │   │
│  │                                                      │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────────────┐   │   │
│  │  │  Agent    │  │  Agent   │  │     Agent        │   │   │
│  │  │  Orator  │  │  Trader  │  │    Guardian      │   │   │
│  │  │ (Voice)  │  │ (Trading)│  │  (Safety)        │   │   │
│  │  └────┬─────┘  └────┬─────┘  └───────┬──────────┘   │   │
│  │       │             │                │              │   │
│  │  ┌────┴─────────────┴────────────────┴──────────┐   │   │
│  │  │           Agent Orchestrator                  │   │   │
│  │  │  (Routes intent → agent, manages context)    │   │   │
│  │  └────────────────────┬─────────────────────────┘   │   │
│  │                       │                              │   │
│  │  ┌────────────────────┴─────────────────────────┐   │   │
│  │  │           Gemma 4 (On-Device LLM)             │   │   │
│  │  │           via MLX Swift                       │   │   │
│  │  └────────────────────┬─────────────────────────┘   │   │
│  │                       │                              │   │
│  │  ┌────────────────────┴─────────────────────────┐   │   │
│  │  │           Core Services Layer                │   │   │
│  │  │  ┌────────┐ ┌────────┐ ┌────────┐ ┌──────┐  │   │   │
│  │  │  │Speech  │ │Glasses │ │Encrypt │ │Local │  │   │   │
│  │  │  │Service │ │Service │ │Storage │ │DB    │  │   │   │
│  │  │  └────────┘ └────────┘ └────────┘ └──────┘  │   │   │
│  │  └─────────────────────────────────────────────┘   │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Optional: Lab Sync Layer                  │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────────────┐   │   │
│  │  │ Bridge   │  │ MAAT    │  │  Git Sync        │   │   │
│  │  │ Client   │  │ Memory  │  │  (Episodic)      │   │   │
│  │  └────┬─────┘  └──────────┘  └──────────────────┘   │   │
│  └───────┼──────────────────────────────────────────────┘   │
└──────────┼───────────────────────────────────────────────────┘
           │ HTTP (LAN / Tunnel)
           ▼
┌─────────────────────────────────────────────────────────────┐
│                  Mac Lab (192.168.4.36)                      │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Bridge Server (Python)                   │   │
│  │  :9876                                                │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────────────┐   │   │
│  │  │ Scribe   │  │ Trading │  │  Membership      │   │   │
│  │  │ API      │  │ API     │  │  API             │   │   │
│  │  └────┬─────┘  └────┬─────┘  └───────┬──────────┘   │   │
│  │       │             │                │              │   │
│  │  ┌────┴─────────────┴────────────────┴──────────┐   │   │
│  │  │           Hermes Gateway (localhost:8642)     │   │   │
│  │  │           MCP → MAAT Memory                   │   │   │
│  │  └─────────────────────────────────────────────┘   │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │ MAAT Memory  │  │  maat-scribe │  │  Trading System  │   │
│  │ (git files)  │  │  (notes/book)│  │  (FVG Edge)      │   │
│  └──────────────┘  └──────────────┘  └──────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │           Lab Brain Postgres (192.168.4.21)           │   │
│  │           Artifacts, Members, Audit Log              │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Technology Stack

| Layer | Technology | Justification |
|-------|-----------|---------------|
| **App Framework** | SwiftUI + UIKit | Native iOS, best performance, full hardware access |
| **On-Device LLM** | MLX Swift (Apple) | Optimized for Apple Silicon, runs Gemma 4 locally |
| **Voice Input** | Apple Speech Framework | On-device, no data leaves phone |
| **Voice Output** | AVSpeechSynthesizer | Built-in, routes to glasses speakers |
| **Glasses** | Meta Wearables DAT SDK | Official Meta SDK for camera/audio |
| **Local Storage** | CoreData + CryptoKit | Encrypted, biometric-locked |
| **Networking** | URLSession | Standard iOS networking |
| **Backend** | Python http.server | Zero dependencies, runs on any Mac |
| **Memory** | Git-based markdown files | Versioned, auditable, agent-readable |
| **Database** | PostgreSQL (lab brain) | Artifacts, members, audit |

---

## 3. Multi-Agent Design

### 3.1 Agent Architecture

```
                    ┌─────────────────────────┐
                    │   User Input (Voice)     │
                    │   "Log a trade: ES=F..." │
                    └────────────┬────────────┘
                                 │
                    ┌────────────▼────────────┐
                    │    Agent Orchestrator    │
                    │                         │
                    │  1. Parse intent        │
                    │  2. Route to agent      │
                    │  3. Collect response    │
                    │  4. Speak back          │
                    └────┬──────┬──────┬──────┘
                         │      │      │
              ┌──────────┘      │      └──────────┐
              ▼                 ▼                  ▼
     ┌────────────────┐ ┌────────────┐ ┌────────────────┐
     │  Agent Orator   │ │Agent Trader│ │Agent Guardian   │
     │                 │ │            │ │                 │
     │ • Voice notes   │ │ • FVG scan │ │ • Know rights   │
     │ • Book writing  │ │ • Journal  │ │ • Record        │
     │ • Picture save  │ │ • Position │ │ • Auto-delete   │
     │ • Idea capture  │ │ • Sessions │ │ • Emergency     │
     │ • Lab queries   │ │ • Ideas    │ │ • Training      │
     └────────────────┘ └────────────┘ └────────────────┘
```

### 3.2 Agent Definitions

#### Agent Orator (Voice + Scribe)
| Capability | Input | Output | Local/Remote |
|-----------|-------|--------|-------------|
| Save Note | Voice text | File on Mac + MAAT memory | Remote (bridge) |
| Write Book | Voice text | Chapter/section files | Remote (bridge) |
| Save Picture | Camera image | File on Mac | Remote (bridge) |
| List Notes | Voice command | Formatted list | Remote (bridge) |
| Show Book | Voice command | Book structure | Remote (bridge) |
| Lab Status | Voice command | Bridge health | Remote (bridge) |
| Search Memory | Voice query | Search results | Remote (bridge) |

#### Agent Trader (Trading Tools)
| Capability | Input | Output | Local/Remote |
|-----------|-------|--------|-------------|
| FVG Scan | OHLC candles | FVG analysis | Local (JS engine) |
| Log Trade | Trade details | Saved to journal | Local (CoreData) |
| Journal Stats | Voice command | Win rate, P&L | Local (CoreData) |
| Position Calc | Account, risk, entry | Position size, R:R | Local (JS engine) |
| Session Timer | Voice command | Active sessions | Local (JS engine) |
| Save Idea | Voice text | Saved to scratchpad | Local (CoreData) |
| Trading Status | Voice command | System status | Remote (bridge) |

#### Agent Guardian (Constitutional Safety)
| Capability | Input | Output | Local/Remote |
|-----------|-------|--------|-------------|
| Know Rights | Voice command | Rights recitation | Local (static) |
| Start Recording | Voice/tap | Encrypted video | Local (encrypted) |
| Emergency Contact | Voice command | Send location | Local (SMS) |
| Auto-Delete | Timer | Wipe sensitive data | Local (timer) |
| Training Scenario | Voice command | Roleplay | Local (LLM) |

### 3.3 Intent Routing

```
User: "Save a note: ES looking bearish at 7450"
       │
       ▼
Orchestrator: Parse intent
       │
       ├─ Keywords: "save a note" → Agent Orator
       ├─ Keywords: "ES", "bearish", "7450" → Agent Trader (context)
       │
       ▼
Agent Orator: POST /note {content: "ES looking bearish at 7450", tags: "trading"}
       │
       ▼
Response: "Note saved. Also, I see you mentioned a bearish setup on ES.
           Want me to log that as a trade idea?"
```

### 3.4 Context Management

Each agent maintains a short-term context window (last 5 interactions). The orchestrator merges context when routing between agents.

```
Context Window:
├── [0] User: "Log a trade: ES=F long, entry 7448, exit 7500"
├── [1] Agent: "Trade logged. P&L: +$104"
├── [2] User: "What's my win rate?"
├── [3] Agent: "67% over 12 trades"
└── [4] User: "Save a note about that last trade"
      └── Orator uses context from Trader to enrich the note
```

---

## 4. Component Breakdown

### 4.1 iOS App Components

```
MAAT-App/
├── App/
│   ├── MAATApp.swift              # App entry, state management
│   ├── ContentView.swift          # Main UI (talk button, mode switch)
│   └── Info.plist                 # Permissions, config
│
├── Agents/
│   ├── AgentOrchestrator.swift    # Intent routing, context management
│   ├── AgentOrator.swift         # Voice notes, book, pictures
│   ├── AgentTrader.swift         # Trading tools
│   └── AgentGuardian.swift       # Constitutional safety
│
├── Core/
│   ├── GemmaService.swift         # On-device LLM wrapper (MLX)
│   ├── SpeechService.swift        # Voice I/O
│   ├── GlassesService.swift       # Meta glasses SDK
│   └── EncryptedStorage.swift     # Biometric-locked storage
│
├── Models/
│   ├── Trade.swift                # Trade journal model
│   ├── Note.swift                 # Scratchpad model
│   ├── FVG.swift                  # FVG analysis model
│   └── Member.swift               # Membership model
│
├── Services/
│   ├── BridgeClient.swift         # HTTP client for lab bridge
│   ├── LocalEngine.swift          # Local JS execution for FVG/position
│   └── SyncService.swift          # Optional lab sync
│
├── UI/
│   ├── TalkButton.swift           # Big red mic button
│   ├── MembershipView.swift       # Invite code entry
│   ├── ModeSelector.swift         # Trader/Guardian toggle
│   └── ResponseView.swift         # Text + voice response
│
└── Resources/
    ├── Assets.xcassets            # Icons, branding
    └── Gemma4/                    # Model files (downloaded at runtime)
```

### 4.2 Bridge Server Components

```
edge-bridge/
├── bridge_server.py               # HTTP API server
├── .nojekyll                      # GitHub Pages config
├── README.md                      # Documentation
│
├── maat-bridge/                   # All-in-one skill (AI Edge Gallery)
│   ├── SKILL.md
│   └── scripts/index.html
│
├── maat-scribe/                   # Voice notes + book skill
│   ├── SKILL.md
│   └── scripts/index.html
│
├── fvg-scanner/                   # FVG analysis skill
│   ├── SKILL.md
│   └── scripts/index.html
│
├── trade-journal/                 # Trade logging skill
│   ├── SKILL.md
│   └── scripts/index.html
│
├── position-calculator/           # Position sizing skill
│   ├── SKILL.md
│   └── scripts/index.html
│
├── session-timer/                 # Session tracking skill
│   ├── SKILL.md
│   └── scripts/index.html
│
├── trade-scratchpad/              # Trade ideas skill
│   ├── SKILL.md
│   └── scripts/index.html
│
├── chart-vision/                  # Chart analysis skill
│   ├── SKILL.md
│   └── scripts/index.html
│
└── maat-trader/                   # Combined trading skill
    ├── SKILL.md
    └── scripts/index.html
```

### 4.3 Lab Components

```
maat-ecosystem/
├── ios-app/                       # iOS app source
├── edge-bridge/                   # Bridge server + skills
├── maat-memory/                   # Git-based memory store
│   ├── episodic/                  # Daily logs, scans
│   └── semantic/                  # System knowledge
├── maat-scribe/                   # Voice notes + book files
│   ├── notes/                     # Saved notes
│   ├── book/                      # Book chapters
│   └── pictures/                  # Saved images
├── governance/                    # Constitutional audit
└── docs/                          # Documentation
```

---

## 5. Build Phases

### Phase 1: Foundation (Week 1-2)
**Goal:** Working iOS app with talk button + on-device Gemma 4

| Task | Description | Status |
|------|-------------|--------|
| 1.1 | Clean Xcode project setup | ✅ Done |
| 1.2 | MLX Swift integration | 🔄 In progress |
| 1.3 | Speech service (voice in/out) | ✅ Done |
| 1.4 | Big talk button UI | ✅ Done |
| 1.5 | Membership gate (offline codes) | ✅ Done |
| 1.6 | Build to iPhone via Xcode | ✅ Done |
| **Milestone** | **App runs on iPhone with talk button** | **🔜** |

### Phase 2: Multi-Agent Core (Week 3-4)
**Goal:** Agent orchestrator + 3 agents working

| Task | Description | Status |
|------|-------------|--------|
| 2.1 | Agent orchestrator (intent routing) | ⬜ |
| 2.2 | Agent Orator (voice notes + book) | ⬜ |
| 2.3 | Agent Trader (FVG, journal, position) | ⬜ |
| 2.4 | Agent Guardian (rights, recording) | ⬜ |
| 2.5 | Local JS engine for offline tools | ⬜ |
| 2.6 | Context management across agents | ⬜ |
| **Milestone** | **All 3 agents respond to voice commands** | **🔜** |

### Phase 3: Lab Integration (Week 5-6)
**Goal:** Bridge server + MAAT memory sync

| Task | Description | Status |
|------|-------------|--------|
| 3.1 | Bridge client in iOS app | ⬜ |
| 3.2 | Scribe API (notes, book, pictures) | ✅ Done |
| 3.3 | Trading API (status, queries) | ✅ Done |
| 3.4 | Membership API (verify, register) | ✅ Done |
| 3.5 | MAAT memory write (episodic) | ✅ Done |
| 3.6 | Optional sync toggle in settings | ⬜ |
| **Milestone** | **App syncs with lab when on same network** | **🔜** |

### Phase 4: Meta Glasses (Week 7-8)
**Goal:** Full glasses integration via Meta SDK

| Task | Description | Status |
|------|-------------|--------|
| 4.1 | Meta Wearables SDK package added | ✅ Done |
| 4.2 | Glasses connection service | ⬜ |
| 4.3 | Camera capture → agent analysis | ⬜ |
| 4.4 | Audio routing to glasses speakers | ⬜ |
| 4.5 | One-tap glasses button → record | ⬜ |
| 4.6 | Meta developer approval | 🔄 Waiting on user |
| **Milestone** | **Full hands-free operation via glasses** | **🔜** |

### Phase 5: Polish & Ship (Week 9-10)
**Goal:** TestFlight release for community

| Task | Description | Status |
|------|-------------|--------|
| 5.1 | UI polish (dark mode, animations) | ⬜ |
| 5.2 | Error handling + edge cases | ⬜ |
| 5.3 | Performance optimization | ⬜ |
| 5.4 | TestFlight build + distribution | ⬜ |
| 5.5 | Invite code generation system | ⬜ |
| 5.6 | Documentation + onboarding | ⬜ |
| **Milestone** | **v1.0 on TestFlight for members** | **🔜** |

---

## 6. Data Flow

### 6.1 Voice Command Flow

```
1. User taps glasses button (or phone mic)
       │
2. SpeechService starts listening
       │
3. Apple Speech → text (on-device)
       │
4. AgentOrchestrator parses intent
       │
5. Routes to appropriate agent
       │
6. Agent processes:
   ├─ Local: JS engine / CoreData
   └─ Remote: HTTP to bridge server
       │
7. Response formatted
       │
8. SpeechService speaks back (→ glasses speakers)
       │
9. Response also shown on screen
```

### 6.2 Data Storage Flow

```
User says "Save a note: ..."
       │
       ▼
Agent Orator
       │
       ├─ Local: Save to CoreData (encrypted)
       │
       └─ If sync enabled:
              │
              ▼
          Bridge Client → POST /note
              │
              ▼
          Bridge Server
              │
              ├─ Save to ~/maat-scribe/notes/note.md
              │
              └─ MCP → MAAT Memory (git commit)
```

### 6.3 Trading Data Flow

```
User says "Log a trade: ES=F long, entry 7448..."
       │
       ▼
Agent Trader
       │
       ├─ Parse: symbol=ES=F, direction=long, entry=7448
       │
       ├─ Calculate: P&L, R:R
       │
       ├─ Save to CoreData (encrypted)
       │
       └─ Response: "Trade logged. P&L: +$104"
              │
              ▼
          SpeechService speaks back
```

---

## 7. Security & Privacy

### 7.1 On-Device Security

| Measure | Implementation |
|---------|---------------|
| **All inference** | MLX Swift runs Gemma 4 locally — no cloud |
| **Voice data** | Apple Speech framework — on-device processing |
| **Trade data** | CoreData + CryptoKit AES-256 encryption |
| **Recordings** | Biometric-locked (FaceID/TouchID) |
| **Auto-delete** | Configurable timer (default 24h) wipes sensitive data |
| **No telemetry** | Zero analytics, zero crash reporting |

### 7.2 Network Security

| Measure | Implementation |
|---------|---------------|
| **Lab sync** | Optional, user-enabled toggle |
| **Bridge connection** | LAN-only by default (192.168.4.x) |
| **Tunnel** | HTTPS via localhost.run (temporary, for remote) |
| **No external APIs** | All trading tools run local JS engine |
| **No accounts** | Invite codes only, no email/password |

### 7.3 Constitutional Safety

| Feature | Description |
|---------|-------------|
| **Know Your Rights** | Offline recitation of 4th/5th Amendment rights |
| **Encrypted Recording** | Video/audio encrypted with device key |
| **Emergency Contact** | One-tap sends "I'm being detained" + location |
| **Auto-Delete Protocol** | If no check-in within N hours, evidence forwarded |
| **Training Scenarios** | AI roleplay for de-escalation practice |

---

## 8. Deployment

### 8.1 Distribution Channels

| Channel | Method | Best For |
|---------|--------|----------|
| **TestFlight** | Apple's beta system (100 users) | Early community testing |
| **App Store** | Public listing | Public launch |
| **Enterprise** | In-house distribution | Full control, no Apple review |

### 8.2 Membership Flow

```
1. Lab generates invite code
       │
2. User downloads app (TestFlight link)
       │
3. App opens → asks for invite code
       │
4. Code verified (offline list + lab check)
       │
5. User is member → full access
       │
6. Optional: Register device with lab
```

### 8.3 Build Pipeline

```
Developer Mac (Xcode)
       │
       ├─ Build .app
       │
       ├─ Sign with development certificate
       │
       ├─ Install to iPhone via USB
       │
       └─ Archive → TestFlight / App Store
```

---

## 9. Roadmap

### v1.0 (Current — 10 weeks)
- [x] iOS app scaffold
- [x] Talk button + speech I/O
- [x] Membership gate
- [x] Bridge server with 8 skills
- [x] GitHub Pages skill hosting
- [ ] MLX Swift Gemma 4 integration
- [ ] Agent orchestrator
- [ ] All 3 agents functional
- [ ] Meta glasses SDK integration
- [ ] TestFlight release

### v2.0 (Future)
- [ ] Local MoE model (mixture of experts)
- [ ] RAG API for backend upgrades
- [ ] Android version (fork AI Edge Gallery)
- [ ] Workflowware template generator
- [ ] Community skill marketplace
- [ ] Revenue model (subscription for RAG)

### v3.0 (Vision)
- [ ] Fully autonomous trading agent
- [ ] Real-time chart analysis via glasses camera
- [ ] Multi-user lab collaboration
- [ ] Custom model training pipeline
- [ ] White-label for other communities

---

## 10. Appendix

### 10.1 Key Files Reference

| File | Path | Purpose |
|------|------|---------|
| App entry | `ios-app/MAAT-App/MAATApp.swift` | App lifecycle, state |
| Main UI | `ios-app/MAAT-App/ContentView.swift` | Talk button, mode switch |
| Speech | `ios-app/MAAT-App/SpeechService.swift` | Voice I/O |
| LLM | `ios-app/MAAT-App/GemmaService.swift` | On-device Gemma 4 |
| Storage | `ios-app/MAAT-App/EncryptedStorage.swift` | Encrypted local data |
| Glasses | `ios-app/MAAT-App/GlassesService.swift` | Meta SDK wrapper |
| Bridge | `edge-bridge/bridge_server.py` | HTTP API server |
| Skills | `edge-bridge/maat-bridge/` | All-in-one skill |
| Memory | `maat-memory/` | Git-based knowledge store |

### 10.2 API Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/status` | Bridge health |
| GET | `/episodic` | Recent memories |
| GET | `/semantic` | Semantic knowledge |
| GET | `/trading` | Trading system status |
| GET | `/search?q=` | Search memory |
| GET | `/notes` | List saved notes |
| GET | `/book` | List book structure |
| POST | `/note` | Save voice note |
| POST | `/book` | Write book section |
| POST | `/picture` | Save picture |
| POST | `/verify` | Check invite code |
| POST | `/register` | Register device |
| POST | `/generate` | Create invite code |

### 10.3 Environment

| Variable | Value | Purpose |
|----------|-------|---------|
| Mac IP | `192.168.4.36` | Bridge server host |
| Bridge Port | `9876` | HTTP API port |
| Hermes Gateway | `localhost:8642` | MCP server |
| Lab Brain | `192.168.4.21:5432` | Postgres |
| Tunnel | `*.lhr.life` | Remote HTTPS access |
| Xcode | 16.2 | Build environment |
| iOS Target | 17.0+ | Minimum deployment |
| Swift | 6.0 | Language version |

### 10.4 Glossary

| Term | Definition |
|------|------------|
| **Agent** | A specialized module that handles a domain of tasks (trading, voice, safety) |
| **Orchestrator** | Routes user intent to the correct agent and manages context |
| **Bridge** | HTTP server on the Mac that the iPhone app calls for lab operations |
| **MAAT Memory** | Git-based markdown store for episodic and semantic knowledge |
| **MLX Swift** | Apple's framework for running ML models on Apple Silicon |
| **Meta DAT** | Device Access Toolkit — Meta's SDK for glasses integration |
| **FVG** | Fair Value Gap — ICT/SMC trading concept |
| **50-Yard Line** | Midpoint of an FVG, the "battlefield" for price action |
| **Constitutional Safety** | Features designed to protect users during police encounters |

---

*Document maintained by Hermes Agent (MAAT FVG Edge)*  
*Last updated: 2026-07-31*  
*Next review: Phase 2 completion*
