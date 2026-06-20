# MAPLAB 文章配圖：資源地圖 + 配圖流程（A2 / Codex / 地端模型共用）

版本：v1.0 | 建立：2026-06-16 | 維護：A2
> 給任何要幫 maplabkitchen.com 文章找圖、換圖、補圖的 agent（含地端 gemma4 等容易迷路的模型）。
> 核心原則：**先用「已整理好、命名清楚」的本機素材，不要憑檔名猜「是不是盜圖」，最後一定要視覺核對。**

---

## 0. 三條鐵則（先記這個）

1. **不可用「英文檔名 = stock 盜圖」判斷。** Owner 自己/AI 產的菜圖也是英文描述名（例：`Creamy-Penne-Carbonara`）。要判斷「是不是自有」看**出處**（有沒有在下列已整理資料夾 / 品項目錄裡），再**視覺核對**，不是看檔名。
2. **698（`tainan-custom-catering-menu`）是 Owner 一張一張手做的頁面，禁止改它的圖。** 其他 Owner 手做頁同理，先問再動。
3. **配不到合適的真圖就停下來問 Owner，不要硬塞一張。** 食物/案例配錯比沒圖更糟。
4. **毛利紅線：低毛利品不可當主軸、不可主動曝光。**
   - ❌ **餐盒 / bento / 便當盒裝**＝低毛利，會拉低毛利，**絕不放主圖、不主動曝光**（2026-06-16 Owner 明確指示）。
   - ✅ 要主打**高毛利擺盤**：長桌 buffet、層架甜點、手指食物、桌面佈置、飲品桶、花藝陳列。
   - 選圖前先看：這張呈現的是「精緻擺盤外燴」還是「餐盒外帶」？是餐盒就換掉。

---

## 1. 配圖素材地圖（依優先序）

### A0. 文章/案例圖 — 最佳來源（已分類、有索引、可對主題）
`~/Desktop/2025案例/` — A4 的 2025 案例素材庫（asset-case-match 產出）。看 `README_INDEX.md` 的分類索引：
- ToB：`會議茶點`(科林研發,8) / `企業茶會`(亞綸科技,2) / `開幕茶會`(住商+美甲,12) / `品牌活動_建案`(建案開工,7)
- ToC：`生日週歲派對`(兜兜親子12 / 輕輕的說5) / `家庭聚會_入厝`(新居入厝,12) / `性別揭曉`(1)
- 每個案例資料夾有 `public_case_notes.md`（公開可用方向，**禁價格/人數/電話/地址**）。文章主題 → 對到 ToB/ToC 場景資料夾挑圖。
- ⚠️ 婚禮在此庫沒有；婚禮只有 B 區 1 張（`maplab-outdoor-wedding-catering-venue`）→ 婚禮頁可裁切重用或先標缺口。

### A. 文章/案例圖 — 也可用（本機、已 webp、已 SEO 命名、可直接上 WP）
`~/Desktop/案例分享wordpress用_webp/`（30 張）+ `~/Desktop/案例分享wordpress用/`
- 每張 = 一個真實案例，檔名即場景，例：
  `maplab-office-opening-amd-tea-party-case.webp`、`maplab-corporate-forum-cathay-wealth-management-hero.webp`、
  `maplab-outdoor-wedding-catering-venue.webp`、`maplab-white-theme-birthday-party.webp`、
  `maplab-museum-exhibition-siraya-opening-case.webp`、`maplab-real-estate-vip-reception-*.webp`…
- 文章主題 → 對應案例檔名挑選（企業開幕→amd/ocean-industry；論壇→cathay；婚禮→outdoor-wedding；週歲/生日→white-theme/old-money-birthday；展覽→art-museum/siraya/tangdezhang；VIP→real-estate-vip-*）。

### B. 單一菜色/菜單圖 — 首選（本機，依 item_id 命名）
`~/Desktop/item 圖片夾/`（52 張）— 檔名 = `<item_id> <菜名>`，例 `DST013 義式提拉米蘇.jpg`、`MAIN002 濕式熟成牛排.JPG`、`APP026 尼斯鮪魚奶油乳酪可頌.jpg`
- item_id 對應品項目錄 `data/items_master.json`（102 品項：主食 MAIN / 餐食小點 APP / 甜點 DST / 飲品）。
- 要某道菜的圖：在 items_master 找 item_id → 在 item 圖片夾 抓對應檔。

### C. 補充素材（本機，量大、未必命名）
`~/Desktop/外燴照片（擺設）/`（119）、`~/Desktop/2025案例/`（147）、`~/Desktop/場景檔案夾/`

