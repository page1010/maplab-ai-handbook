# 6 月真實案例 → SEO 矩陣對照表

版本：v1.0 | 建立：2026-07-04 | 狀態：規劃分類（唯讀，不改 Drive 試算表）
維護：A2

> ⚠️ **硬規則**：本文件是分類規劃，**絕不碰、不改「外燴系統」那張 Drive 試算表**。
> 來源資料夾：Drive「真實案例」(id `1pKfGSOZXBpG7qXcJrW5T7aoHX4nqB1Tt`)

---

## 為什麼真實案例是最高優先資產

真實案例對 SEO 同時提供三層價值：

| 價值層 | 說明 |
|---|---|
| **E-E-A-T（經驗證據）** | Google 最重視「有實際服務經驗」的頁面；真實案例照片 + 場次資訊是 Experience 的直接証明，比純 how-to 文章權重高 |
| **圖片 SEO** | 真實拍攝的場景照，alt + 檔名命名後可被 Google 圖片搜尋收錄；正確的 webp 轉換 + SEO 命名（`maplab-{場景}-{描述}.webp`）是獨立流量來源 |
| **廣告素材** | `asset_conversion_manifest` 裡標 `ad_ok=yes` 的真實案例照可直接進廣告；比 AI 生圖 CTR 高，且合規欄位已在素材表管控 |

**最高優先做「會議」兩場**（富信飯店社工公會 + 大台南會展工研院）：
- 接上現有 HR 行政茶會文章線（WP 1992），補文章缺少的 proof 照片
- 直接對上 Google Campaign5「高意圖\_大臺南會展中心」在跑的關鍵字
- 兩場都是 B 端，CPL 價值高於 C 端

---

## 案例分類矩陣

| 案例（資料夾名/場次）| cluster | 目標關鍵字方向 | 對應 landing slug | 可做案例文 | 圖片素材處理 |
|---|---|---|---|---|---|
| **富信飯店—社工公會會議（0614）** ★ | `meeting_refreshment` | 會議茶點、機構會議外燴、社福機構茶會 | `corporate-tea-party-desserts` | ✅ **最優先** — 真實案例回填「會議茶點」線，補 WP 1992 HR 文缺的 proof | HEIC→webp；alt=`台南機構會議外燴—富信飯店社工公會茶點桌`；查 needs_face_crop（與會者） |
| **大台南會展中心—工研院跨部會會議（0612）** ★ | `meeting_refreshment` / `corporate_forum` | 會展中心茶點、政府會議外燴、跨部會會議茶點 | `corporate-tea-party-desserts` | ✅ **最優先** — 直接對上 Google Campaign5 高意圖_大臺南會展中心 | HEIC→webp；alt=`台南會展外燴—大台南會展中心工研院跨部會茶點`；查 needs_face_crop |
| 遊學說明會 gostudy（0627） | `meeting_refreshment` / 說明會 | 說明會茶點、講座點心外燴、教育活動茶會 | `corporate-tea-party-desserts` | ⬜ 次優先，補「說明會/講座」案型 | HEIC→webp；alt=`台南說明會外燴—gostudy 遊學講座茶點`；查 needs_face_crop（學員） |
| 仁德資訊安全中心—三立論壇（0625） | `corporate_forum` | 論壇茶點、記者會外燴、媒體活動外燴 | `brand-esg-catering-service` | ⬜ 次優先，有「三立」媒體背書，ESG/論壇關鍵字強 | HEIC→webp；alt=`台南論壇外燴—三立資安論壇茶點陳設`；查 needs_face_crop（講者/嘉賓）、needs_logo_crop（三立 logo） |
| 說事實木地板開幕（0621） | `opening_tea` | 店面開幕茶會、木地板品牌開幕外燴 | `tainan-corporate-opening-tea-catering` | ⬜ 補開幕 cluster 案例 | HEIC→webp；alt=`台南店面開幕外燴—說事實木地板茶會點心`；查 needs_logo_crop（品牌招牌） |
| 醞舞流舞蹈教室開幕（0614） | `opening_tea` | 教室開幕茶會、文創空間開幕外燴 | `tainan-corporate-opening-tea-catering` | ⬜ 補開幕 cluster 案例，與上一場可合併為「小型空間開幕」案例頁 | HEIC→webp；alt=`台南教室開幕外燴—醞舞流舞蹈教室茶會`；查 needs_face_crop（學員） |
| 建案百慶擎川（0613） | `brand_vip` | 建案 VIP 茶點、預售屋賞屋接待外燴、豪宅開案茶會 | `vip-expo-catering-business-meeting` | ✅ 高價值（建案 VIP 接待 = 高消費受眾），廣告素材潛力高 | HEIC→webp；alt=`台南建案外燴—擎川 VIP 賞屋茶點桌`；嚴查 needs_face_crop（潛在買家） |
| 東門教會證婚（0627） | `wedding`（可能新 cluster） | 證婚茶會、教會婚禮外燴、婚禮茶點 | ⚠️ 婚禮 landing 待確認是否存在 | ⬜ 評估新 cluster — 若站上已有婚禮頁則填入；若無，列為內容缺口 | HEIC→webp；alt=`台南教會婚禮外燴—東門教會證婚茶點`；**嚴查 needs_face_crop**（新人/來賓） |
| 歡樂時光—性別派對（0621） | `party`（C 端） | 性別派對外燴、主題派對點心、彩虹派對茶會 | ⚠️ 派對 landing 待確認是否存在 | ⬜ 評估 C 端派對 cluster — 若站上有慶生/派對頁則合併；若無，列為內容缺口 | HEIC→webp；alt=`台南派對外燴—性別派對茶點氣球佈置`；查 needs_face_crop（來賓） |
| 遊艇氣泡水（0613） | `lifestyle` / 特殊場域 | 遊艇派對外燴、戶外活動飲品、台南戶外茶會 | ⚠️ 待評估（niche，目前站上無對應頁） | ⬜ 評估值不值獨立一頁（搜尋量不確定），暫掛 | HEIC→webp；alt=`台南遊艇外燴—戶外活動氣泡水茶點`；查 needs_face_crop |

