# T-A2-006 — Ads / SEO / WordPress Patrol

建立：2026-05-29
負責：A2 / A1 governance
狀態：🟢 ACTIVE

## Owner Request

新增 A 部門 A2 的廣告、SEO 策略、WordPress 狀態定時巡查。A2 被召喚後要先回答品牌價值、品牌語氣、品牌顏色、網頁狀態，確認記憶，並把 MAPLAB 與 Investment OS 的企業文化整合共用且嚴格遵守。

## Scope

- 建立 A2 巡查 prompt / project doc。
- 更新 Chrome Extension A2 module，讓召喚時帶入 Ads / SEO / WordPress patrol。
- 建立 Codex automation 定時巡查。
- 只允許 safe repo/file-only changes 與 read-only evidence；外部發布或廣告設定需要 Owner approval。

## Current State — 2026-05-29

- `projects/a2-ads-seo-wordpress-patrol.md` 已建立。
- `recalls/A2_recall.md` 已加入品牌記憶確認與 T-A2-006 patrol 入口。
- `tools/ai_workbook/build_extension_task_modules.py` 已更新，A2 module role name 為 `Ads SEO WordPress Patrol`。
- `chrome-extension/task-modules/A2.json` 已重建。
- Codex automation `a2-ads-seo-wordpress-patrol` 已建立並 ACTIVE。
- Schedule: `FREQ=WEEKLY;BYDAY=MO;BYHOUR=9;BYMINUTE=0;BYSECOND=0`

## System Evolution — 2026-06-09

Owner 修正第二層自動化定義：正式 WordPress / Google Ads / Meta Ads / Rank Math
變更不是「不能自動跑」，而是必須先自動跑到 approval-ready plan。A2/A3/A4
要把計畫、原因、預期效果、影響範圍、風險、rollback、驗收方式整理好，讓
Owner 可以批准、提問、退回或縮小範圍。

新增協議：`projects/a2a3a4-approval-ready-automation.md`
Implementation commit：`4988747`

狀態定義：

- `proposal_done`：已產出 `owner_approval_card.md`，Owner 可直接批准或提問。
- `execution_done`：Owner 已批准精確範圍，agent 已執行、驗收、回寫 task card 並 commit。

沒有 `owner_approval_card.md` 的巡查，不算跑到可決策狀態。

## Startup Requirements

A2 必須先回答：

1. MAPLAB 品牌價值。
2. MAPLAB 品牌語氣。
3. 品牌顏色/視覺規範來源。
4. WordPress live URL / draft / Ads 狀態來源。
5. MAPLAB 與 Investment OS 共用文化：證據分層、風險邊界、交接紀律。

## Output Contract

預設寫到 `workbook/reviews/JOB-A2-ADS-SEO-WP-PATROL-YYYYMMDD/`：

- `ads_seo_wordpress_patrol.md`
- `brand_memory_check.md`
- `wordpress_status_matrix.md`
- `ads_landing_alignment.md`
- `safe_fix_log.md`
- `review_request.md`

若需要 A2/A3/A4 合作形成正式變更 proposal，改寫到：

```text
workbook/reviews/JOB-A2A3A4-APPROVAL-READY-YYYYMMDD/
```

必要輸出：

- `brand_memory_check.md`
- `a4_asset_manifest.md`
- `a2_seo_wordpress_plan.md`
- `a3_ads_strategy_plan.md`
- `owner_approval_card.md`
- `integration_review.md`

## High-Risk Actions

需要 Owner/A1 批准：

- 發布 WordPress 或改已發布內容。
- 改 Google Ads / Meta Ads 預算、投放、受眾、開關、付款。
- 讀 secrets、API keys、cookies。
- 修改 Rank Math 付費/退訂設定。

## Patrol Run — 2026-06-15 大臺南會展中心 SEO + Ads

Owner 召喚 A2 針對「大臺南會展中心外燴 / 茶點」做 SEO、Google Ads、WordPress 實例結合規劃。

本輪輸出：

- Review bundle: `workbook/reviews/JOB-A2A3A4-APPROVAL-READY-20260615-ICCTAINAN/`
- Status: `proposal_done`
- Owner approval card: `workbook/reviews/JOB-A2A3A4-APPROVAL-READY-20260615-ICCTAINAN/owner_approval_card.md`
- Drive folder metadata confirmed: `1wTu2cfZVSUMwSb0avEhSAd6sdVZZa2pT`
- Drive folder title: `0612大台南會展中心-工研院在宅醫療科技推動計畫跨部會工作小組會議`
- Direct children listed: 22 media files（11 JPG / 3 HEIC / 6 MP4 / 2 MOV）

本輪結論：

- 「大臺南會展中心外燴 / 茶點」適合先做場地型 SEO draft，再以小額 Google Search exact/phrase test 守住高意圖字。
- Google Ads 不應先重壓泛字；先用場地字與活動情境字，並以便當、團膳、便宜、交通、停車、門票、場租等否定字降低錯市場流量。
- Meta 不搶關鍵字，先做「MAPLAB = 台南會展中心企業茶點 / 品牌接待」的視覺記憶與再行銷 proposal。
- 第一個建議 approval 是 `A2-SEO-ICCTN-001`：只建立 WordPress 未發布草稿，slug `icc-tainan-catering`，不發布。

本輪未做：

- 未發布 WordPress。
- 未上傳媒體。
- 未改 Google Ads / Meta Ads。
- 未動 Rank Math / GTM / Pixel / 預算 / 開關。
- 未讀 secrets、cookies、`.env`。

## Resume Prompt

我是 A2 Ads / SEO / WordPress Patrol。請先讀 `CURRENT_STATUS.md`、`pitfalls.md`、`handoff/tasks/T-A2-006-ads-seo-wordpress-patrol.md`、`projects/a2-ads-seo-wordpress-patrol.md`、`projects/a2a3a4-approval-ready-automation.md`、`projects/seo-ads-agent.md`、`skills/brand-voice-guide.md`、`skills/maplab-visual-spec.md`。

若接續 2026-06-15 大臺南會展中心任務，接著讀：

1. `workbook/reviews/JOB-A2A3A4-APPROVAL-READY-20260615-ICCTAINAN/README.md`
2. `workbook/reviews/JOB-A2A3A4-APPROVAL-READY-20260615-ICCTAINAN/owner_approval_card.md`
3. `workbook/reviews/JOB-A2A3A4-APPROVAL-READY-20260615-ICCTAINAN/a4_asset_manifest.md`
4. `workbook/reviews/JOB-A2A3A4-APPROVAL-READY-20260615-ICCTAINAN/a2_seo_wordpress_plan.md`
5. `workbook/reviews/JOB-A2A3A4-APPROVAL-READY-20260615-ICCTAINAN/a3_ads_strategy_plan.md`
6. `workbook/reviews/JOB-A2A3A4-APPROVAL-READY-20260615-ICCTAINAN/integration_review.md`

目前狀態：proposal_done，尚未外部執行。第一個建議 approval 是 `A2-SEO-ICCTN-001`：只建立 WordPress 未發布草稿 `icc-tainan-catering`，不發布。未經 Owner/A1 精確批准，不發布、不改 Ads、不改 GTM/Pixel/Rank Math、不動預算或開關。
