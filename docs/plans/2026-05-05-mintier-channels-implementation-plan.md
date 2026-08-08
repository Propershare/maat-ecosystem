# Mintier Channels Implementation Plan

> For Hermes: Use subagent-driven-development skill to execute task-by-task if implementation is requested.

Goal: Launch and operationalize Mintier multi-channel communications (WhatsApp, Telegram, Discord, X) with a single content spine, governance controls, and measurable growth loops.

Architecture: A hub-and-spoke model: one canonical content source in the repo, distributed publishing via OpenClaw channels and scheduled cron jobs, with memory logging and policy gating (Tehuti Guard) for high-impact actions.

Tech Stack: OpenClaw gateway, cron jobs, WhatsApp/Telegram/Discord/X integrations, gitMaat memory scripts, Tehuti Guard policy API, markdown docs in `/home/suspect/.n8n/docs/`.

---

## Assumptions and Scope

- Workspace root is `/home/suspect/.n8n`.
- OpenClaw gateway configured in `~/.openclaw/openclaw.json` and reachable.
- Mintier is the brand/project for the channels.
- No paid growth tooling is required for v1; organic workflows first.

Out of scope (v1): paid ad campaigns, deep CRM integrations, advanced attribution modeling.

---

## Task 1: Create canonical Mintier channel strategy docs

Objective: Define channel roles, voice, cadence, and ownership in versioned docs.

Files:
- Create: `/home/suspect/.n8n/docs/mintier/channels/README.md`
- Create: `/home/suspect/.n8n/docs/mintier/channels/channel-map.yaml`

Step 1: Write README with operating model
- Include:
  - Purpose per channel (awareness, community, support, conversion)
  - Content pillars (education, updates, proof, culture, CTA)
  - Voice and style rules per platform
  - Escalation owner per channel

Step 2: Write `channel-map.yaml`
- Include keys:
  - `channel_id`, `platform`, `role`, `primary_audience`, `owner`, `cadence`, `cta_type`

Step 3: Verify
- Confirm files exist and are readable.

---

## Task 2: Build 30-post content matrix (single source)

Objective: Create one canonical queue of posts adaptable to each channel.

Files:
- Create: `/home/suspect/.n8n/docs/mintier/channels/content-matrix-30d.csv`
- Create: `/home/suspect/.n8n/docs/mintier/channels/templates.md`

Step 1: Create 30-day matrix CSV columns
- `day, pillar, theme, source_post, whatsapp_variant, telegram_variant, discord_variant, x_variant, cta, status`

Step 2: Add reusable templates
- 5 template families:
  - Launch/update
  - How-to tip
  - Case/proof
  - Community question
  - CTA prompt

Step 3: Verify
- CSV has 30 rows (day 1-30).

---

## Task 3: Implement posting schedule via cron

Objective: Establish reliable publishing cadence per channel.

Files:
- Create: `/home/suspect/.n8n/docs/mintier/channels/cron-schedule.md`

Step 1: Define schedule policy
- Telegram: 1-2/day
- WhatsApp: 1/day
- Discord: 1/day + conversation prompts
- X: 2/day

Step 2: Create cron jobs (example)
- Morning publish: `0 9 * * *`
- Afternoon publish: `0 15 * * *`
- Evening engagement: `0 20 * * *`

Step 3: Delivery targets
- Default to `origin` for testing; switch to explicit channel targets after validation.

Step 4: Verify
- List cron jobs and confirm next-run timestamps.

---

## Task 4: Add moderation + policy gates

Objective: Prevent risky/autonomous misfires before publishing.

Files:
- Create: `/home/suspect/.n8n/docs/mintier/channels/governance.md`

Step 1: Define risk classes
- Low: standard educational posts
- Medium: competitive claims, performance claims
- High: legal/financial/sensitive statements

Step 2: Wire policy checks
- High-risk posts require Tehuti Guard check (`POST /decision`) before send.

Step 3: Incident playbook
- If policy denies: hold post, notify owner, create revision task.

Step 4: Verify
- Simulate one high-risk post through dry-run check path.

---

## Task 5: Heartbeat + monitoring loop

Objective: Keep channels actively maintained without spammy behavior.

Files:
- Create: `/home/suspect/.n8n/HEARTBEAT.md`
- Create: `/home/suspect/.n8n/memory/heartbeat-state.json` (if absent)

Step 1: HEARTBEAT checklist
- Check mentions/replies
- Check pending DMs
- Check unanswered community questions
- Check campaign day status

Step 2: Quiet-hour policy
- Do not push non-urgent outbound content during 23:00-08:00 local.

Step 3: Verify
- Run one heartbeat cycle and log decisions.

---

## Task 6: Metrics and weekly review

Objective: Track outcomes and tune channel mix quickly.

Files:
- Create: `/home/suspect/.n8n/docs/mintier/channels/metrics.md`
- Create: `/home/suspect/.n8n/docs/mintier/channels/weekly-review-template.md`

Step 1: Define KPI baseline
- Reach/impressions
- Engagement rate
- Response latency
- CTA conversion count

Step 2: Weekly review ritual
- Keep / kill / iterate decisions for each content type.

Step 3: Verify
- Fill one sample weekly review with mock data format.

---

## Task 7: 14-day launch execution sequence

Objective: Sequence delivery so output ships in two weeks.

Day 1-2
- Finalize docs, channel map, content matrix.

Day 3-5
- Configure cron jobs and testing targets.

Day 6-10
- Go live with scheduled content + daily engagement handling.

Day 11-14
- Analyze metrics, tune frequency, refine CTA and templates.

---

## Execution commands (operator cheatsheet)

- Check gateway availability:
  - `curl -s http://127.0.0.1:18790/health || true`
- Check Ka manifest:
  - `curl -s http://127.0.0.1:8010/manifest | head`
- Refresh gitMaat context:
  - `python /home/suspect/.n8n/maatlangchain/scripts/query_gitmaat.py --out /home/suspect/.n8n/GITMAAT-CONTEXT.md`

---

## Definition of done

- Channel map and content matrix committed.
- Cron jobs active and verified.
- Governance and Tehuti Guard checks documented and tested.
- Heartbeat checklist live.
- Weekly metrics template in use.
- At least 7 days of consistent posting and engagement logs captured.
