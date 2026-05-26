# Access Check

日期：2026-05-26
執行者：A2 / Codex Chrome Extension
模式：只讀；未發布、未儲存、未修改 WordPress / Google Ads / Meta Ads 設定。

## Chrome Extension

- 結果：可連線。
- 觀察：Chrome 已有 Google Ads 總覽、GA4、WordPress 控制台分頁。
- 處理：A2 另開臨時分頁做只讀檢查，檢查後已 finalize，不保留臨時分頁。

## WordPress

檢查 URL：

`https://www.maplabkitchen.com/wp-admin/post.php?post=586&action=edit`

結果：

- 可進入 WordPress 文章編輯頁。
- 頁面標題：`編輯文章 - 台南企業外燴推薦｜會議茶點、開幕茶會與品牌活動規劃｜MAPLAB ‹ MAPLABKITCHEN — WordPress`
- 可見 post slug：`corporate-catering-tainan`
- 可見文章狀態：已發佈。
- 可見 Elementor 編輯入口與文章內容區。
- 未按 `Update` / `Publish` / `Save`。

判斷：

WordPress 端可進入至少一個 live B2B post 的編輯頁。Antigravity 下一步應用同樣只讀方式檢查 7 個 live URL 的 post editor 或前台頁面，不做儲存。

## Google Ads

檢查 URL：

`https://ads.google.com/aw/keywords?ocid=252396667`

結果：

- 可進入 Google Ads account `844-336-3178` 的搜尋關鍵字頁。
- 頁面標題：`搜尋關鍵字 - 844-336-3178 - Google Ads`
- 可見導覽：`目標對象、關鍵字和內容` -> `關鍵字`
- 可見資料檢視日期：2026 年 3 月 13 日 - 4 月 9 日。
- 可見 campaign：`Campaign 4：高意圖搜尋_南台灣外燴`
- 可見 ad group：`廣告群組 1`
- 可見 keyword rows：
  - `"台南研討會餐點"`，詞組比對，狀態：不符合資格 / 搜尋量偏低
  - `"台南診所開幕茶會"`，詞組比對，狀態：不符合資格 / 搜尋量偏低
  - `"台南品牌活動外燴"`，詞組比對，狀態：不符合資格 / 搜尋量偏低
- 未新增、未刪除、未修改 keyword、final URL、search theme、budget 或 conversion goal。

判斷：

Google Ads 的 keyword 設定頁可進入，且目前已有高意圖搜尋 campaign。後續不是先亂加 keyword，而是先用 `review_request.md` 的 landing page matrix 檢查：

- 這些 keyword 是否有正確 final URL。
- 是否需要把 `會議茶點 / 開幕茶會 / VIP 接待 / 美術館展覽` 拆成更乾淨的 ad group。
- 低搜尋量 keyword 要不要保留為 phrase match，或改成更接近搜尋需求的組合。

## Meta Ads

本次尚未進 Meta Ads Manager。Meta 的 detailed targeting 可用項目會變動，下一步由 A3 / Antigravity 做只讀檢查：

- 是否能進 campaign / ad set。
- detailed targeting 或 Advantage+ audience suggestion 是否可用。
- Pixel / conversion event 是否仍指向 maplabkitchen.com。

## Next

1. Antigravity 依 `review_request.md` 的 prompt 繼續做 7 個 live WordPress post 的只讀檢查。
2. Antigravity 補 Google Ads campaign/ad group/final URL matrix，不改設定。
3. A2 開始寫第一批 B2B 案例段草稿。
4. A3 接 Meta 分眾規劃與素材角度。

