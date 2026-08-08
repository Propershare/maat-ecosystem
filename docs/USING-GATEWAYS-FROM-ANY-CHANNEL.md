# Using MAAT Gateways from Any Channel

**Goal:** Drive the MAAT expert gateways from Telegram, Discord, n8n, a shell,
cron, your phone — anywhere — without touching a CLI and without editing
OpenClaw TypeScript. One HTTP endpoint. Every reply is logged, validated,
and scored automatically.

---

## The one picture

```
┌──────────────┐
│ Telegram     │──┐
└──────────────┘  │
┌──────────────┐  │
│ Discord      │──┤
└──────────────┘  │          ┌────────────────────────┐
┌──────────────┐  ├──HTTP──▶ │  :8040/ask             │
│ n8n          │──┤          │  gateway_server.py     │
└──────────────┘  │          │  routes → Ollama →     │
┌──────────────┐  │          │  Archivist → Guard →   │
│ curl / cron  │──┤          │  gitMaat               │
└──────────────┘  │          └────────────────────────┘
┌──────────────┐  │
│ OpenClaw     │──┘
└──────────────┘
```

One endpoint. Every channel. Every turn recorded.

---

## Start the server

```bash
bash /home/suspect/.n8n/scripts/start-gateway-server.sh
# or systemd:
sudo systemctl enable --now maat-gateway-server
```

Verify:

```bash
curl -s http://127.0.0.1:8040/info | python3 -m json.tool
curl -s http://127.0.0.1:8040/gateways
```

---

## Endpoints

| Method | Path | Purpose |
|-------|------|---------|
| `GET`  | `/health`   | Liveness, subsystem versions, registry contents |
| `GET`  | `/info`     | Plain-language description (read this first if you are a new agent) |
| `GET`  | `/gateways` | All registered gateways and their packs |
| `POST` | `/ask`      | The main endpoint. See below. |

### POST /ask

Body:

```json
{
  "message": "your message here",
  "gateway_id": "scout",          // optional; defaults to scout
  "session_id": "telegram:123",   // optional; generated if missing
  "user_id": "imhotep",           // optional
  "research_grade": null          // optional: force on/off; null = auto-detect
}
```

Reply:

```json
{
  "reply": "<the model's actual reply text>",
  "gateway": "scout",
  "expert": "scout",
  "model": "gemma4:e4b",
  "correlation_id": "telegram:123:0000",
  "decision": {
    "decision": "allow" | "review" | "deny",
    "scorecard": { ... },
    "rbl_flags": [],
    "forbidden_hits": []
  },
  "persist": { "jsonl_path": "...", "gitmaat_status": "ok" }
}
```

**The only field a human needs from this is `reply`.** Every other field is
for Sentinel, Bench, and Forge to learn from.

---

## Telegram path (no CLI needed)

You already have Telegram connected to OpenClaw. You don't need a new bot.
You need OpenClaw to forward user messages to `/ask` and reply with
`result.reply`.

### The simplest possible agent tool

In your OpenClaw agent prompt, add this instruction block:

> When a user sends a message, call the MAAT gateway before replying:
>
> 1. Use `web_fetch` (or equivalent) to POST to `http://127.0.0.1:8040/ask`
>    with body `{"message": "<user's message>", "gateway_id": "scout",
>    "session_id": "telegram:<chat_id>"}`.
> 2. Send the value of `result.reply` back to the user.
> 3. If `result.decision.decision` is `deny` or `review`, silently tag the
>    turn in your own log but still deliver the reply.
> 4. Do not try to reinterpret the user's message yourself. The gateway
>    is the expert; you are the channel.

That's the whole integration. No code, just instruction. The agent becomes
a thin conduit and every Telegram turn lands in
`/home/suspect/.n8n/logs/archivist/records.jsonl` with a scorecard.

### A tighter integration (later)

If you want first-class routing (pick different gateways from different
Telegram groups, for example), add a per-group mapping in
`~/.openclaw/openclaw.json`. Each allowed group/topic points at a
`gateway_id`, and the agent prompt reads that binding.

### Scaling gateways

To add a *new* gateway usable from Telegram:

1. Add an entry to `maat-ecosystem/skeleton/gateways/registry.yaml`.
2. (Optional) Add a retrieval pack under `data/retrieval_packs/<id>/`.
3. Restart the server: `systemctl restart maat-gateway-server`.
4. Call it: `{"gateway_id": "your-new-id", ...}`.

**No router code edited. No preset gymnastics.**

---

## Discord / Slack / n8n / anything

Same idea:

```bash
curl -s -X POST http://127.0.0.1:8040/ask \
  -H 'Content-Type: application/json' \
  -d '{"message":"hi","session_id":"cli:suspect"}'
```

For n8n: add an HTTP Request node → POST to `http://127.0.0.1:8040/ask`
→ use `{{$json.reply}}` downstream.

For cron: a three-line wrapper script posting to `/ask` with a fixed
message gives you scheduled prompts with full validation.

---

## Exposing on LAN (with auth)

Default: loopback only. To expose on LAN:

```bash
export GATEWAY_SERVER_BIND=0.0.0.0
export GATEWAY_SERVER_TOKEN="$(openssl rand -hex 32)"
systemctl restart maat-gateway-server
```

Then from another machine:

```bash
curl -H "Authorization: Bearer $TOKEN" \
  -X POST http://<lan-ip>:8040/ask \
  -H 'Content-Type: application/json' \
  -d '{"message":"hello"}'
```

The server **refuses** to bind non-loopback without a token. That is
deliberate — zero-trust-autonomy per `docs/MAAT-ZERO-TRUST-AUTONOMY.md`.

---

## What happens automatically on every turn

1. `ka2_router.route()` picks the expert and tags the request with
   `research_grade`, `level_of_analysis`, `research_type`.
2. `gateway_server` calls Ollama with the right model (from the gateway
   registry; LoRA winners override later).
3. The reply is wrapped in an `ArchivistRecord` with the pack and model
   references as sources.
4. `guard_validator.validate_turn()` runs — recomputes the scorecard,
   checks RBL flags, checks forbidden vocabulary, consults Tehuti Guard
   HTTP if reachable.
5. `archivist_gitmaat.persist()` appends to the JSONL stream and writes
   to gitMaat Postgres if reachable.
6. Sentinel is reading that JSONL stream and updating per-session state
   in the background.

You did none of that manually. You asked a question in Telegram.

---

## The "what is this" for future agents

If you are a fresh agent opening this workspace and see `gateway_server.py`,
here is the short version:

- **It's the front door.** Everything else calls into it.
- **It's channel-agnostic.** HTTP is the lingua franca. If you can POST JSON,
  you can use MAAT.
- **It enforces the contract.** You cannot bypass the Archivist record or
  the scorecard by calling it. They happen server-side, every turn.
- **It does not own the method.** KA2 and Maat rules live in
  `gateway_contract.py` and `guard_validator.py`. The server just wires them.

If the server is down and you need to reach the models anyway, hit Ollama
directly at `:11434` — but you'll have no record, no scorecard, no
governance. That's an explicit opt-out, not a shortcut.
