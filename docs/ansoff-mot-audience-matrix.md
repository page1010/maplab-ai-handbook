# 安索夫矩陣 × MOT × 受眾溫度 × 廣告策略對應表

版本：v0.1-draft | 建立：2026-07-03 | 狀態：**草案，待 A0 審（標記處）→ Owner 定案**
隸屬：`docs/A2-ad-ops-improvement-plan.md` Phase 0 產出

---

## 閱讀說明

- **安索夫四格**：滲透 / 市場開發 / 產品開發 / 多角化
- **MOT（Moment of Truth）**：客戶決策觸點——「搜尋比較」「詢價評估」「成交回訪」「推薦轉介」
- **受眾溫度**：冷（首次接觸）/ 溫（有互動未成交）/ 熱（曾詢價或成交）
- **素材 cluster**：`brand_vip` / `opening_tea` / `corporate_meeting` / `meeting_refreshment` / `cultural_venue`
- **廣告動作**：再行銷（Retarget）/ Lookalike / 興趣受眾 / 不投（有機觸達即可）

> ⚠️ 素材欄的 `output_filename` 為草案推測值，以 `asset_conversion_manifest` 實際欄位為準。標「**待 A0 審**」的格子需 A0 或 Owner 核實後才能進 Phase 1。

---

## 矩陣總表

| 安索夫格子 | 核心邏輯 | MOT 觸點 | 受眾溫度 | 廣告動作 | 適用 cluster | 對應 landing_slug（草案） | 建議素材（output_filename 草案）**待 A0 審** |
|---|---|---|---|---|---|---|---|
| **①滲透**（既有客 × 既有品） | 複購 + 轉介紹，鎖住已知客 | 成交回訪 / 推薦轉介 | 🔴 熱 | 嚴格再行銷（曾詢價客 + 成交客自訂受眾） | `brand_vip` / `corporate_meeting` | `corporate-catering-tainan` / `tainan-corporate-catering-cost` | maplab-corporate-forum-cathay-wealth-management-hero.webp（熱客識別度高，已驗 ad_ok） |
| **②市場開發**（新客 × 既有品） | 把既有案型推給還不認識我們的企業新客 | 搜尋比較 / 進店 | 🔵 冷 | Lookalike（以成交客為種子）+ 職業興趣受眾（HR / 秘書 / 行政 / 企業主） | `opening_tea` / `corporate_meeting` | `corporate-catering-tainan` / `hr-admin-meeting-catering-guide-tainan` | maplab-opening-tea-hero.webp（**待 A0 審**：確認是否有 cluster=opening_tea 的 hero_16x9 且 ad_ok=yes） |
| **③產品開發**（老客 × 新品/新案型） | 既有企業客試用他們還沒點過的案型 | 詢價評估 / 複購 | 🟡 溫熱 | 溫再行銷（互動未成交）+ 既有客郵件/LINE 推播 | `meeting_refreshment` / `cultural_venue` | `meeting-refreshment-catering-tainan`（⚠️ 確認 live 狀態）/ `corporate-tea-party-desserts` | maplab-meeting-refreshment-case-hero.webp（**待 A0 審**：確認 cluster=meeting_refreshment 的 hero 素材） |
| **④多角化**（新客 × 新品） | 新市場新產品，ROI 不明，暫不投付費廣告 | — | 🔵 冷 | **不投 FB/IG 導購廣告**；以 SEO 有機觸達為主 | `cultural_venue` | 待 SEO 文章上線後評估 | — |

---

## 各格細節

### ① 滲透（既有企業客 × 既有案型）

**策略**：把已成交的客戶留住、讓他們推薦同事/同業。廣告只打「已知道你的人」，不浪費曝光在陌生客。

| 項目 | 內容 |
|---|---|
| **受眾建法** | 自訂受眾：曾詢價 LINE 名單 + 曾成交 TimeTree 紀錄（待 Phase 4 統一後可自動更新） |
| **文案方向** | 場景式回憶：「上次的論壇茶點，同仁說印象不錯」→ 不硬賣，說場景 |
| **主視覺** | `brand_vip` + `corporate_meeting` cluster，選已知案例（如國泰建設論壇） |
| **廣告動作** | 再行銷，頻率上限 3 次/週，避免騷擾 |
| **landing_slug** | `corporate-catering-tainan`（服務總覽）+ `tainan-corporate-catering-cost`（費用估算） |
| **KPI** | 再詢價率 / 推薦轉介數 |

---

### ② 市場開發（企業新客 × 既有案型）