### D. 最後手段 — A4 場景索引（lb99104 雲端，量大但有雜訊）
A4 整理的是 **mina/lb99104 帳號**的雲端硬碟 `MAPLAB/MAPLAB_ASSETS`，索引在本機 `data/photo_alt_index.db`
（table `photos(rel_path,alt_zh,scene,tags,usable)`，~28K usable，scene：茶點桌面/企業活動/慶生派對/餐點特寫/婚禮/場地空景…）。
- ⚠️ **只在 A/B/C 都找不到時才用**。檔案在 lb99104 雲端（本機可能沒同步），需 Drive API 取；**同名有重複、且有壞檔**（例：一張 catering 名稱底下其實是 5,246,281 bytes 的 Porsche 廣告圖）。用時必須資料夾遍歷解析正確檔 + 下載後 PIL 驗證 + size!=5246281。

### 品項介紹 sheet（描述文字，需要時查）
`data/items_master.json` 只有名稱/分類/成本，無描述。完整品項介紹在 Google Sheet（外燴系統 / 報價表）。要寫菜色文案再查。

---

## 2. 配圖流程（每張都走一遍）

1. **判斷需求**：這篇/這個位置要「案例場景圖」(用 A) 還是「單一菜色圖」(用 B)？
2. **挑候選**：從對應資料夾依檔名/ item_id 找 1–2 張最貼題的。
3. **視覺核對（必做）**：實際開圖看內容對不對（用 `Read` 看圖、或 `qlmanage -p`、或 PIL）。確認是真 MAPLAB 食物/現場、構圖 OK、無人臉/外部 logo/酒（依 `maplab-visual-spec.md`）。
4. **裁切 + 轉檔/命名**：**可以裁切**（Owner 2026-06-16 同意）——裁掉非 MAPLAB 文字浮水印/外部 logo、裁掉畫面內的低毛利品（餐盒）、裁成適合比例（WP 精選圖 16:9 ≈1200×675；內文橫式佳）、聚焦高毛利擺盤。MAPLAB 自家品牌浮水印可留。工具：`sips`（`sips -c H W` 裁、`-z` 縮、`-s format webp`）或 PIL。A 資料夾已 webp；其他先縮 ≤1600 再 `cwebp -q 82`。命名 `maplab-{場景}-{描述}.webp`。
5. **上傳 WP media**（REST，憑證見 `wp-article-standard.md §5`，用後即刪）：
   ```
   curl -s -K /tmp/.maplab_wp.cfg -X POST ".../wp/v2/media" \
     -H "Content-Disposition: attachment; filename=<name>.webp" \
     -H "Content-Type: image/webp" --data-binary @<file>
   ```
   再設 alt：`POST .../media/<id> -d '{"alt_text":"台南{場景}外燴—{描述}"}'`。
   （註：WP 會把 webp 轉存 avif；用回傳的 source_url。Cloudflare 偶發 524 但 media 仍建立 → 檢查並刪重複。）
6. **放上文章**：featured 用 `POST .../posts/<id> -d '{"featured_media":<id>}'`；inline 用 wp:image 區塊插入內文（經典文章可 REST；**Elementor 文章內文圖在 _elementor_data，REST 改不動，需 Elementor 編輯器**）。
7. **三層驗證**：raw / rendered / 前台 HTML 都確認新圖在、舊圖無。

---

## 3. 踩過的坑（務必避免）

- ❌ 用檔名猜盜圖 → 誤把 Owner 手做的 698 當 stock。**改看出處 + 視覺。**
- ❌ 直接從 MAPLAB_ASSETS 用裸檔名搜尋下載 → 抓到同名 Porsche 壞檔。**先用桌面已整理資料夾。**
- ❌ 把 base64 整張圖載進主對話 → 燒爆額度。**下載類重活丟 subagent；或直接用本機檔避免下載。**
- ❌ 配不到還硬塞 → 食物/案例圖文不符。**寧可停下問 Owner。**

## 4. 給地端模型的最短指令
> 要幫文章配圖：(1) 案例圖去 `~/Desktop/案例分享wordpress用_webp/` 按檔名挑、菜色圖去 `~/Desktop/item 圖片夾/` 按 item_id 挑；(2) 開圖看過確認是對的真圖；(3) `cwebp` 轉（若非 webp）；(4) 用 `curl -K /tmp/.maplab_wp.cfg` 上傳 media + 設 alt；(5) 設 featured 或插 wp:image；(6) 開前台確認。**不確定就停，別亂配。** 細節讀本檔 §1–§2。
