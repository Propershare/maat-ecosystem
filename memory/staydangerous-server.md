# StayDangerous Server (2026-02-25)

## Overview
- Root path: `/mnt/ai_backup/staydangerous1`.
- Primary config: `server.cfg` (powered by license `cfxk_1adOacfgRbwXmNvzdqSv4_2XI5UE`, txAdmin port 40120, `onesync` left to txAdmin, `oxmysql` pointing to `staydangerousqb`, QBCore framework, Zyke feature set, voice defaults using native audio, debug_mode off). Production log files: `server_output.log`, `server_manager.log`, `nohup.out`.
- Lightweight/test configs: `server_basic.cfg` and `server_minimal.cfg` share the license and core network settings but limit resources for testing purposes (basic gamemode + hardcap + session/spawn/map managers). Keep them in sync when tweaking production parameters.

## Custom Framework Flags
- Resource load order (critical dependencies):
  1. Core session/ spawn/ map managers + `basic-gamemode`, `hardcap`, `oxmysql`, `baseevent`, `ox_lib`, `qb-core`, `qs-textui`, `PolyZone`, `menuv`, `chat`, `thug-chat-v3`, `qb-target`, `cdev_lib`, `ps-els`.
  2. Player systems: `illenium-appearance`, `[apartments]`, `[multicharacter]`, `[inventory]`, `[smartphone-pro]`, `[drugs-creator]`, `pug-repojob`, `bt-producer`, `wais-studio`, `DLDebadgedStarter`, `[ak4yscripts]`, `[advancedgarages]`, `pma-voice`.
  3. Licensing/vehicle/communication: `bcs_licensemanager`, `bcs_driveschool`, `[Quasar]`, `[qb]`, `[Ak47]`, `[housing]`, `[Cdev]`, `zyke_lib`, `zyke_propaligner`, `zyke_status`, `zyke_sounds`, `zyke_consumables`.
  4. Jobs & standalone content: `[GangJobs]`, `[jobs&Businesses]`, `jim_bridge`, `jim-consumables`, `[defaultmaps]`, `molo_mosley`, `[maps]`, `[Vehicles]` and subpacks, `[RTX]`, `[rcore]`, `[AnimatedBannersCustomLogos]`, `[Playlolly]`, `d3MBA-lib`, `[Pug]`, `[17moveScripts]`, `[SIX]`, `[Misc]`, `[Ak47]`, `lc_utils`, `[clothing]`, `[wasabi]`, `[dirkscripts]`, `[Weapon]`, `montgomery_bat`, `kyros-weapon-pack-*`, `[toxic]`, `[molo_mosley]` (duplicate note – ensure no double loading). Certain vehicle packs (e.g., `primo`, `fugitive`) are explicitly replaced.
  5. Standalone utilities like `[standalone]/fivem_vehicle_image_creator/vehicle_image_creator` run last.
- Permissions: Many ACE groups defined (admin, god, vip) plus resource-level ACEs (`resource.qb-core`, `qbcore.god`, `resource.rcore_*`, `resource.ox_lib`, `group.admin` wide permissions). Keep ACE updates consistent with this file—no automatic rewrites.

## Monitoring & Optimization Hooks
- Watch logs: `server_output.log` for runtime errors, `server_manager.log` for TxAdmin operations, `nohup.out` for general stdout/stderr.
- Paid scripts: All resources under `resources/` marked `[Multi-]` or with custom names require tracking for licensing/optimization; use this memory as inventory (start by listing directories inside `resources/` and noting paid ones).
- Document notable custom configs (voice defaults, Ox primary colors, screenshot webhook, MySQL strings) so future config checks can compare values.
- Automation idea: Use `server_manager.sh` and `server_manager.log` to orchestrate restarts; plan to track last restart time and active script load states.

## Next Steps
1. Inventory `resources/` folders to tag paid scripts vs open-source ones and note vendor/version when available.
2. Build a checklist that reads `server.cfg` to ensure critical `setr` and `ensure` lines match our documented sequence before each restart.
3. Tail the key logs for anomalies and append noteworthy events to this memory (with timestamps) to build an optimization storyline.
4. Tie any AI tools (e.g., txAdmin dashboards, monitoring bots) into this workflow so future prompts get the entire picture.

## Upgrade workflow blueprint
- Create an `upgrade_pending/` drop folder where you can place new paid/custom scripts and config bundles; I’ll monitor that folder for changes and handle version rotation.
- The automation will validate dependencies (resource order, ACE groups, colors/config markers), move the unpacked folders into `resources/`, and ensure `server.cfg` and `permissions.cfg` carry over any manual edits (custom colors, voice defaults, etc.).
- Before each restart, run a pre-flight checklist (resource ensures, config diff, log sanity) so transitions remain smooth; if a change touches custom colors or config keys, flag it explicitly.
- I’ll log every upgrade action (who dropped the folder, which resources changed, results) so the history lives in memory for reference and optimization follow-ups.

