# Discord Paywall + Whitelist — Architecture Draft

**Owner:** Suspect (OG_Suspect813)
**Target server:** StayDangerousRP — Purple World
**Drafted:** 2026-06-11
**Status:** DRAFT — for review before any channel/role edits

---

## Goal (one sentence)

Convert StayDangerousRP from an open RP Discord into a **subscription-gated whitelist** where paying members get a private trading lane and curated RP channels, with everything else (lounge, status, announcements) staying public so new players can still discover the server.

---

## Decisions to make before we build

These four answers determine the whole map. None of them are blockers for drafting, but the build script can't run until they're set.

### 1. What currency is the subscription?

| Option | How it works | Pros | Cons |
|---|---|---|---|
| **A. Discord native Subscriptions** (real money via App Directory / Paid Memberships in a Community server, or a Premium App SKU) | Discord handles billing, role auto-assigned via `MONETIZATION_*` events or a webhook | Cleanest, least code, trust signal | Requires Community + Monetization enabled, role must be a "subscription" role tied to a SKU; takes 1-3 days for Discord to approve monetization for new apps |
| **B. Bot-managed billing** (Raku collects $ via Stripe/CashApp/PayPal, manually or via a `/subscribe` flow) | Full control, any payment provider, can tie to in-game currency | No platform dependency, can be combined with in-game bank | We're the merchant of record; chargebacks/refund handling is on us; need a small DB of subscribers |
| **C. In-game currency only** (e.g. 100k from `/bank` → unlocks Discord role) | No real money movement; role tied to a QBCore bank tier | Feels RP-native, no tax | Doesn't actually pay the bills; easy to grind or share |

**Recommendation for the first cut:** **B (Stripe-backed, bot-mediated)**, with the door open to **A** later once monetization is approved. Reason: we control the SKU list, we can offer multiple tiers (basic / trader / OG), and the role-mapping logic lives in code we own (Raku + a thin DB table). If A becomes available, it's a one-line change to which provider fires the role-assign event.

### 2. Tiers

Suggested three-tier menu — adjust numbers freely:

| Tier | Price | Discord role | What it unlocks |
|---|---|---|---|
| **Prospect** | free | `@Member` (auto via Screening) | `#lounge`, `#server-status`, `#announcements`, read-only `#lore-canon` |
| **Trader** | $9.99 / mo | `@Trader` | Prospect + `#trading-floor` (private), `#rp-general`, `#looking-for-group` |
| **OG** | $24.99 / mo | `@OG` | Trader + `#og-lounge`, early access to lore drops, priority in queue, custom emoji in `#rp-general` |

If you want a single tier, drop Trader and the gate becomes binary: free vs. paid. Cleaner, simpler, fewer edge cases for the first month.

### 3. Whitelist gate style

Three real options, not theoretical:

| Style | Mechanism | Friction | Best for |
|---|---|---|---|
| **Membership Screening** (built-in) | New joiners get a server-specific screening form (Discord-supplied). Their answers go to a mod channel. Mod approves → server role granted. No payment. | Low — built in, zero cost, zero code | Pure whitelist without paywall |
| **Paid Subscription** (built-in) | Tied to a Discord SKU. Auto role on first paid cycle, auto-strip on lapse. | Medium — needs monetization approval | Pure paywall, simplest |
| **Hybrid: Screening + Subscription** | Screening is the front door (so we control who even *sees* the offer). Subscription is the second door (so we get paid). | Highest — two-step | Premium clubs that want taste + payment |

**Recommendation:** **Hybrid.** Screening keeps the riffraff out *before* they ever see a price. Subscription is the second hop. Raku handles both: screening answers → staff review → approve/deny; subscription webhook → grant/strip Trader or OG role.

### 4. What "private trading" means for RP

This is the one I most need your call on:

- **(a) Out-of-character trading** — real-money commerce for in-game items/cash/accounts. Discord is the marketplace, FiveM is the delivery. This is what most "private trading" subs actually are.
- **(b) In-character black-market** — buyers/sellers stay in their characters, talk "IRL" prices but the goods move in-game. More immersive, more risk of ToS grey areas.
- **(c) Whitelisted faction business** — only the named Purple World factions (Ballas, Vagos, etc.) get a private room for their own RPers. No money exchanged in Discord; the room is just a gated hangout for canon characters.

