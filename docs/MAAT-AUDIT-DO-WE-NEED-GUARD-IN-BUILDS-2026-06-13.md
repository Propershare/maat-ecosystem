# MAAT Audit - Do We Need Tehuti Guard In Our Builds?

**Date:** 2026-06-13  
**Auditor agent:** `cursor_staydangerous`  
**Question:** Should Tehuti Guard be part of every build, given that security is not the operator's constant focus?

## Verdict

Yes, but not as a full copied Guard inside every repository.

Every build should carry a **small local Guard layer**: deterministic checks for dangerous shell commands, sacred paths, package installs, and durable memory/config mutations. That layer must run offline and never depend on a network service.

The central Tehuti Guard service (`POST /decision` on `:8013`) should be a **called authority**, not copied into every repo. It is valuable for machine posture, Sentinel context, cross-repo audit, and product-grade governance, but only after its wire contract is stable and clients degrade safely when it is unavailable.

## Truth

The current lab already has part of the right pattern:

- `maat-runtime` has a local governance layer that blocks sacred paths and high-risk commands before a remote Guard call.
- Tehuti Guard's Python API has a clear nested `/decision` envelope.
- There is contract drift: at least one current client sends a flat `{ actor, action, resource }` request while the Python API expects `{ machine_id, actor: { id, role }, action: { kind, resource, risk } }`.
- The remote service has recently been advertised by Ka discovery while not listening on `:8013`.

So the need is real, but the current remote layer must become honest: either reachable and contract-compatible, or treated as optional/warn-only.

## Balance

Embedding the entire Guard codebase in every repo would create drift, duplicate maintenance, and false confidence. Calling only a central service would create a network dependency that can block work or silently fail open.

The balanced architecture is hybrid:

1. **Embedded thin layer:** a versioned SDK plus local deterministic rules in every build.
2. **Central authority:** Tehuti Guard API called for high-impact or ambiguous actions.
3. **Audit trail:** local append-only logs always, central governance events when available.

This gives protection even when offline, while still allowing the hosted Guard to become a monthly product.

## Order

The adoption order should be:

1. Standardize the `GUARD.md` and `maat.guard.json` templates in every build.
2. Standardize the Guard wire contract and make every client send the same envelope.
3. Package a thin TypeScript and Python Guard client.
4. Default remote Guard to `warn` while dogfooding; move to `enforce` only after uptime and contract tests are proven.
5. Run `tehuti-guard-serve` and Sentinel as managed services.
6. Build hosted audit, dashboards, policy packs, and fleet correlation as the monetized product surface.

## Justice

Do not claim central protection where no service is running. Do not make agents depend on a dead remote service. Do not copy the full Guard into each repo and call that product maturity.

The fair claim is:

> This build is protected by local Tehuti Guard rules and can optionally consult the central Tehuti Guard service for posture-aware decisions and audit.

## Product Judgment

This can be a monthly product, but the paid value is not the denylist itself. The paid value is:

- hosted decision API,
- audit retention,
- compliance-grade reports,
- maintained policy packs,
- cross-machine/fleet correlation,
- dashboard and alerts,
- customer-specific policy profiles.

The open/free layer should be the SDK and local templates. The subscription layer should be the hosted brain and audit/control plane.

## Recommendation

Adopt Tehuti Guard in every build as a **thin local SDK + config template**, and call the central service for higher-order decisions. Do not copy the whole implementation into every repo. Do not make the central service mandatory until it is stable.

This is the Maat-aligned path: real protection, no theater, no brittle dependency, and a credible route to a product.
