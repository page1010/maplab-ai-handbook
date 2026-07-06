# MAPLAB Alt-Text 標準提案（待 Owner 核可）

> **性質：提案稿，不是生產檔。** 未經 Owner 核可前，不得覆寫 `recalls/A2_recall.md`、`skills/maplab-visual-spec.md`、`skills/wp-article-standard.md`、`skills/maplab-photo-sourcing.md`、`skills/gdrive-to-wordpress-upload-guide.md` 等正式檔。
> 作者：A1 系統總管 ｜ 日期：2026-06-30 ｜ 對齊：`skills/brand-voice-guide.md` v1.1、`skills/maplab-visual-spec.md`
> 任務來源：把現有兩套衝突 alt 格式 reconcile 成單一標準（做標準化，非內部二選一）。

---

## 0. 一頁總結（TL;DR）

- **採用單一標準**：`台南{場景}外燴—{現場具體描述}`（即現有 canonical A 式，微調強化），**廢止** B 式 `MAPLAB Kitchen {場景}｜{描述}`。
- **核心理由**：alt 的第一順位是「描述內容＋可及性」，地點＋場景關鍵字前置最有利於圖片／在地搜尋；品牌名放在 alt 開頭既非搜尋詞、又對 screen reader 造成每張圖重複冗餘，且違反品牌語氣「說場景不硬講賣點」。
- **品牌曝光不會消失**：改由「檔名 + caption + title + featured image」承擔，分工更正確。
- **遷移成本最低**：A 式已在 3 個 canonical 來源一致（A2 Conventions Lock v1 / visual-spec / wp-article-standard），只需修正 1 處 gdrive 指南與 1 張舊任務卡即可統一（80/20）。

---

## 1. 研究摘要：10 個權威來源 / 實例的優劣

| # | 來源 | 核心主張 | 優點 | 缺點 / 侷限 |
|---|------|---------|------|------------|
| 1 | **Google Search Central — Image SEO** | 描述要具體（"white running shoes with red soles" 不是 "image of a product"）；別寫 "image of"；別 keyword stuffing；放在相關文字旁 | 最高權威、規則明確、直接對應排名 | 偏英文情境，未給中文長尾與在地寫法 |
| 2 | **Moz / Victorious — Alt Text** | 邏輯地用 1–2 個主關鍵字；過度塞詞＝負面體驗 | 點出「1–2 keyword」這個可操作上限 | 案例通用、非餐飲外燴 |
| 3 | **Yoast — Image SEO** | alt 先服務視障者、再服務 SEO；焦點關鍵字自然出現一次即可 | 把「可及性優先」講清楚，破除純 SEO 思維 | 以 WordPress/Yoast 外掛視角，規則偏保守 |
| 4 | **Ahrefs — Alt Text for SEO** | 簡潔、資訊豐富、關鍵字「只在合理處」加；裝飾圖不必加 alt | 平衡 SEO 與可及性，明確反對全圖都加 | 工具導向（推自家 AI 產生器），需人工複核 |
| 5 | **WebAIM — Alternative Text** | alt 取決於「脈絡」；裝飾／與 caption 重複的圖用 `alt=""`；典型 5–15 字 | 可及性黃金標準，給出「5–15 words」長度錨點 | 不談 SEO 關鍵字策略 |
| 6 | **W3C WAI — alt Decision Tree** | 分「資訊圖 / 裝飾圖 / 功能圖」三類決定 alt | 給出可機械化判斷流程，避免主觀 | 不涵蓋所有情境、不談行銷關鍵字 |
| 7 | **ezCater / Squarespace / owner.com — 餐廳在地 SEO** | 餐飲圖 alt 範例：`fresh seafood pasta at [Restaurant] in [City]`；專做 catering 落地頁可搶 "corporate catering near me" | 給出「品項 + 在 + 餐廳 + 城市」在地句型，正中外燴需求 | 範例偏短、品牌名放句尾（與本標準一致） |
| 8 | **foodphoto.ai — 餐飲在地食物攝影** | 照片質與量是 GBP/Yelp 排名因子；缺 alt 與通用檔名＝浪費 SEO；至少每月更新 | 連結「圖片新鮮度」與在地排名 | 行銷口吻、數據未必可考 |
| 9 | **veroniiiica — 食物 alt 與描述** | 食物 alt 要點出食材／擺盤／可辨識細節；菜單品項照菜單原名 | 食物特寫的描述顆粒度指引 | 偏可及性，未談關鍵字前置 |
| 10 | **fuelyourphotos — 攝影師 29 例** | 描述主體＋情境，不報檔名、不寫 "photo of" | 大量正例可仿寫場景描述 | 通用攝影、非外燴垂直 |