These are not mutually exclusive. Most paid RP servers run (a) for real revenue and (c) as a flavor channel. (b) is the one that attracts moderation pain.

---

## Proposed channel map (proposal)

Mark each channel: 🟢 keep, 🟡 merge, 🔴 delete, 🆕 new.

### Public — visible to everyone (including non-members)

| Channel | Status | Who can post | Notes |
|---|---|---|---|
| `#welcome` | 🆕 new | staff only (read-only for joiners) | Server Guide + screening link pinned |
| `#server-status` | 🟢 keep | bot only | txAdmin status embed |
| `#announcements` | 🟢 keep (rename from `#server-announce`) | staff only | Mirror of in-game announce |
| `#lounge` | 🟢 keep | everyone | General hangout, the "see what we're about" channel |
| `#lore-canon` | 🟢 keep | staff only writes, everyone reads | The Pitch: this is what you get if you subscribe |

### Member-only (Screening passed, no payment)

| Channel | Status | Who can post | Notes |
|---|---|---|---|
| `#rules-and-conduct` | 🆕 new | staff only | One pinned message, no chatter |
| `#looking-for-group` | 🆕 new | Member+ | Reduce DM spam, build the queue |
| `#general-rp` | 🆕 new | Member+ | The open RP floor, screening is the gate |

### Paid-only (Trader or OG)

| Channel | Status | Who can post | Notes |
|---|---|---|---|
| `#trading-floor` | 🆕 new (private) | Trader+, log-only for staff | The actual paid lane. Thread per deal: `[WTS] / [WTB] / [WTT]`. Auto-close after 48h. **All deal messages get DM-notified to mod team.** |
| `#rp-private` | 🆕 new (private) | Trader+ | Whitelisted RP, smaller pool, higher quality bar |
| `#content-queue` | 🟡 merge into `#trading-floor` as a thread? | Trader+ | Currently a draft channel; needs a decision — see note below |

### OG-only

| Channel | Status | Who can post | Notes |
|---|---|---|---|
| `#og-lounge` | 🆕 new (private) | OG | Patron tier, casual |
| `#og-lore-drops` | 🆕 new (private) | OG | Early access to new canon entries |

### Staff-only (no change)

| Channel | Status | Who can post | Notes |
|---|---|---|---|
| `#mod-chat` | 🟢 keep | Mod+ | Internal |
| `#fivem-admin` | 🟢 keep | Admin+ | Existing ops |
| `#bot-audit` | 🟢 keep | bot only | Already wired in Raku |
| `#screening-review` | 🆕 new | Mod+ | Output of Membership Screening — approve/deny here |
| `#payment-audit` | 🆕 new | Owner + bot | Subscription events, refunds, disputes |

### Channels to retire

| Channel | Why |
|---|---|
| `#server-announce` | Renamed to `#announcements`, fewer characters |
| `#content-queue` (if not merged) | Nobody's using it as a queue; if we're killing it, the content commands can post direct to `#content-published` after `/content publish` |
| `#content-published` | 🟡 repurpose: anyone with Member+ can read; only staff post |
| Anything else we don't actively use in 7 days | Audit at the end of week 1, then prune |

---

## Role stack

```
@everyone
   ↓ screening pass
@Member
   ↓ Trader subscription
@Trader
   ↓ OG subscription
@OG
   ↓ staff appointments (separate, never tied to payment)
@Mod
@Admin
@ServerOwner   ← bound to DISCORD_OWNER_USER_ID in .env, can't be self-issued
```

**Critical rule:** subscription roles (`@Trader`, `@OG`) are managed **only** by the billing webhook. Staff can never `/role add @Trader` by hand. Manual override goes through a logged `/grant` command that auto-expires in 24h and posts to `#bot-audit`.

---

## What Raku has to do (delta from current skill)

This is the build list, ordered:

1. **Membership Screening handler** — listen for `GUILD_MEMBER_UPDATE` / screening completion, post to `#screening-review`, accept ✅/❌ reactions or `/approve @user` slash command.
2. **Subscription webhook receiver** — small Flask/FastAPI sidecar (or a `aiohttp.web` route in the existing Raku process) on `127.0.0.1:8015`. Receives Stripe events (`customer.subscription.created/updated/deleted`), maps Stripe customer → Discord user ID, assigns/strips `@Trader` or `@OG`. Sends a thank-you DM with the new private channel links.
3. **`/subscribe` slash command** — generates a Stripe Checkout link tied to the user's Discord ID. Free trial of 3 days on first subscribe, no card-on-file for the trial (Stripe supports this with `trial_period_days`).
4. **`/subscription status`** — user-only, shows their current tier, renewal date, link to manage billing.
5. **`/content publish`** — admin command to move a draft from a temp thread into `#content-published` (keeps the queue concept but inside threads).
6. **`#trading-floor` thread discipline** — bot watches messages in the channel; anything starting with `[WTS] / [WTB] / [WTT]` gets auto-threaded and a deal-card embed. Thread is auto-archived after 48h. Deal count → `#payment-audit` daily digest.
7. **`#welcome` Server Guide** — populate via Discord's built-in onboarding flow. Three steps: Read the rules → Tell us about your character → Get screened.

---

## Permissions matrix (final shape)

| Role | `#trading-floor` | `#rp-private` | `#og-lounge` | `#screening-review` | `#payment-audit` | `#fivem-admin` |
|---|---|---|---|---|---|---|
| @everyone | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| @Member | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| @Trader | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| @OG | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| @Mod | ✅ (mod) | ✅ (mod) | ✅ (mod) | ✅ | ❌ | ❌ |
| @Admin | ✅ (mod) | ✅ (mod) | ✅ (mod) | ✅ | ❌ | ✅ |
| @ServerOwner | ✅ (mod) | ✅ (mod) | ✅ (mod) | ✅ | ✅ | ✅ |

(Mod = can read + delete + slowmode, not post in-character. Owner can post anywhere.)

---

## Build phases

| Phase | What ships | What I need from you | ETA after sign-off |
|---|---|---|---|
| **0. Decisions** | This doc, signed off | The 4 answers above | — |
| **1. Channel surgery** | Create new channels, archive unused, set up Server Guide | Go-ahead to do destructive Discord ops (one-time, fully reversible by us in dev portal) | 1 day |
| **2. Screening** | Raku screening handler + `#screening-review` + Server Guide content | Rules text, screening questions | 2 days |
| **3. Billing core** | Stripe Checkout link, webhook receiver, role mapping | Stripe account (test mode first), product/price IDs | 3 days |
| **4. Trading lane** | `#trading-floor`, deal-card embeds, 48h auto-archive, mod DM | Sample WTS/WTB format you want enforced | 2 days |
| **5. Polish** | `/subscription status`, payment DM, `#payment-audit` digest | — | 1 day |

Realistic ship for the full picture: **~2 weeks** of focused work, in parallel with FiveM ops staying live.

---

## Risks I'm flagging up front

1. **Discord ToS on monetization** — Discord allows real-money subs for digital goods/services within reason, but they don't love marketplaces *inside* Discord. If `#trading-floor` becomes "buy in-game cash for real cash," that's a Tax/ToS question I want you to think about before we go live. *Not a block, but a "be aware."*
2. **Chargebacks** — if we go Stripe, expect 1-3% chargeback rate in the first quarter. Budget a dispute handling routine into `#payment-audit` from day one.
3. **Role loss on subscription lapse** — the standard flow is "strip the role at period end." We can soften this with a 3-day grace, but be aware: when a Trader lapses, they lose access to `#trading-floor` *immediately* on grace end. Decide if we want a 7-day read-only grace, or hard cut.
4. **Screening abuse** — bots will burn through your screening queue. Need a captcha or a "must wait 24h after join before applying" gate. Raku can do the second one trivially.

---

## Open questions for you

- Tier prices — are $9.99 / $24.99 right, or do you want different numbers?
- Do you want a one-time "lifetime" tier alongside the monthly? (Implementation: still a Stripe subscription with `trial_period_days: 36500` and a webhook that hard-binds the role — but cheap to build.)
- "Trading" — is this real-money-for-in-game, or pure RP flavor with no real money changing hands? This single question determines whether we need Stripe at all.
- Are you okay with me running the destructive channel ops (archive, rename) from your account via Raku, or do you want to do them in the Discord client yourself and tell me when they're done?

---

*Drafted by Tehuti on 2026-06-11. Will not be applied to the guild until you sign off on the four decisions at the top.*
