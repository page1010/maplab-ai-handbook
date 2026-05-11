# A4 Source of Truth

Version: v1.1  
Owner: A1 / A4 coordination  
Updated: 2026-05-11

## Canonical facts

- Primary account: `mina` / `lb99104@gmail.com`
- Asset log: `MAPLAB_ASSET_LOG`
- Asset log sheet ID: `1nlxlMdaLdGEAmOjP70BYspRWqu_eYpsiRyZaujEZkYI`
- Asset log tab: `工作表1`
- Shared MAPLAB root folder: `1SLIMAtjN6XSCYUTXRPe2XrkAO7sT-B0l`
- Destination assets folder: `1yVggYKiTkBJe4kd8CPoM3U75km0nVuNy`
- Source takeout root: `1jNUnnXPYMEq3GLDiJNC1GFZjQWRvwcCz`
- Workbook dashboard: `workbook/dashboard.html`

## Verified source tree

The current Drive connector verified this path:

- `Takeout` folder: `1rJhCG3PJFntYk94YYysg0ggzjiKnCO60`
- `Google 相簿` folder: `18Y1vXHrlzp8Ot3TV2-qN02YPi3hBhgdk`
- Year folders under `Google 相簿`:
  - `2021 年的相片`
  - `2022 年的相片`
  - `2023 年的相片`
  - `2024 年的相片`
  - `2025 年的相片`
  - `2026 年的相片`

## What is source of truth

- The sheet is the index.
- The Drive tree is the source archive.
- The workbook produces plans, reports, and dashboards.
- No move should assume a folder ID that has not been verified in the current account.

## Interface verification — 2026-05-11

Read-only Google Drive / Sheets API check confirmed:

- `1SLIMAtjN6XSCYUTXRPe2XrkAO7sT-B0l` = `MAPLAB`
- `1yVggYKiTkBJe4kd8CPoM3U75km0nVuNy` = `MAPLAB_ASSETS`, parent = `MAPLAB`
- `1jNUnnXPYMEq3GLDiJNC1GFZjQWRvwcCz` = source `Google 相簿`
- `1nlxlMdaLdGEAmOjP70BYspRWqu_eYpsiRyZaujEZkYI` = `MAPLAB_ASSET_LOG`, tab `工作表1`, rowCount `36923`
- Old dashboard/root reference `1L0udpuXLy3vEbHmzBbaLqNVDut2FFpCe` returned Drive API 404 and must not be used by active scripts.

## Historical references

The repo contains older or conflicting folder IDs for `MAPLAB_ASSETS`.
Treat them as historical notes until the owner confirms the active destination root.

## Operating rule

- If the account cannot see the source file, do not fake the move.
- If the destination root is not verified, do not create a parallel archive.
- Preserve originals.