---

## 圖片素材處理流程（每場共用）

依 `skills/seo-image-from-album.md` 執行，每場案例圖的標準流程：

```
1. 從 Drive 真實案例子資料夾下載原始 HEIC
2. HEIC → webp 轉換（保持長寬比，目標 1920px 長邊）
3. 檔名命名：maplab-{場景關鍵字}-{描述}.webp（無中文/空格）
4. 必查三個合規欄位（對照 asset_conversion_manifest 或人工判斷）：
   - needs_face_crop：有人臉 → 先裁/模糊，才能上傳
   - needs_logo_crop：有外部品牌 logo → 確認可公開才上傳
   - ad_ok：若要進廣告素材，需此欄 = yes
5. alt 文字：台南{場景}外燴—{具體描述}（A 式格式）
6. 上傳 WP Media，設定 alt / caption / description
7. 回填 asset_conversion_manifest（A4 執行）
```

**合規高風險場次**（需 A4 優先處理人臉/logo）：
- 東門教會證婚：新人正面 → 嚴查
- 建案百慶擎川：潛在買家正面 → 嚴查
- 大台南會展工研院：政府/企業人員 → 查

---

## ✅ 三個內容缺口 — 已決策（2026-07-05 Owner 定案 + 2026-07-07 SEO 三人小組覆核確認）

> 本節原為「待 A0/Owner 確認」，決策記錄在 `docs/ad-buildout-plan.md` P2 段（2026-07-05）；2026-07-07 A2 交叉查核 `docs/seo-keyword-map.md` 與 WP REST 全站掃描後發現婚禮/派對其實早已是 live 頁面，不是空缺；SEO 三人小組（Claude+Codex+Antigravity）07-07 覆核三項決策皆一致同意，詳見 `docs/ad-funnel-battle-plan.md` §7。

### 1. 婚禮 / 證婚 landing — ✅ 開（其實早就存在，非新建）

**修正認知**：`docs/seo-keyword-map.md` 已列 5 個婚禮 slug 為 `live_referenced`；2026-07-07 WP REST 全站掃描確認「台南證婚派對外燴」「台南戶外婚禮外燴」等多篇文章 live。`東門教會證婚` 案例不需要「找 landing」，而是回填進既有頁面補案例證據。
**決策**：受眾包 `cold-c-wedding`（生命里程碑：訂婚/結婚，年齡25-40），熱層字詞「台南戶外婚禮外燴」「台南婚禮茶點」，主 landing 建議整合到 `outdoor-wedding-catering-venue`。三人小組提醒：既有婚禮頁偏多、有互搶風險，新素材/廣告流量導向單一主 landing，不要再開新 slug。

### 2. 派對（性別揭曉派對）landing — ✅ 併入慶生線，不獨立

**修正認知**：`gender-reveal-party-tips` 已是 `live_referenced`，週歲/慶生類文章也已 `verified`，不是空缺。
**決策**：不獨立受眾包，併入 `cold-c-birthday`（慶生線）定向。三人小組補充：SEO 頁可保留現狀，但慶生 landing 內建議有一個小節/案例圖承接「性別派對」的 message-match，避免廣告點進來後受眾覺得文不對題。

### 3. 遊艇/戶外特殊場域 — ❌ 不建獨立頁、不投廣告（此版本排除）

**決策維持**：受眾規模太小、無對應 landing，此版本排除，待日後評估。三人小組建議：案例照片不浪費，改作 B4 VIP/公關品牌 cluster 的廣告輪播素材使用（彰顯承接高端活動的視覺美感），不必等關鍵字量評估完才有出路。

---

## 變更紀錄

| 版本 | 日期 | 變更 | 來源 |
|---|---|---|---|
| v1.0 | 2026-07-04 | 初版：10 場 6 月案例分類進 SEO 矩陣，含三個內容缺口標注 | Owner 指定骨架 + 提供案例清單 |
| v1.1 | 2026-07-07 | 3 個內容缺口改標「已決策」，補回 07-05 Owner 定案內容 + SEO 三人小組覆核意見；修正婚禮/派對 landing 其實早已存在的認知錯誤 | Owner 07-05 定案 + 三人小組 07-07 評審 |
