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
| Antigravity / Chrome access | A2 manager + Antigravity | `reports/antigravity_chrome_ui_analysis_round_003.md` | Round 003 accepted Chrome UI over API route | Round 004 consumes A2 visual bridge packet |
| Google Ads readonly | A2 Chrome | `reports/google_ads_chrome_round_001.md` | Done 13 keyword rows | 下一輪只做 proposal，不改設定 |
| Meta Ads readonly | A2 Computer Use + Owner Chrome | `reports/meta_ads_owner_chrome_visual_bridge_round_004.md` | Correct Owner Chrome shows account `318634712`, business `215690449213844`, 13 campaign rows | Next packet: ad set targeting / destination URLs for B2B candidates |
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

## Round 002 Credential Routing — Superseded

- Antigravity credential SOP：`ANTIGRAVITY_CREDENTIAL_ROUTING_PROMPT.md`
- Antigravity command file：`commands/ROUND-002-antigravity-credential-routing.md`
- Expected outputs:
  - `reports/antigravity_wp_backend_round_002.md`
  - `reports/antigravity_google_ads_round_002.md`
  - `reports/antigravity_meta_ads_round_002.md`
- Status：superseded by Owner clarification. The active path is Owner Chrome UI evidence, not agent/API tokens.

## Round 003 Chrome UI Correction

- Antigravity prompt：`ANTIGRAVITY_CHROME_UI_PROMPT.md`
- Antigravity output：`reports/antigravity_chrome_ui_analysis_round_003.md`
- A2 review：`reports/a2_round_003_review.md`
- Status：partial pass. API-token route corrected, but Meta campaign reuse assumption needs recheck.

## Round 004 Meta Visual Bridge

- A2 corrected evidence：`reports/meta_ads_owner_chrome_visual_bridge_round_004.md`
- Screenshot evidence：`visual_evidence_round_004/meta_ads_owner_chrome_campaigns_round_004_cropped.png`
- Antigravity prompt：`ANTIGRAVITY_VISUAL_BRIDGE_META_PROMPT.md`
- Command file：`commands/ROUND-004-antigravity-visual-bridge-meta.md`
- Expected output：`reports/antigravity_visual_bridge_meta_round_004.md`
- Superseded mistake record：`reports/meta_ads_chrome_round_002_account_recheck.md`

## Round 005 Meta Ad Sets + Ads Visual Bridge

- A2 ad set / ad evidence：`reports/meta_ads_owner_chrome_adsets_ads_visual_bridge_round_005.md`
- Screenshot evidence：
  - `visual_evidence_round_004/meta_ads_owner_chrome_adsets_round_005_cropped.png`
  - `visual_evidence_round_004/meta_ads_owner_chrome_ads_round_006_cropped.png`
- Antigravity prompt：`ANTIGRAVITY_ADSETS_ADS_VISUAL_BRIDGE_PROMPT.md`
- Command file：`commands/ROUND-005-antigravity-adsets-ads-visual-bridge.md`
- Expected output：`reports/antigravity_adsets_ads_visual_bridge_round_005.md`
- Current confirmed B2B ad set seeds：`互動廣告組合 B 公關公司窗口`、`互動廣告組合 A 企業窗口`
- Still missing：詳細受眾、Advantage+、pixel/custom audience、destination URL

## Round 006 Meta Detail Visual Bridge

- A2 detail evidence：`reports/meta_ads_owner_chrome_detail_visual_bridge_round_006.md`
- Screenshot evidence：`visual_evidence_round_006/`
- Antigravity prompt：`ANTIGRAVITY_DETAIL_VISUAL_BRIDGE_PROMPT.md`
- Command file：`commands/ROUND-006-antigravity-detail-visual-bridge.md`
- Antigravity output：`reports/antigravity_detail_visual_bridge_round_006.md`
- A2 review：`reports/a2_round_006_review.md`
- Confirmed A seed：`互動廣告組合 A 企業窗口`
- A detail result：Meta `Instagram 或 Facebook` conversion location, page-like/follow objective, CTA `追蹤`; useful B2B audience/proof seed but not WordPress landing-page traffic.
- A audience result：台南市 +40 公里、30-60、所有性別、半導體/工程/金融條件 + 商業決策者/創辦人/產品經理等條件。
- B status：`互動廣告組合 B 公關公司窗口` remains running B2B seed with one `輪播圖卡`, but detail pane did not open; keep exact targeting/destination as `Needs UI Detail`.
- Safety：no publish/save/discard/toggle/field edit was executed.

## Round 007 Meta Landing Page Proposal

- Command file：`commands/ROUND-007-meta-landing-page-proposal.md`
- Output：`meta_landing_page_proposal_round_007.md`
- A2 review：`reports/a2_round_007_review.md`
- Goal：turn the verified Meta B2B audience seed into a proposal-only landing-page routing plan using existing live WordPress To B posts.
- Guardrail：do not edit Meta Ads, WordPress, Google Ads, Rank Math, or secrets.
- Status：accepted as proposal-only planning; next step is Owner review and optional read-only B detail pane reattempt.
