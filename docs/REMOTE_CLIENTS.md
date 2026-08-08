# Remote clients — join the Lab from another machine

Short checklist for **laptops, desktops, or orchestrators** (mobile later) that should behave like part of the same swarm—not an isolated chat client.

**Full contract:** [`docs/REMOTE_SWARM_SPEC.md`](REMOTE_SWARM_SPEC.md)  
**Session Index service (implementers):** [`docs/SESSION-INDEX-SERVICE.md`](SESSION-INDEX-SERVICE.md)  
**Tehuti Guard call sites:** [`docs/TEHUTI-GUARD-INTEGRATION-MATRIX.md`](TEHUTI-GUARD-INTEGRATION-MATRIX.md)  
**Connect + DB:** [`docs/GITMAAT-CONNECT.md`](GITMAAT-CONNECT.md)  
**LAN exposure:** [`CLAWD-MCP-ACCESS.md`](../CLAWD-MCP-ACCESS.md)

---

## Before you start

1. **Lab host** — hostname or LAN IP of the machine running Discovery and organs (example: `192.168.4.21` or `staydangerous`).
2. **Auth** — `KA_API_KEY` (or whatever organs require); never commit keys.
3. **Identity** — pick a stable **`agent_id`** and **`device_id`** for this machine (see spec).

---

## Steps

1. **Discovery** — `curl http://<lab-host>:8010/manifest` and note `organs.brain.endpoint`, `organs.memory.endpoint`, etc. Do not assume `localhost` unless this device **is** the server.
2. **Configure MCP / OpenAPI client** — base URL for Tehuti Core (often `:8014`) and Maat Memory (`:8022`) from manifest; send `Authorization: Bearer …` if required.
3. **Copy machine config** — from [`tehuti-config/swarm.config.example.yaml`](../tehuti-config/swarm.config.example.yaml) to local `swarm.config.yaml`; fill discovery URL, service URLs, and **`session_index.endpoint`** **from manifest** when exposed (otherwise leave disabled until the service exists).
4. **Behavior** — honor **Scout / Analyst / Archivist** (see [`AGENTS.md`](../AGENTS.md) and [`docs/SCOUT-ANALYST-ARCHIVIST.md`](SCOUT-ANALYST-ARCHIVIST.md)); Archivist outputs **structured** (JSON, tags, sources, timestamps).
5. **Memory** — use **gitMaat tools** for coordination and durable memory; **query when appropriate**; avoid duplicate unstructured dumps.
6. **Events** — as the runtime matures, emit **canonical event types** for task/memory/tool actions (see spec).
7. **Session index** — when the **Swarm Session Index** API exists, **register** on session start, **heartbeat**, **close** on completion; durable outcomes still go to **gitMaat**.

---

## What `AGENTS.md` does here

If this machine **opens the same git workspace**, it may load root [`AGENTS.md`](../AGENTS.md). If not (e.g. phone app, minimal client), replicate the **same norms** in your product config: roles, structured Archivist, discovery-first URLs, identity headers.

---

**Last updated:** 2026-04-08 (session index + guard layers in spec).
