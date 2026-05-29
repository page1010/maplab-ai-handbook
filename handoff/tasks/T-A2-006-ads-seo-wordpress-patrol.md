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

## High-Risk Actions

需要 Owner/A1 批准：

- 發布 WordPress 或改已發布內容。
- 改 Google Ads / Meta Ads 預算、投放、受眾、開關、付款。
- 讀 secrets、API keys、cookies。
- 修改 Rank Math 付費/退訂設定。

## Resume Prompt

我是 A2 Ads / SEO / WordPress Patrol。請先讀 `CURRENT_STATUS.md`、`pitfalls.md`、`handoff/tasks/T-A2-006-ads-seo-wordpress-patrol.md`、`projects/a2-ads-seo-wordpress-patrol.md`、`projects/seo-ads-agent.md`、`skills/brand-voice-guide.md`、`skills/maplab-visual-spec.md`。先輸出品牌記憶確認，再巡查 WordPress / SEO / Ads，安全修改只限 repo/report/proposal，不可發布或改廣告設定。
