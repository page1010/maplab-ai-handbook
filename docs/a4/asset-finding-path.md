# A4 Asset Finding Path

Updated: 2026-05-12

## Purpose

Give A2/A3/A6 a fact-first path for finding usable MAPLAB photos without guessing.

The first reliable key is not image recognition. The first reliable key is:

```text
photo date
→ quote sheet date
→ TimeTree catering event
→ ASSET_LOG category/SEO text
→ Drive source file
→ visual QA
```

## Canonical Inputs

- ASSET_LOG: `1nlxlMdaLdGEAmOjP70BYspRWqu_eYpsiRyZaujEZkYI`
- ASSET_LOG tab: `工作表1`
- Source photo tree: `Takeout/Google 相簿/2025 年的相片`
- Local quote sheets: `~/Library/CloudStorage/GoogleDrive-lb99104@gmail.com/我的雲端硬碟/外燴 訂單/2025外燴訂單`
- TimeTree lookup: `data/timetree_events_2022_2026.json`
- Destination assets root: `MAPLAB_ASSETS/2025/catering/...`

## CLI

Find high-confidence 2025 matches:

```bash
python3 tools/ai_workbook/cli.py asset-case-match --year 2025 --limit 120
```

Check one date:

```bash
python3 tools/ai_workbook/cli.py asset-case-match --year 2025 --limit 25 --date 2025-02-19
```

Output:

- `workbook/outputs/YYYY-MM-DD/T-A4-2025-asset-case-match/case_match_report.json`
- `workbook/outputs/YYYY-MM-DD/T-A4-2025-asset-case-match/case_match_report.md`

## Confirmed Seed Case

The first confirmed case is stored at:

- `workbook/outputs/2026-05-12/T-A4-2025-asset-link-proof/confirmed_combo.md`

Summary:

- Date: `2025-02-19`
- Scenario: B2B office / company catering
- TimeTree: company catering event on the same date
- Quote sheet: `2025 2 19 900 15人.gsheet`
- Asset rows: `27133`, `27135`
- Suggested public-safe case name: `亞綸科技開春聚餐茶點外燴`

## Rules

- Do not trust image recognition as the primary key.
- Do not publish private contact details, addresses, internal price, or internal headcount.
- Do not delete or move source photos.
- Copy only after a case match has date + quote sheet + ASSET_LOG + visual QA.
- Public copy should use scene names, not internal quote-sheet titles.
