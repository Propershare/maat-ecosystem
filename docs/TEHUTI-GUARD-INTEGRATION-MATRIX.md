# Tehuti Guard — integration matrix

**Library:** [`../tehuti-guard/`](../tehuti-guard/) (`enforceLDAPPolicy`, `isResourceAccessible`, LDAP → `inner-ring` | `middle-ring` | `outer-ring`).  
**Stack context:** [`REMOTE_SWARM_SPEC.md`](REMOTE_SWARM_SPEC.md) (presence → Guard → Archivist).  
**Session presence (separate):** [`SESSION-INDEX-SERVICE.md`](SESSION-INDEX-SERVICE.md).

Tehuti Guard answers: **given identity + action + resource path, allow or deny?**  
It does **not** answer session collision, summary quality, or “who is online” — use Session Index + Analyst + events.

---

## Call surfaces (wire Guard **before** execution)

| Surface | Guard `action` | Typical `resource` (path or namespace) | Notes |
|---------|----------------|----------------------------------------|--------|
| **File read / write** | `read` / `write` | Repo-relative path (e.g. `jarvis/maat-graphs/…`) | Pair with `isResourceAccessible`; inner ring read-only. |
| **Config edits** | `write` | Path to file or config key namespace | Treat secrets and canon paths as high ring sensitivity. |
| **Memory writes** (gitMaat, RAG ingest, structured store) | `write` | Logical store id + optional path/tag | Same as files if writes map to disk; else namespace in policy extension. |
| **MCP / tool execution** | `execute` | Tool id + arguments-derived resource if mutating | Map tool to ring (e.g. deploy tools → outer; canon editors → deny default). |
| **Shell / deploy / package scripts** | `execute` | Working directory or script path | Often outer-ring-only unless explicitly allowlisted. |
| **PR / patch / proposal** (scholarship flow) | `propose` | Target path for change | Middle ring: propose yes, direct write no. |

---

## Minimal decision flow (pseudocode)

1. Resolve **LDAP groups** (or synthetic groups for agents) → `MaatRole`.
2. If policy is path-based: `isResourceAccessible(role, resource)` — fast path fail.
3. `enforceLDAPPolicy({ action, resource, user }, ldapUser)` → `allowed`, `reason`.
4. If denied: emit **event** (e.g. `tool.denied` / `policy.evaluated`) and **do not** run tool or write.
5. If allowed: run operation; then **Archivist / gitMaat** for durable outcome.

---

## Expectations

- Guard **only runs where integrated** — if a code path skips it, that path is ungoverned.
- **Session Index** does not replace Guard; register presence separately from permission checks.
- Extend **`THREE_RING_GOVERNANCE.resources`** in [`tehuti-guard/src/three-ring.ts`](../tehuti-guard/src/three-ring.ts) when new trees need different tiers.

**Last updated:** 2026-04-08
