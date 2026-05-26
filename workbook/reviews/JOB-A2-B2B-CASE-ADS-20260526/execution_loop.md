# A2 Execution Loop — B2B Case + Ads Routing

日期：2026-05-26
Owner 指令：規劃好了就動起來；讓各角色回報、A2 檢查、下新指令、定時檢查，重複直到美好。

## Loop Contract

每輪固定做四件事：

1. Collect：收 Antigravity / A3 / A4 回報。
2. Inspect：A2 檢查是否有 live URL、廣告 final URL、素材 slot、缺資料、風險。
3. Command：A2 下下一輪具體指令。
4. Persist：更新本 job bundle、Task Card、必要時 `CURRENT_STATUS.md`，並 commit。

## Active Workstreams

| Workstream | Owner | Report path | Current state | Next check |
|---|---|---|---|---|
| Antigravity / Chrome access | A2 manager + Antigravity | `reports/antigravity_round_001.md` | Done public URL check; no logged-in cookie | A2 已用 Chrome 補 Google Ads / Meta readonly |
| Google Ads readonly | A2 Chrome | `reports/google_ads_chrome_round_001.md` | Done 13 keyword rows | 下一輪只做 proposal，不改設定 |
| Meta Ads readonly | A2 Chrome | `reports/meta_ads_chrome_round_001.md` | Done onboarding surface check | 等 Owner/A3 確認 business portfolio / ad account |
| Meta segmentation | A3 worker | `reports/a3_meta_round_001.md` | Done Round 001 | 保持 `Needs UI Check`，不硬寫 interest |
| Asset slots | A4 worker | `reports/a4_assets_round_001.md` + `asset_conversion_manifest_round_001.csv` | Done Round 001 | 下一輪照 manifest 處理 P1 圖，不上傳 |
| Case copy | A2 | `reports/a2_case_copy_round_001.md` | Done Round 001 | 等 Owner review 後才進 WordPress update plan |

## Round 001 Acceptance Criteria

Round 001 完成條件：

- Antigravity 回報 7 個 live WordPress post 的可編輯/前台狀態。
- Google Ads 回報 campaign / ad group / keyword / final URL 可見狀態，不改設定。
- Meta 回報每個 ad set 的 landing page、素材、Needs UI Check。
- A4 回報第一批 B2B 圖片 slot 與 WebP 命名。
- A2 寫出下一輪指令：哪些先寫文章，哪些先修 final URL，哪些素材先轉檔。

## Guardrails

- 不發布 WordPress。
- 不修改 Google Ads / Meta Ads 設定、預算、final URL。
- Rank Math 既有設定凍結。
- 不使用 404 planned slugs。
- Owner 提供的照片視為可進公開流程，不再拆 public/internal/private。
- 每輪都要區分：已驗證事實、合理推論、缺資料、下一步。

## Check Cadence

- 自動巡檢：每小時一次。
- Automation id：`a2-b2b-case-ads-loop-check`
- 巡檢任務只讀 repo 與報告檔。
- 若缺報告：產出 next command，不假裝完成。
- 若報告已齊：A2 檢查並產出下一輪指令。

## Round 001 Review Files

- Antigravity public URL report：`reports/antigravity_round_001.md`
- A2 Google Ads Chrome supplement：`reports/google_ads_chrome_round_001.md`
- A2 Meta Ads Chrome supplement：`reports/meta_ads_chrome_round_001.md`
- A2 review：`reports/a2_round_001_review.md`
- A2 case copy：`reports/a2_case_copy_round_001.md`
- A4 conversion manifest：`asset_conversion_manifest_round_001.csv`
