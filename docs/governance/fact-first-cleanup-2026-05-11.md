# Fact-First Cleanup — 2026-05-11

Owner instruction: let facts speak before deciding.

## Scope

This pass checked the active MAPLAB handbook repo, the stale Downloads copy, A4 asset locations, A2/A3 workbench state, live WordPress inventory, and OpenClaw/A6 governance docs.

## Facts Confirmed

### Repo truth

- Official repo: `/Users/pagemacmini/maplab-ai-handbook`
- Stale/non-git copy: `/Users/pagemacmini/Downloads/maplab-ai-handbook-main`
- Quarantined stale copy: `/Users/pagemacmini/Downloads/沒用的資料夾/maplab-ai-handbook-main-stale-20260511`
- The Downloads copy has `CURRENT_STATUS.md` v4.0 and no `pitfalls.md`; the official repo has `CURRENT_STATUS.md` v6.0 and `pitfalls.md`.
- The official repo already documents the Downloads-copy mistake in `pitfalls.md` and `docs/a2a3/workbench-integrity-report.md`.

### A4 asset truth

Read-only Google Drive / Sheets API verified:

- `MAPLAB`: `1SLIMAtjN6XSCYUTXRPe2XrkAO7sT-B0l`
- `MAPLAB_ASSETS`: `1yVggYKiTkBJe4kd8CPoM3U75km0nVuNy`, parent = `MAPLAB`
- Source `Google 相簿`: `1jNUnnXPYMEq3GLDiJNC1GFZjQWRvwcCz`
- `MAPLAB_ASSET_LOG`: `1nlxlMdaLdGEAmOjP70BYspRWqu_eYpsiRyZaujEZkYI`, tab `工作表1`, rowCount `36923`
- Old ID `1L0udpuXLy3vEbHmzBbaLqNVDut2FFpCe` returned Drive API 404 and is invalid for current operations.

### A4 move status

Local checkpoint:

- `workbook/outputs/2026-05-05/T-A4-photo-move/checkpoint.json`
- copied `36620`
- skipped `280`
- failed `22`
- next_index `36922`

Interpretation: the bulk copy run reached the end of the sheet, but the 22 failed rows still require a targeted audit before claiming A4 fully closed.

### WordPress truth

Live WP public REST verified on 2026-05-11:

- 6 published pages
- 57 published posts
- Planned local workbench slugs are not live WordPress objects.
- Existing intent owners include `corporate-catering-tainan`, `tainan-corporate-opening-tea-catering`, `brand-esg-catering-service`, `corporate-tea-party-desserts`, and `catering-one-year-old-party-tainan`.

## Decisions From Facts

1. Do not use the Downloads copy as a working directory.
2. Do not use old `MAPLAB_ASSETS` ID `1L0udpuXLy3vEbHmzBbaLqNVDut2FFpCe` in active scripts.
3. Do not create new WordPress slugs until live owner pages/posts are mapped.
4. Do not treat local preview/workbench output as published truth.
5. Do not move or delete original Drive photos; only copy/index and write reviewable logs.

## Files Updated In This Pass

- `tools/ai_workbook/photo_pipeline.py`
- `scripts/organize_photos_by_category.py`
- `docs/a4/source-of-truth.md`
- `docs/a4/drive-map.md`
- `docs/glossary.md`
- `skills/credentials/google-drive-api.md`
- `projects/maplab-pipeline.md`
- `projects/a2-asset-guide.md`
- `handoff/tasks/T-A4-001.md`
- `workbook/dashboard.html`
- `pitfalls.md`

## Files Quarantined

- Moved `/Users/pagemacmini/Downloads/maplab-ai-handbook-main` to `/Users/pagemacmini/Downloads/沒用的資料夾/maplab-ai-handbook-main-stale-20260511`
- Reason: it is not a git repo, had stale v4.0 status, no `pitfalls.md`, and previously caused A2/A3 workbench truth-source confusion.
- Safety: this was a move, not deletion; files remain recoverable from the quarantine folder.

## Next Cleanup Queue

1. Build an A4 failed-row audit for the 22 failed copies.
2. Build an A2/A3 live-owner map before more WordPress drafting.
3. Update OpenClaw/A6 memory to read this fact-first cleanup before dispatching A2/A4 tasks.
4. Add a small link/resource checker that fails if active docs/scripts reference a Drive ID that API cannot see.