**策略**：讓還沒聽過 MAPLAB 的企業主、行政、HR 在「搜尋比較期」認識我們。Lookalike 以成交客為種子，職業興趣鎖精準。

| 項目 | 內容 |
|---|---|
| **受眾建法** | Lookalike（1–3%，以成交客為種子）+ 職業興趣（人力資源 / 秘書 / 行政管理 / 企業主 / PMO） |
| **文案方向** | 說場景：「200 人的財富管理論壇，茶點從詢價到進場只要 5 天」—— 具體數字，開放感 |
| **主視覺** | `opening_tea` / `corporate_meeting` cluster，選乾淨橫式、無臉、無浮水印 |
| **廣告動作** | 冷流量進站 → 軟轉換（LINE 加好友 / 詢價頁）|
| **landing_slug** | `corporate-catering-tainan` / `hr-admin-meeting-catering-guide-tainan` |
| **KPI** | 點擊率 / LINE 加好友數 / 詢價數 |
| **⚠️ 待 A0 審** | 確認 `opening_tea` cluster 中是否有 `slot=hero_16x9` + `ad_ok=yes` + `needs_face_crop=no` 的素材 |

---

### ③ 產品開發（老客 × 新案型）

**策略**：老客已信任品牌，引導他們試用還沒點過的案型（會議茶點補充、文化場域）。溫再行銷比冷流量轉換成本低。

| 項目 | 內容 |
|---|---|
| **受眾建法** | 溫再行銷：看過網頁 30 秒以上 / IG 互動過 / 粉專有互動（非成交） |
| **文案方向** | 新案型介紹：「除了論壇茶點，我們也做會議中場的點心補給」—— 不說「不是只做 X」，正向描述新場景 |
| **主視覺** | `meeting_refreshment` / `cultural_venue` cluster，選溫馨細節圖（食物特寫、器皿） |
| **廣告動作** | 軟轉換（詢價頁）或直接引導 LINE |
| **landing_slug** | `meeting-refreshment-catering-tainan`（⚠️ 需確認 live 狀態，見下） / `corporate-tea-party-desserts` |
| **KPI** | 新案型詢價數 / 老客新案型成交率 |
| **⚠️ 待 A0 審** | 1. 確認 `meeting-refreshment-catering-tainan` 是否 live（上次查為 planned_404，若已上線需更新 keyword-map）2. 確認 `meeting_refreshment` cluster 是否有合適 hero 素材 |

---

### ④ 多角化（新客 × 新品/文化場域）

**策略**：文化場域 + 新型客群（藝廊、書店、獨立空間）ROI 尚不明確，付費廣告 CPA 會偏高。先用 SEO 有機觸達，等有數據後再評估是否轉投廣告。

| 項目 | 內容 |
|---|---|
| **廣告動作** | **不投 FB/IG 導購廣告** |
| **替代策略** | SEO 文章（`cultural_venue` cluster）+ IG 有機貼文建品牌形象 |
| **重啟條件** | `cultural_venue` landing page SEO 上線 > 3 個月、有詢價紀錄後，A2 提案給 Owner 評估是否轉投 |
| **⚠️ 待 A0 審** | `cultural_venue` SEO 文章是否已規劃在 GAP 清單中？ |

---

## 素材需求缺口（待 A0 × A4 確認）

| 格子 | 缺口 | 處理建議 |
|---|---|---|
| ② 市場開發 | `opening_tea` cluster 缺 `hero_16x9` + `ad_ok=yes` 素材（待查） | A4 從 Drive 相簿確認是否已有；如無，列入下一輪拍攝清單 |
| ③ 產品開發 | `meeting_refreshment` cluster 素材數量待確認 | 同上 |
| ③ 產品開發 | `meeting-refreshment-catering-tainan` slug live 狀態未確認 | A2 REST 確認 |

---

## 下一步（解鎖 Phase 1 的前置動作）

1. Owner 審定本矩陣（特別是「待 A0 審」格子的策略方向）
2. Owner 確認廣告平台 + 帳號（見 `A2-ad-ops-improvement-plan.md` 待確認事項 #1 #2）
3. A0 × A4 補齊素材缺口
4. A2 將矩陣轉為可機讀的 JSON 物件，供 Phase 1 受眾包規劃腳本讀取

---

## 變更紀錄

| 版本 | 日期 | 變更 | 來源 |
|---|---|---|---|
| v0.1-draft | 2026-07-03 | 初版草案：4 格 × 5 cluster 對應，素材部分待 A0 審 | Owner 指定骨架，A2 填入 |
