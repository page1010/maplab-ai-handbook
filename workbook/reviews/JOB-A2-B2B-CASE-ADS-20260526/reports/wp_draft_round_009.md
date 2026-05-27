# A2 Round 009 — WordPress Draft Save Report

日期：2026-05-27
角色：A2 搜尋流量作戰部
範圍：把 Round 008 案例草稿實際存入 WordPress；不發布、不改 Rank Math、不改 Ads。

## Startup / Goal Check

1. 任務目標：把本輪案例內容建立成 WordPress 未發布草稿，讓 Owner 能在 WP 後台審稿。
2. 系統價值：A2 產物不只停在 repo Markdown，而是進入實際 WordPress 審核流。
3. 使用者價值：Owner 可直接打開 WP 草稿看內容，後續再決定是否插入正式頁。
4. 完成標準：WP draft 存在、內容持久化、狀態未發布、保留案例段與圖片 slot 對應；若圖片不能上傳，必須清楚列阻塞原因。
5. 允許範圍：使用 Owner Chrome 登入態、建立未發布草稿、保存 repo 斷點。
6. 禁止範圍：發布 WordPress、修改現有正式頁、修改 Rank Math、修改 Google Ads / Meta Ads、讀取密碼/cookie/API key。
7. 不清楚之處：Owner 未指定要一篇總審稿草稿或多篇 landing page draft；本輪採最小風險的一篇總審稿草稿。

## Verified WordPress Draft

- Post ID：`1696`
- Status：`草稿`
- Title：`MAPLAB 企業外燴與活動茶點案例審核草稿 Round 008`
- Edit URL：`https://www.maplabkitchen.com/wp-admin/post.php?post=1696&action=edit`
- Persistence check：已重新載入 edit URL 後確認內容仍存在。
- Content check：
  - 文字長度：約 8,068 字元。
  - 已包含案例段 1-21。
  - 已包含每則案例的建議插入頁、圖片 slot、檔名、Alt、Caption。
  - 未發布；未點 Publish；未修改 Rank Math；未修改 Google Ads / Meta Ads。

## Image Upload Status

已完成本機素材：

- `wordpress_assets_round_008/`：30/30 WebP 已存在。
- `asset_conversion_status_round_008.csv`：30/30 converted。

本輪未完成 WordPress 實體圖片插入，原因如下：

1. A2 嘗試透過 Chrome file chooser 上傳 30 張 WebP。
2. Chrome extension 回錯誤：`{"code":-32000,"message":"Not allowed"} fileChooser.setFiles failed`
3. 依 Chrome skill，若要讓 Codex extension 上傳本機檔案，需要 Owner 在 Chrome extension 設定允許 file URL access。
4. A2 也檢查 WordPress uploads 預期路徑 `https://www.maplabkitchen.com/wp-content/uploads/2026/05/{filename}.webp`，30 張目前皆為 `404`，表示尚未上傳到 WP media library。

Tool-required user-facing instruction if continuing image upload:

```text
To enable file upload, go to chrome://extensions in Chrome, click Details under the Codex extension, and enable "Allow access to file URLs." See [here](https://developers.openai.com/codex/app/chrome-extension#upload-files) for details.
```

## Ads Routing Pointer

廣告設定建議仍以 Round 008 proposal 為準：

- `ads_landing_settings_round_008.md`

本輪未更動 Google Ads / Meta Ads。建議仍是：

- Google Ads：以 P1 搜尋意圖拆組導到 existing live To B URLs；不要直接改既有 keyword final URL，先做 proposal / duplicate campaign path。
- Meta Ads：現役互動廣告保留不動；另建獨立 landing-page traffic path，把建案 VIP、企業開幕、會議茶點、文化場館案例導到對應 WordPress live posts。

## Self-Review Loop

1. 原始任務是讓 Owner 看到 WordPress 草稿，而不是 repo Markdown：已達成文字草稿。
2. 變動與初始目標一致：是，建立未發布 WP draft，沒有動正式頁。
3. 完成標準是否達成：部分達成。WP draft 達成；圖片實體插入未達成。
4. 是否新增不必要複雜度：否，採單篇審稿草稿，避免多篇 draft 混亂。
5. 是否碰到禁止範圍：否。未發布、未改 Rank Math、未改 Ads、未讀 credential。
6. 下一步最小可執行動作：Owner 開啟 Codex Chrome extension 的 file URL access 後，A2 再上傳 30 張 WebP 到 media library 並插入同一篇 draft。

## Resume Prompt

```text
我是 A2 搜尋流量作戰部，接續 T-A2A3-001-B Round 009 WordPress draft。

先讀：
1. CURRENT_STATUS.md
2. handoff/tasks/T-A2A3-001-B.md
3. workbook/reviews/JOB-A2-B2B-CASE-ADS-20260526/reports/wp_draft_round_009.md
4. workbook/reviews/JOB-A2-B2B-CASE-ADS-20260526/wordpress_case_insert_draft_round_008.md
5. workbook/reviews/JOB-A2-B2B-CASE-ADS-20260526/ads_landing_settings_round_008.md
6. workbook/reviews/JOB-A2-B2B-CASE-ADS-20260526/asset_conversion_status_round_008.csv

現況：
- WordPress draft 已建立並驗證持久化。
- Draft edit URL：https://www.maplabkitchen.com/wp-admin/post.php?post=1696&action=edit
- Draft status：草稿。
- 內容已含 21 則案例段與圖片 slot/檔名/Alt/Caption。
- 圖片實體尚未插入，因 Chrome extension file upload 回 `Not allowed`。
- 不發布、不改 Rank Math、不改 Google Ads / Meta Ads。

下一步：
1. 若 Owner 已開啟 Codex Chrome extension 的 file URL access，重試上傳 `wordpress_assets_round_008/` 30 張 WebP。
2. 將圖片插入 post=1696 的照片素材區或對應案例段。
3. 儲存草稿後重新載入 edit URL 驗證圖片仍在。
4. 更新 wp_draft_round_009 或新增 Round 010 report，commit checkpoint。
```
