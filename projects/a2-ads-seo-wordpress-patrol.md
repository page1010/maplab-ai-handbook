# A2 Ads / SEO / WordPress Patrol

建立：2026-05-29
狀態：召喚型可用 + 定時巡查

## Purpose

A2 新增固定巡查任務：針對 MAPLAB Kitchen 的廣告、SEO 策略、WordPress 狀態與品牌記憶做一次完整檢查，必要時著手安全修改 repo 文件、草稿計畫與 review bundle。外部系統變更仍需 Owner 批准。

## Startup Memory Check

A2 被 Chrome Extension 召喚後，必須先回答並確認：

1. 品牌價值：自然、溫暖、安靜、細緻、有質感、專業、穩定、有分寸；不靠低價、不硬賣。
2. 品牌語氣：說場景，不硬講賣點；具體、克制、穩定；禁用誇張促銷語。
3. 品牌顏色與視覺：先讀 `skills/maplab-visual-spec.md`，不可憑記憶猜色票。
4. 網頁狀態：以 live URL / WordPress public REST / Owner Chrome read-only evidence 為準，不把 planned slug 當 live URL。
5. 企業文化：MAPLAB 的款待、場景、專業與 Investment OS 的證據分層、風控、交接紀律共用，輸出時嚴格分清「已驗證 / 推論 / 缺資料 / 需批准」。

## Patrol Scope

- WordPress：live pages/posts、draft status、category、圖片/alt/caption、內連結、未發布草稿。
- SEO：關鍵字、title/meta/slug、live URL、Search Console/GSC 觀察、內容缺口。
- Ads：Google Ads / Meta Ads 只讀巡查、landing page alignment、keyword final URL、受眾與廣告目標是否與品牌/SEO 對齊。
- Brand：品牌語氣、禁用語、視覺色票、頁面是否仍像 MAPLAB。
- Cross-culture：MAPLAB 對外內容與 Investment OS 的嚴格證據分層、風險邊界、交接紀律共用。

## Safe Actions

A2 可直接做：

- repo 文件更新、review bundle、巡查報告。
- 未發布草稿的變更計畫。
- SEO / Ads / WordPress 的 read-only evidence matrix。
- 明確標為 proposal 的文案、landing page plan、內連結建議。

## Approval-Ready Automation

A2/A3/A4 的第二層任務不是停止在「需 Owner 批准」。正確輸出是
approval-ready plan：先自動整理為什麼要改、改什麼、預期效果、影響範圍、
風險、rollback、驗收方式與 Owner 可選項，讓 Owner 可以直接批准、提問或退回。

必讀協議：`projects/a2a3a4-approval-ready-automation.md`

預設閉環：

1. A4 產素材 readiness / slot / WebP / alt / caption manifest。
2. A2 產 SEO / WordPress / landing / 內連結 plan。
3. A3 產 Google Ads / Meta Ads / GTM / Pixel / UTM plan。
4. A2 整合 `owner_approval_card.md`。
5. Owner 批准精確範圍後，才進 execution mode。

A2 不可直接做：

- 發布 WordPress。
- 改 Google Ads / Meta Ads 預算、投放、受眾、開關、付款。
- 讀 secrets、API keys、cookies。
- 改 Rank Math 付費/退訂相關設定。
- 把未驗證 live URL 當作可投放 landing page。

Owner-approved WordPress execution 例外：若 Owner 已精確批准建立或更新未發布草稿，
A2 必須先讀 `skills/credentials/wordpress-api.md`，再依
`AGENT_STARTUP_PROTOCOL.md Step 5.5` 與 `AGENT_RULES.md Credential 例外`處理。
Notion API Keys 保管室可作 credential vault / index，但不可作狀態真相；secret
本體與衍生 header 不得寫進 repo、memory、log、review bundle 或 final。批准範圍
以外仍禁止，且 WordPress status 必須維持 `draft`。

## Output Contract

預設寫到 `workbook/reviews/JOB-A2-ADS-SEO-WP-PATROL-YYYYMMDD/`：

- `ads_seo_wordpress_patrol.md`
- `brand_memory_check.md`
- `wordpress_status_matrix.md`
- `ads_landing_alignment.md`
- `safe_fix_log.md`
- `review_request.md`

如果巡查發現需要正式外部變更，還必須補：

- `a4_asset_manifest.md`
- `a2_seo_wordpress_plan.md`
- `a3_ads_strategy_plan.md`
- `owner_approval_card.md`
- `integration_review.md`
