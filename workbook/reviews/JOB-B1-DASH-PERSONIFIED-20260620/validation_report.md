# JOB-B1-DASH-PERSONIFIED-20260620 validation report

## Scope

- Owner wanted the Guild Ops Board to feel like a personified game floor rather than a static card grid.
- Implemented v0.2 inside `workbook/dashboards/maplab-ops-game-dashboard.html`.
- Kept the original offline-ready single-file dashboard and existing department cards/drawer.
- Did not implement the registry generator or live status JSON from `T-B1-DASH-001`; those remain separate next steps.

## What changed

- Added a `Today Status` panel based on `CURRENT_STATUS.md` 2026-06-20 16:00:
  - 8h no new non-patrol commits.
  - `T-A8-001` and `T-A1-LEARNING-LOOP-001` remain over 48h.
  - A4 and B1 remain critical.
  - GCP billing remains red.
  - No new task-card inconsistency.
- Added an `OPS CONVENIENCE STORE` game-floor layer:
  - 6 room zones.
  - 9 clickable NPCs.
  - Manager/subordinate distinction.
  - Off-duty and caution states.
  - Dialogue panel with "how to ask this role" text.
  - Buttons to copy task wording, open the existing department drawer, and copy the manager summon prompt.

## Chrome readback

- URL: `file:///Users/pagemacmini/maplab-ai-handbook/workbook/dashboards/maplab-ops-game-dashboard.html`
- Title: `MAPLAB · Investment OS — Guild Ops Board`
- Counts:
  - NPCs: 9
  - Rooms: 6
  - Existing department cards: 21
- Click smoke:
  - Clicked `momentum-openclaw`.
  - Dialogue correctly said OpenClaw can collect browser/GPT evidence but cannot decide Top 3 or create trading logic.
  - Clicked `b4-patrol` in mobile readback.
  - Dialogue correctly marked B4 as off-duty and routed to backup.

## Screenshots

- Desktop first viewport: `/tmp/maplab_ops_game_dashboard_v02.png`
- Desktop game-floor dialogue: `/tmp/maplab_ops_game_dashboard_v02_dialogue.png`
- Mobile viewport: `/tmp/maplab_ops_game_dashboard_v02_mobile.png`

## Tests run

- `node` inline script syntax check: pass.
- `git diff --check -- workbook/dashboards/maplab-ops-game-dashboard.html`: pass.
- Chrome DevTools readback desktop: pass, no runtime/log events.
- Chrome DevTools readback mobile width 390: pass, body width 390, no horizontal overflow.

## Remaining work

- Connect `T-B1-DASH-001` generator and `ops_board_status.json` in a later pass.
- Expand all 21 departments into full NPC placement if Owner likes this direction.
- Replace emoji sprites with a consistent pixel-art asset set if the prototype is approved.