**橫向共識（去蕪存菁後的「標準答案」原則）：**

1. **可及性優先，SEO 其次**：alt 先讓看不到圖的人理解，關鍵字是順帶（來源 1/3/4/5）。
2. **具體名詞勝過空泛形容**：寫得出「長桌茶點分區」就不要寫「精緻擺盤」（來源 1/9/10）。
3. **長度**：screen reader 約 125 字元截斷，典型 5–15 字；中文宜 ≤ 約 30 字（來源 1/2/5）。
4. **關鍵字 1–2 個、自然融入**，禁堆疊（來源 1/2/3/4）。
5. **禁 "圖片／照片／image of"、禁檔名、禁 code**（來源 1/3/10）。
6. **脈絡決定**：裝飾圖或與 caption 重複 → `alt=""`（來源 4/5/6）。
7. **在地句型有效**：場景 + 地點（台南）對在地與圖片搜尋有利；品牌名放句尾或交給 caption（來源 7/8）。
8. **一圖一句、不重複**：每張圖獨特，不照抄 caption（來源 5/8）。

---

## 2. 現有兩套格式的衝突盤點

| | A 式（canonical） | B 式（待廢止） |
|---|---|---|
| 模板 | `台南{場景}外燴—{食物特寫/現場紀錄/桌面佈置}` | `MAPLAB Kitchen {場景}｜{具體描述含長尾關鍵字}` |
| 出處 | `recalls/A2_recall.md`（A2 Conventions Lock v1）、`skills/maplab-visual-spec.md`、`skills/wp-article-standard.md`、`skills/maplab-photo-sourcing.md` | `skills/gdrive-to-wordpress-upload-guide.md`、舊任務卡 `handoff/tasks/T-A2-001.md` |
| 範例 | `台南公司聚餐外燴—大型單位餐會長桌陳列` | `MAPLAB Kitchen 企業茶會｜接待中心茶點桌長桌佈置` |
| 開頭 | 地點＋場景關鍵字（搜尋詞前置） | 品牌名前置 |

**A 式優點**：地點＋場景＋「外燴」長尾關鍵字前置，正中在地圖片搜尋；場景敘事符合品牌語氣「說場景不硬講賣點」；已在 3 處 canonical 一致。
**A 式可改進**：破折號後描述偶爾過於精簡；需明訂「具體名詞、長度上限、裝飾圖規則」。

**B 式缺點（為何不選）**：
- 開頭「MAPLAB Kitchen」不是搜尋者在圖片搜尋會輸入的字，浪費最有價值的前置位置，近似品牌 stuffing（違反來源 1）。
- 每張圖 screen reader 都先念「MAPLAB Kitchen」→ 跨圖重複冗餘（違反 WebAIM 來源 5）。
- 以品牌名開頭＝用 alt 推銷，違反 `brand-voice-guide.md` §二.1「說場景，不硬講賣點」。

**結論**：以 A 式為基底統一，B 式廢止；品牌曝光改由檔名／caption／title 承擔。**大致正確勝過精準錯誤＋80/20**：採已三處一致的 A，只需改 1 指南 + 1 任務卡，遷移成本最低。

---

## 3. MAPLAB Alt-Text 單一標準（提案）

### 3.1 結構模板

```
台南{場景}外燴—{現場具體描述}
```

- `台南`：地點固定前置（在地搜尋錨點）。
- `{場景}`：場景／受眾關鍵字，**對齊該頁主關鍵字**（企業／公司聚餐／企業茶會／婚禮／週歲派對／品牌記者會／學術會議／藝文特展…）。
- `外燴`：品類詞，構成長尾「台南＋場景＋外燴」。
- `—`：全形破折號分隔關鍵字段與描述段。
- `{現場具體描述}`：用**具體名詞**描寫桌面／食物／佈置／動線，約 10–20 中文字。

### 3.2 內容規則

1. **描述先行、關鍵字自然融入**：先讓人「看見」現場，關鍵字不堆疊（1–2 個即可）。
2. **場景關鍵字對齊頁面主關鍵字**，地點固定「台南」。
3. **用具體名詞，不用空泛形容**（對齊 brand-voice §二.2）：長桌茶點分區 / 抓周餐桌 / 主廚現切，而非「精緻 / 質感 / 超好吃」。
4. **長度 ≤ 約 30 中文字**（≈ <125 字元），一句講完。
5. **一圖一句、每圖獨特**，不照抄 caption 原文。
6. **純裝飾／與 caption 重複的圖**：用 `alt=""`（W3C/WebAIM）。
7. **受眾語氣微調**（對齊 brand-voice §十一）：藝文特展用克制安靜詞、學術會議可帶雅致詞，但仍以場景具體名詞為主、不浮誇。
8. **品牌名不進 alt 開頭**；品牌曝光交給：檔名 `maplab-{場景}-{描述}.webp`、caption、title、featured image。

