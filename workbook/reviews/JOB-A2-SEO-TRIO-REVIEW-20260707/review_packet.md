# SEO 三人小組評審包（2026-07-07）

你是本次評審的其中一位（Codex 或 Antigravity），角色是**唯讀評審**：找盲點、給專業意見，**不要修改任何檔案，不要建議自己去執行變更**——所有改動與整合決策由 Claude（A2）做。請針對下面三個問題直接給意見，不需要重複背景資料。

---

## 背景：MAPLAB Kitchen 廣告漏斗矩陣（4 份草案文件摘要）

### 1. docs/ad-funnel-battle-plan.md（v0.1-draft，廣告漏斗作戰計畫）
- 現況：Google PMax 已停用（黑箱無法做 message-match，外燴是「高考慮×LINE詢價」產品不適合黑箱優化）；Meta 目前全是 C 端冷層（週歲/高收入媽媽），溫層 retarget 完全空白（最痛缺口）；無熱層收割素材。
- 三層漏斗：冷層 Meta 認知（KPI=ThruPlay/CPM）→ 溫層 retarget（KPI=CTR/加LINE，現況空白）→ 熱層 Google 搜尋收割（KPI=詢價轉換率）。
- 8 情境對照表：B 端 5 情境（B1高管接待/B2採購/B3 HR行政茶會/B4公關品牌/B5論壇會展）+ C 端 3 情境（C1慶生/C2入厝/C3壽宴），每情境定義 Meta受眾+Google關鍵字+landing+KPI+UTM。
- 第一個試跑（FDE）選 B3 HR行政茶會線：文章已上線（WP 1992）、landing已live（corporate-tea-party-desserts）、Google已在收「台南茶會點心推薦」等字。**兩週試跑計畫：Week1 建冷受眾包（草案日預算 NT$150/天，本次 Owner 已定案改為 NT$100/天）+ Google加關鍵字；Week2 補溫層 + 數據評估。**

### 2. docs/ansoff-mot-audience-matrix.md（安索夫矩陣 × MOT × 受眾溫度）
- 安索夫四格對應廣告動作：①滲透（既有客×既有品，熱層嚴格再行銷）②市場開發（新客×既有品，冷層Lookalike+職業興趣）③產品開發（老客×新案型，溫再行銷）④多角化（新客×新品，**不投付費廣告，SEO有機觸達優先**）。
- 實跑教訓：PMax 已停用驗證「多角化不投廣告」策略正確；外燴的高考慮特性不適合黑箱優化，須回到分受眾×分廣告×分landing。

### 3. docs/A2-ad-ops-improvement-plan.md（A2 廣告能力進化計畫）
- 5 Phase 路徑：Phase 0 建矩陣物件（已完成草案）→ Phase 1 唯讀 Ads API 盤點（未開始，Meta/Google API 未接通）→ Phase 2 廣告發布閘門 ad_publish_gate.py（比照 seo_publish_gate.py，查素材合規/預算上限/受眾重疊/矩陣對齊）→ Phase 3 經閘門批量寫入 → Phase 4 戰情中心統一 Meta/Google/GSC/TimeTree 資料。
- 核心優勢主張：「又快又安全」勝過競品的 fire-and-forget，靠獨立驗證閘門 + 素材表自帶合規欄位（ad_ok/needs_face_crop）+ maker/checker 架構。

### 4. docs/real-cases-to-seo-matrix.md（6月真實案例→SEO矩陣，v1.0，2026-07-04）
- 10 場 6 月真實案例分類進 cluster（meeting_refreshment/opening_tea/brand_vip/corporate_forum），最高優先兩場會議案例（富信飯店社工公會、大台南會展工研院）直接對上 Google 高意圖字詞。
- **本文件當時提出 3 個內容缺口「待 A0/Owner 確認」**（見下方獨立章節，這是本次評審的重點之一）。

### 補充：docs/ad-buildout-plan.md（v1.1，2026-07-05，比上面 4 份文件更新一天）
Meta 受眾/素材/佈局執行計畫，P2 C端擴充段落寫著：**「Owner 定案 cluster 預設（2026-07-05）：婚禮線開；性別派對併入慶生線；遊艇先不做」**——這其實已經是 Owner 隔天做的決定，但沒有回填進上面 4 份「矩陣草案」文件，所以矩陣文件現在跟這個決定不一致。

---

## 三個 Landing 缺口：原始討論脈絡（為什麼要/為什麼不要）

