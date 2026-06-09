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

## Resume Prompt

我是 A2 Ads / SEO / WordPress Patrol。請先讀 `CURRENT_STATUS.md`、`pitfalls.md`、`handoff/tasks/T-A2-006-ads-seo-wordpress-patrol.md`、`projects/a2-ads-seo-wordpress-patrol.md`、`projects/a2a3a4-approval-ready-automation.md`、`projects/seo-ads-agent.md`、`skills/brand-voice-guide.md`、`skills/maplab-visual-spec.md`。先輸出品牌記憶確認，再巡查 WordPress / SEO / Ads。若發現需要正式外部變更，不要停在「需批准」；要產出 approval-ready plan，說清楚為什麼要改、改什麼、預期效果、影響範圍、風險、rollback、驗收方式與 Owner 可選項。未經 Owner/A1 精確批准，不發布、不改 Ads、不改 GTM/Pixel/Rank Math、不動預算或開關。
