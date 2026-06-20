# Safe Fix Log — JOB-fullsite-patrol-20260615

## 2026-06-15 — post 945 `brand-esg-catering-service` 崩壞尾巴清除 + 結構升級

**對應清單（哪個改動 → 哪個 URL）**
- URL：https://www.maplabkitchen.com/brand-esg-catering-service/ (post id 945)

**改了什麼**
1. 移除 `KEYWORD-RECOVERY:brand END` 之後的全部廢文：`段落15/16`×3 重複、紅字 `[圖片未能載入: maplab-brand-conference-beauty-summit-meta.webp]`、假 `歷年案例精選`（內含重複佔位）。
2. 開頭埋 🍁 `<!-- 🍁 MAPLAB-AUTHENTIC v1 -->`。
3. 新增「快速索引」TOC（5 項）+ 各案例 H3/H2 加 anchor id（case-benz / case-siraya / case-tech / case-logistics / brand-event-points）。
4. 保留全部真案例（賓士偏鄉/西拉雅/美光科林/收拾復原）、CTA、作者介紹、相關文章、內連、結尾重點區。

**結果**：raw 13328 → 10276 字元；status 維持 `publish`；WP 自動存 revision（可回復）。

**三層驗證**
- raw(authed)：🍁 在、廢文清除 ✅
- rendered(public REST)：快速索引/錨點在、段落/圖片未能載入/歷年案例精選 皆 False ✅
- 前台 HTML + Chrome `get_page_text`：閱讀邏輯乾淨、無殘留 ✅（cache 無 stale）

**未動（待 Owner）**
- 圖片雙副檔名 `…webp.webp`（8 張皆 HTTP 200 可載入，僅命名醜，重新上傳有風險，暫緩）。
- 結構微調：CTA/作者/相關文章在結尾重點區之前，順序略可優化，未重排（降低風險）。

**工具**：WP REST Basic Auth（Cloudways posts 端點實測可用）+ Chrome MCP 驗證。憑證取自 Notion 保管室，用後即刪，未落地。

## 2026-06-15 — 批次：矩陣頁補強 + 全站壞連結修復

### 13 篇經典矩陣頁補強（live，前台驗證）
1199 1207 1209 1211 1213 1215 1217 1218 1220 1222 1224 1226 1227
- TOC「📋 本文目錄」→「快速索引」
- 1211 加「不同規模的實際案例參考」（成功大學數百人 / 科林研發大型研發，**無價格**，名稱已核實）
- 1217 偵測到 1 處 AI 說服式句型 → 已標記待人工重寫（未自動改）

### 全站壞連結修復（49 篇，live，前台+Elementor 皆驗證 0 殘留）
舊 planned slug 404 → live：
- /catering-corporate-tainan/(404, 29篇) → /corporate-catering-tainan/
- /catering-birthday-party-tainan/(404, 25篇) → /catering-one-year-old-party-tainan/
- /catering-wedding-tainan/(404, 22篇) → /wedding-catering-vs-banquet-tainan/
- /esg-event-catering-tainan/、/tainan-esg-activity-catering/ → /brand-esg-catering-service/
- /tainan-corporate-tea-catering/ → /corporate-tea-party-desserts/
- /tainan-catering-venue-7/、/tai-nan-wai-hui-chang-di-tui-jian/ → /tai-nan-wai-hui-chang-di-tui-jian-2023/
- /tainan-catering-cost/ → /tainan-catering-cost-guide/
驗證：rendered + Elementor 前台皆 0 殘留 404 內連。
工具：確定性批次腳本（比逐篇 agent 省額度）；目標全部先驗證 200 才替換。

### 待辦
- 圖片補圖（34 篇 0 圖）→ 發包 subagent/Codex（需 Drive 實拍配對）
- 婚禮/週歲/地區/菜單矩陣頁「真案例」需 Owner 案例素材（目前僅做一致性+內連，未捏造案例）
- AI 語氣重寫：1217 等
- Elementor 12 篇正文（TOC/補圖）：Chrome 編輯器
