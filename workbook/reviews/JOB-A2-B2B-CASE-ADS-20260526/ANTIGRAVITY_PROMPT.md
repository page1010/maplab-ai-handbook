# ANTIGRAVITY PROMPT — MAPLAB A2 B2B Case Ads ROUND 001

你是 Antigravity，運行在 Google / Chrome ecosystem。
管理方是 A2。你的任務不是寫漂亮規劃，而是替 A2 做只讀 access check + matrix 回報，讓 A2 可以檢查並下下一輪指令。

## Working Directory

`/Users/pagemacmini/maplab-ai-handbook`

## Read First

1. `CURRENT_STATUS.md`
2. `handoff/tasks/T-A2A3-001-B.md`
3. `docs/a2a3/live-wordpress-audit.md`
4. `docs/a2a3/b2b-case-inventory.md`
5. `workbook/reviews/JOB-A2-B2B-CASE-ADS-20260526/review_request.md`
6. `workbook/reviews/JOB-A2-B2B-CASE-ADS-20260526/access_check.md`
7. `workbook/reviews/JOB-A2-B2B-CASE-ADS-20260526/execution_loop.md`
8. `workbook/reviews/JOB-A2-B2B-CASE-ADS-20260526/commands/ROUND-001-antigravity.md`
9. `workbook/reviews/JOB-A2-B2B-CASE-ADS-20260526/reports/a3_meta_round_001.md`

## Hard Rules

- Do not publish WordPress content.
- Do not click Update / Publish / Save / Apply.
- Do not modify Google Ads / Meta Ads settings, budget, keyword, final URL, search themes, conversion goals, audience, campaign, ad set, or ads.
- Do not touch Rank Math paid UI; Rank Math is unsubscribed and existing settings are frozen.
- Do not use 404 planned slugs.
- Do not read secrets, env files, passwords, cookies, local storage, profile stores, or API keys.
- Owner-provided photos are approved for public-case workflow; do not split public/internal/private buckets.

## Known Live URLs

Use these only:

- `https://www.maplabkitchen.com/corporate-catering-tainan/`
- `https://www.maplabkitchen.com/corporate-tea-party-desserts/`
- `https://www.maplabkitchen.com/tainan-corporate-opening-tea-catering/`
- `https://www.maplabkitchen.com/brand-esg-catering-service/`
- `https://www.maplabkitchen.com/press-conference-catering/`
- `https://www.maplabkitchen.com/vip-expo-catering-business-meeting/`
- `https://www.maplabkitchen.com/daxin-art-museum-opening-catering/`

Do not use these 404 slugs:

- `catering-corporate-tainan`
- `meeting-refreshment-catering-tainan`
- `opening-event-catering-tainan`
- `brand-event-catering`
- `school-event-catering-tainan`

## Tasks

### 1. WordPress Read-Only Check

Check the 7 live URLs above. If logged-in editor access is available, check the post editor or admin edit page only enough to record:

- page/post title
- slug
- status visible or not
- editor type / Elementor presence
- likely insertion point for case section
- any blocker

Do not save.

### 2. Google Ads Read-Only Check

Check Google Ads account `844-336-3178`, especially:

- campaigns
- ad groups
- keywords / PMax search themes if visible
- final URL column if visible
- conversion actions if visible without editing

Record a matrix:

- campaign
- ad group / asset group
- keyword/search theme
- match type if any
- status
- final URL if visible
- suggested landing page from `review_request.md`
- mismatch / missing data

Do not edit.

### 3. Meta Ads Read-Only Check

If Meta Ads Manager is accessible:

- confirm campaign/ad set layer is reachable
- confirm whether detailed targeting or Advantage+ audience suggestion UI is available
- confirm whether pixel / website custom audience / conversion event view is reachable

Do not create or edit campaigns/ad sets.

### 4. Output

Write a single Markdown report to:

`workbook/reviews/JOB-A2-B2B-CASE-ADS-20260526/reports/antigravity_round_001.md`

Required sections:

1. `已驗證事實`
2. `WordPress 7 URL Matrix`
3. `Google Ads Keyword / Final URL Matrix`
4. `Meta Ads UI Check`
5. `合理推論`
6. `缺資料`
7. `風險 / 不可做事項`
8. `給 A2 的下一輪指令建議`

If UI access fails, still write the report and include:

- tried what
- where it stopped
- why it cannot proceed
- what Owner can do in 5 minutes

## Finish

Return a short summary:

- file written
- systems checked
- blockers
- next best command for A2