### qs-advancedgarages upgrade log (2026-02-25)
- Backup: `/resources/[advancedgarages]/qs-advancedgarages.bak-20260225_215835`, `/resources/[advancedgarages]/[sql].bak-20260225_215835`, DB dump `backups/staydangerousqb-20260225_215835.sql` (staydangerousqb).
- Deployed Quasar v5.0.18 from the upgrade drop: moved the new `qs-advancedgarages`, added the `[shells]` helper bundle, and replaced the `[sql]` patch bundle.
- Added `web/build/assets/custom-brand.css` and included it in `web/build/index.html` so the UI reuses the StayDangerous red (#8F0000) while overriding the primary/danger CSS variables.
- Ran the provided `update.sql` to add `interior_type` to `player_garages`, then restarted the server through `server_manager.sh restart` so the resource reloads with minimal drift.
- Next steps: watch logs (especially `server_output.log`/`server_manager.log`) for `screenshot-basic`/webpack rebuild errors, verify the new landing UI still respects the branding overlays, and run the other Quasar drops one at a time after confirming each upgrade path.

### qs-inventory upgrade log (2026-02-26)
- Backups: `resources/[inventory]/qs-inventory.bak-20260226_005744`, `qs-shops.bak-20260226_005744`, `[dlc].bak-20260226_005800`, `[sql].bak-20260226_005800` plus the old directories in case a rollback is needed.
- Deployed the Quasar v3.7.17 inventory bundle (plus the updated `qs-shops` and `[dlc]` helpers) from the drop folder. This replaced the previous `qs-inventory`/`qs-shops` assets and the SQL bundle, matching the new version metadata.
- Added a `html/css/custom-brand.css` file and wired it into `html/ui.html` so the inventory UI now uses the StayDangerous crimson (#8F0000) gradients/shadows while leaving Quasar’s assets intact.
- Updated `server_manager.sh`’s update list so `qs-inventory` now reports 3.6.95 → 3.7.17 and `qs-advancedgarages` shows 4.0.44 → 5.0.18, matching the resources we just deployed.
- Restarted the server with `server_manager.sh restart` so the new inventory/shops resources load cleanly and the logs reflect the new version IDs.

### Startup stabilization (2026-02-26)
- Commented the `ensure [standalone]/fivem_vehicle_image_creator/vehicle_image_creator` line in `server.cfg` so the resource doesn’t repeatedly fail during boot; will bring it back once we have the pre-built assets.
- Renamed `/resources/[standalone]/screenshot-basic` to `screenshot-basic.disabled` (plus its `ensure` dependency comment) to stop the loop caused by the repeated `webpack`/`yarn` build failure; we can restore it once we precompile the bundle or swap in a compatible build.
- Restarted the server via `server_manager.sh restart`; ports 30120/40120 came up cleanly and the console no longer cycles while the dependent resources stay offline.
- Next step: build `screenshot-basic` artifacts in an Alpine-compatible environment or source pre-built output, then rename the folder back and re-add the `ensure` if we still need the functionality, while we keep an eye on the `yarn` warnings and `sb-handlingtuning` sandbox rejection.

### Screenshot build & stabilization (2026-02-26)
- Renamed `/resources/[standalone]/screenshot-basic` back into place and precompiled the server/client/UI bundles with webpack 4 by installing `yarn add -D webpack-cli@3.3.12` and running `NODE_OPTIONS=--openssl-legacy-provider ./node_modules/.bin/webpack --config server.config.js/client.config.js/ui.config.js`. The `dist/` folder now contains the compiled `server.js`, `client.js`, `ui.js`, and `ui.html`, so the resource no longer hits the `yarn`/`webpack` build error on startup.
- Added `ensure screenshot-basic` to `server.cfg` (while keeping the `vehicle image creator` ensure commented) so the resource loads automatically while the boat image system stays disabled per your request.
- Restarted the server with the new build: txAdmin and port 30120 are steady, and the console no longer loops from repeated `webpack` runs.

### Screenshot manifest cleanup (2026-02-26)
- Removed the `dependency/yarn`, `dependency/webpack`, and all `webpack_config` lines from `resources/[standalone]/screenshot-basic/fxmanifest.lua` so the resource simply loads the prebuilt `dist/` assets instead of trying to rebuild them on each boot.
- Restarted the server through `server_manager.sh restart` to confirm the `webpack`/`yarn` loop is gone; the console now stops printing repeated build failures while txAdmin/game ports remain online.

### qs-housing upgrade log (2026-02-26)
- Backed up the live housing resource to `resources/[housing]/qs-housing.bak-20260226_130807` and saved the new default configs as `config/*.new-version` so future merges can reference the latest value map while your working configs remain untouched.
- Deployed the extracted Quasar Store `qs-housing` v5.2.56 bundle from `/tmp/housing_upgrade/[housing]/qs-housing`, covering the refreshed `fxmanifest.lua`, new server modules (including `furnitureShop.lua`, `metakey.lua`, and the `/assetpacks` dependency), and the prebuilt `web/build` UI assets.
- Restored your existing `config/*.lua` files from the backup to preserve any custom tweaks/history, while keeping the new defaults in `.new-version` copies for future comparisons.
- Added the StayDangerous branding overlay (`web/build/assets/custom-brand.css`) and linked it inside `web/build/index.html` so the UI keeps the #8F0000 gradients/buildings like the other Quasar upgrades.
- SQL files from the upgrade are staged under `/tmp/housing_upgrade/[housing]/[sql]` (all_houses.sql, qb.sql, esx.sql, mirror_park.sql, etc.); please import whichever matches your economy once the new resource is live so the shells, furniture, and meta keys align with your database schema.
- Next steps: import the SQL patch, restart via `server_manager.sh restart`, monitor `server_output.log` for the new meta key/furniture modules, and reapply any delta between your `config/*.lua` and the `.new-version` defaults when a flow requires new fields.
