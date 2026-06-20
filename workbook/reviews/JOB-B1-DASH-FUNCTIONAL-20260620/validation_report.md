# JOB-B1-DASH-FUNCTIONAL-20260620 Validation Report

## Scope

Owner asked to stop spending effort on pixel-style UI polish and make the Guild Ops Board functionally complete.

This run updated:

- `workbook/dashboards/maplab-ops-game-dashboard.html`
- `handoff/tasks/T-B1-DASH-001.md`
- `CURRENT_STATUS.md`
- `workbook/owner_requirements_panel.md`

## What Changed

- Added `Role Dispatch Console` below the personified ops floor.
- Kept the v0.2 visual floor as a fast entry point, but made the functional layer cover all 21 departments.
- Added a task textarea that routes by simple keyword matching.
- Added top route suggestions and a full 21-role roster.
- Added a generated dispatch prompt that says, in plain language:
  - find the department manager first;
  - if the manager is off-duty, use workers/backups only for evidence or drafts;
  - workers cannot make final calls;
  - do not place real orders, invent trading logic, or read sensitive credentials.

## Verification

### Static

```text
inline script syntax pass
```

### Browser Readback

Chrome connector bootstrap failed at the local tool layer before page control with:

```text
node_repl/js: codex/sandbox-state-meta: missing field sandboxPolicy
```

Fallback used a temporary headless Google Chrome profile with Chrome DevTools Protocol. It did not use the Owner's live Chrome profile, login state, external sites, or secrets.

Readback result:

```json
{
  "title": "MAPLAB · Investment OS — Guild Ops Board",
  "cards": 21,
  "visualNpcs": 9,
  "rosterRoles": 21,
  "routeButtons": 5,
  "promptHasNoTradeBoundary": true,
  "promptHasManagerRule": true,
  "errors": [],
  "desktop": {
    "scrollWidth": 1425,
    "innerWidth": 1440
  },
  "mobile": {
    "innerWidth": 390,
    "scrollWidth": 390,
    "hasHorizontalOverflow": false,
    "rosterRoles": 21,
    "promptVisible": true,
    "errors": []
  }
}
```

Interaction checks:

```text
Input: 我覺得實單查詢已經修好了，請檢查紅燈能不能關掉並確認只讀不送單
Top suggestion: IOS-INVENTORY · 庫存審查經理
Prompt owner: IOS-INVENTORY · 庫存審查經理
B4 selected: prompt includes 經理未上班
B4 selected: prompt includes 不能替經理做最終判斷
```

Screenshots:

- `/tmp/maplab_ops_game_dashboard_v03.png`
- `/tmp/maplab_ops_game_dashboard_v03_mobile.png`

## Not In Scope

- Did not build `tools/ai_workbook/build_ops_board.py`.
- Did not build `ops_board_status.json` or live status probes.
- Did not change Investment OS runtime, broker, Telegram sending, real orders, or sensitive credentials.

## Resume Prompt

You are B1/Codex in `/Users/pagemacmini/maplab-ai-handbook`. Continue `T-B1-DASH-001`.
Read `CURRENT_STATUS.md`, `pitfalls.md`, and `handoff/tasks/T-B1-DASH-001.md`.
v0.3 functional role dispatch is complete in `workbook/dashboards/maplab-ops-game-dashboard.html`.
Do not redo pixel UI polish. Next unfinished items are #1 registry generator and #2 optional live status JSON.
Keep dashboard offline-ready. Generator must only replace the `D[]` marker region and preserve curated persona/flow/ladder/crew overlays.
