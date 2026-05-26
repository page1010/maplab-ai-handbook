# ROUND 001 — Antigravity / Chrome Access

角色：Google ecosystem execution assistant
管理方：A2
模式：只讀 access check

## Read First

1. `CURRENT_STATUS.md`
2. `handoff/tasks/T-A2A3-001-B.md`
3. `docs/a2a3/live-wordpress-audit.md`
4. `workbook/reviews/JOB-A2-B2B-CASE-ADS-20260526/review_request.md`
5. `workbook/reviews/JOB-A2-B2B-CASE-ADS-20260526/access_check.md`
6. `workbook/reviews/JOB-A2-B2B-CASE-ADS-20260526/execution_loop.md`

## Do

1. WordPress：只讀檢查 7 個 live post editor 或前台頁面。
2. Google Ads：只讀檢查 campaign / ad group / keyword / final URL / conversion goal 可見狀態。
3. Meta Ads：只讀檢查是否能進 Ads Manager campaign / ad set；確認 detailed targeting 或 Advantage+ suggestion UI 是否可見。

## Do Not

- 不發布 WordPress。
- 不按 Update / Publish / Save / Apply。
- 不改 Google Ads / Meta Ads 設定、預算、keyword、final URL、conversion goal。
- 不碰 Rank Math paid UI。

## Output

寫入或回報到：

`workbook/reviews/JOB-A2-B2B-CASE-ADS-20260526/reports/antigravity_round_001.md`

必含：

- 已驗證事實
- Google Ads keyword / ad group / final URL matrix
- 7 個 WordPress live post 狀態
- Meta Ads UI 可進入狀態
- 缺資料
- 下一步建議