### 3.3 範例（5–8 個，涵蓋主要場景）

| 場景 | Alt 範例 |
|------|---------|
| 企業茶會 | `台南企業茶會外燴—接待中心長桌茶點與飲品分區` |
| 公司聚餐 | `台南公司聚餐外燴—大型單位餐會長桌菜色陳列` |
| 婚禮 | `台南婚禮外燴—戶外證婚區甜點桌與鮮花佈置` |
| 週歲派對 | `台南週歲派對外燴—抓周餐桌與手指食物拼盤` |
| 品牌記者會 | `台南品牌記者會外燴—產品發表餐檯與招待飲品` |
| 食物特寫 | `台南企業外燴—主廚現切牛排佐季節時蔬擺盤` |
| 藝文特展（克制） | `台南藝文特展外燴—安靜陳列的茶點與素色器皿` |
| 學術會議（雅致） | `台南學術會議外燴—茶歇品茗小點與咖啡區` |

### 3.4 禁忌（Red Flags）

- ❌ 開頭放品牌名「MAPLAB Kitchen」（B 式問題）。
- ❌「圖片／照片／image of／picture of」。
- ❌ 關鍵字堆疊：`台南外燴台南美食台南buffet台南宴會`。
- ❌ 空泛形容詞：精緻／質感／用心／高品質／超好吃（對齊 brand-voice §三禁用/少用）。
- ❌ 品牌禁用字：最頂／超值／CP值爆高／佛心／名額有限（brand-voice §三）。
- ❌ 寫檔名或副檔名（如 `IMG_2034.jpg` / `.webp`）。
- ❌ 全站／全文同一句 alt（每圖需獨特）。
- ❌ 照抄 caption 原文。

### 3.5 5 秒自檢

> 把這句 alt 念出來，閉上眼，是否「看得見」這張圖的場景？地點＋場景關鍵字是否在前？有沒有空泛形容詞或品牌名開頭？超過 30 字了嗎？

---

## 4. 若 Owner 核可——最小遷移清單（降低未來重工）

> 核可後再執行，本提案不先動。

1. `skills/gdrive-to-wordpress-upload-guide.md`：把 B 式改為指向本標準（A 式）。
2. `handoff/tasks/T-A2-001.md`：Alt text 格式那行同步為本標準。
3. `recalls/A2_recall.md` §D：把「已知衝突待 Owner 裁示」改為「已統一，gdrive 式作廢」。
4. （可選）把本標準濃縮為一段，回灌 `skills/maplab-visual-spec.md` §SEO Alt Text 與 `skills/wp-article-standard.md`，三處措辭完全一致，避免再次漂移。

**這是那個「一個小改動明顯降低未來重工」**：衝突已掛在 A2 recall「待 Owner 裁示」多時，每個碰 alt 的 agent 都要重新判斷一次；統一後一次性消除。

---

## 來源 URL

- Google Search Central — Image SEO Best Practices: https://developers.google.com/search/docs/appearance/google-images
- Moz / Victorious — Alt Text: Its Importance For SEO: https://victorious.com/blog/alt-text/
- Yoast — Image SEO: alt & title text: https://yoast.com/image-seo-alt-tag-and-title-tag-optimization/
- Ahrefs — Alt Text for SEO: https://ahrefs.com/blog/alt-text/
- WebAIM — Alternative Text: https://webaim.org/techniques/alttext/
- W3C WAI — An alt Decision Tree: https://www.w3.org/WAI/tutorials/images/decision-tree/
- ezCater — SEO best practices for small restaurants: https://www.ezcater.com/lunchrush/restaurant/8-seo-best-practices-for-small-restaurants/
- foodphoto.ai — Local SEO Food Photography: https://foodphoto.ai/local-seo-food-photography
- veroniiiica — Alt Text and Image Descriptions for Food: https://veroniiiica.com/alt-text-and-image-descriptions-for-food/
- fuelyourphotos — 29 Examples of Great Alt Text for Photographers: https://www.fuelyourphotos.com/alt-text-for-photographers/
- Squarespace — SEO Tips for Restaurants and Food Businesses: https://www.squarespace.com/blog/food-business-and-restaurant-seo