### 缺口 1：婚禮 landing
- **2026-07-04（real-cases-to-seo-matrix.md）提出時的狀態**：不確定站上是否已有婚禮 landing，東門教會證婚案例卡在「待確認」。
- **交叉查核發現（重要）**：`docs/seo-keyword-map.md`（2026-06-30 建立，比上面早）早就列出至少 5 個婚禮相關 slug 為 `live_referenced`：`wedding-catering-vs-banquet-tainan`、`tainan-wedding-welcome-canapes`、`tainan-wedding-celebration-party-catering`、`tainan-small-wedding-catering`、`tainan-outdoor-wedding-catering`、`tainan-wedding-catering-cost`。2026-07-07 A2 對 58 篇既有文章做 WP REST 全站掃描時，也實際確認了「台南證婚派對外燴」「台南戶外婚禮外燴」「台南小型婚禮外燴推薦」「台南婚宴外燴費用完整指南」「台南婚禮迎賓茶點外燴」等文章確實 live。**婚禮 landing 其實早就存在，不是空缺。**
- **2026-07-05（ad-buildout-plan.md）Owner 決定**：✅ 開。理由：「已有 `maplab-outdoor-wedding-catering-venue.webp` 可用；戶外婚禮場景差異化強」。已配好對應受眾包 `cold-c-wedding`（生命里程碑：訂婚/結婚，年齡25-40）+ 熱層字詞（台南戶外婚禮外燴、台南婚禮茶點）+ landing slug `outdoor-wedding-catering-venue`。

### 缺口 2：派對（性別揭曉/主題派對）landing
- **2026-07-04 提出時的狀態**：「歡樂時光—性別派對」案例的 landing 未知，選項是併入慶生線或獨立建頁。
- **交叉查核發現**：`docs/seo-keyword-map.md` 已列 `gender-reveal-party-tips`（性別揭曉派對）為 `live_referenced`，且週歲/慶生類文章（`catering-one-year-old-party-tainan` 等）已 `verified`。
- **2026-07-05 Owner 決定**：性別派對**不獨立建受眾包**，併入 `cold-c-birthday`（慶生線）定向一起涵蓋。理由：「性別派對不獨立受眾包，語氣友善即可，受眾定向沒有差異化必要」。

### 缺口 3：遊艇外燴 landing
- **2026-07-04 提出時的狀態**：「遊艇氣泡水」案例屬 niche 場景，搜尋量未知，選項是先評估關鍵字量，或先當內文插圖不建獨立頁。
- **2026-07-05 Owner 決定**：❌ **先不做**。理由：「受眾規模太小、無對應 landing；此版本排除，待日後評估」。這是三個缺口中唯一「真的沒有既有頁面、且決定不建」的一個。

---

## 品牌語氣與視覺（skills/brand-voice-guide.md + skills/maplab-visual-spec.md 摘要）

**核心人格**：自然、溫暖、安靜、細緻、有質感、專業、穩定、有分寸；不浮誇、不硬推銷、不靠低價。

**語氣總原則**：說場景不硬講賣點；用具體名詞不用空泛形容；保持開放感不把話說死（禁「一定/保證/最適合/絕對/唯一/最好」）；不用說服式對比句型（禁「不是…而是…」等）；不過度用力成交；有價格邏輯但不進入廉價感。

**婚禮客戶專屬語氣**（brand-voice-guide §八）：在意氛圍、記憶點、風格一致、儀式感、不想俗氣；語氣浪漫但克制、有美感、有場景感、不過度煽情。例句：「婚禮外燴比較像是整體氛圍的一部分，不只是讓賓客吃飽而已。」

**品牌色票（7色）**：奶油白 `#FAF7F2`（主背景）、暖米 `#EDE5D8`（次背景）、深橄欖 `#3A3A2E`（主文字）、棕褐 `#7A5C3E`（CTA強調）、鼠尾草 `#8FA68E`（輔助）、裸粉 `#D9C4B8`（**婚禮/週歲場景專用**，搭配暖米）、炭黑 `#2C2C2C`（線條）。禁用高飽和螢光色、大面積純黑、單畫面超過3主色。

**Owner 本次指示**：landing page 不限定用 Elementor 做（「可以不要 Elementor 也沒關係」），只要符合品牌語氣+品牌色即可。

---

## 請評審回答三個問題

1. **矩陣草案的盲點/風險**：上述 4 份矩陣文件 + 補充的 ad-buildout-plan.md，你看到哪些邏輯漏洞、風險、或跟現實不符的地方？（例如：受眾規模估計是否合理、KPI 設定是否可行、是否有沒考慮到的競爭/合規風險）

2. **B3 試跑方案合理性**（日預算已定案 NT$100/天，不是草案的 150）：以 NT$100/天跑 `cold-b-meeting-corp` + `cold-b-meeting-edu` 兩個冷受眾包、兩週試跑、目標是「溫層CTR>2%、熱層詢價>3%才複製結構」——這個預算/時間/KPI組合合理嗎？有沒有更好的配置建議（例如兩個受眾包要不要拆預算、兩週夠不夠看出訊號）？

3. **三個 landing 各自「要做/不做」的專業意見**：針對婚禮（已決定開，已有既有頁面+新素材）、性別派對（已決定併入慶生線不獨立）、遊艇（已決定不做，受眾太小），請給出你自己的專業判斷——同意還是不同意 Owner 07-05 的決定？有沒有被忽略的角度？

請用繁體中文回答，直接給結論與理由，不需要重複我提供的背景資料。
