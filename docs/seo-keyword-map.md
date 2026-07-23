# MAPLAB SEO 關鍵字／內容地圖（Canonical 單一真相）

> **用途：寫任何 SEO 文章「前」必讀的真相層。** 先讀本圖 → 挑 GAP / 確認沒有互搶 → 按計畫寫，不再每次從頭抓全站。
> 維護：A2 SEO & Ads ｜ 建立：2026-06-30 ｜ 最後更新：2026-07-07（婚禮/會議茶點/週歲群組正式標記 Pillar/Child，見各群組表格）｜ 對齊：`recalls/A2_recall.md`（Conventions Lock v1）、`projects/seo-ads-agent.md`、`workbook/reviews/JOB-A2-SEO-CATERING-COMPETITOR-MATRIX-20260617/article_matrix_seed.md`
> 與其他文件衝突時：**live WP REST > 本圖 > 其他 repo 紀錄**。

---

## 0. 證據分層（每一格都標）

| 標記 | 意義 |
|---|---|
| `verified_public` | 2026-05-11 公開 REST／前台 head 實查過（slug/title/schema 確認 live） |
| `live_referenced` | slug 在 repo 真實內容被多次引用，**極可能 live**，但本輪未經 REST 重查 |
| `planned_404` | 2026-05-11 REST 查無、前台 404，**禁當 live target** |
| `reasonable_inference` | 由 slug 語意/業務推論，需 REST 或 Rank Math 確認 |
| `needs_owner_evidence` | 缺資料，需 Owner / authenticated REST |

> ⚠️ 本圖的「主/次關鍵字」對多數文章是從 **slug 語意 + 已知 title 推論**。要 100% 精準（含 Rank Math focus keyword 與分數），需 authenticated WP REST 跑一次 §6 的 Codex 盤點，回填本圖。

---

## 1. 站台結構（verified_public，2026-05-11）

- 公開 REST：**6 pages + 57 posts**（B2B 入口是「文章 post」，不是 page）。
- 首頁 `page_on_front` = **1250**，title `台南外燴推薦｜週歲派對・婚禮・企業活動｜MAPLAB Kitchen`。
- Rank Math PRO 在前台啟用（輸出 meta/schema）；私有分析端點需 WP auth（401）。**訂閱已取消、設定凍結**（非編輯範圍）。
- ⚠️ 先前任務卡寫「8 landing pages」是錯的 → 正解是 **6 pages + 57 posts**。

### 6 個 Pages（verified_public）

| ID | Slug | Title | 角色 |
|---:|---|---|---|
| 1250 | `homepage-v2`（首頁） | 台南外燴｜MAPLAB Kitchen CATERING SERVICE | 首頁／泛字總入口 |
| 44 | `about-us-maplabkitchen` | About us | 品牌 |
| 209 | `join-maplab-catering-partner` | 外燴加盟合作平台-加入我們 | 加盟招募 |
| 15 | `tainan-party-venue` | 派對流程怎麼規劃？場地、餐點、預算一次搞懂 | 派對規劃（⚠️ venue 字與 post 互搶，見 §5） |
| 46 | `工商代購服務`（中文 slug） | 工商代購服務 | 周邊服務 |
| 1674 | `privacy-policy` | 隱私權政策 | 法務 |

---

## 2. 關鍵字宇宙（台南外燴，依搜尋意圖分群）

> 量級用質性標記（高/中/低 intent + 競爭），不假造精確搜尋量；要精確量再用 GSC/Ads keyword planner 回填。

| 群組 | 代表關鍵字 | 意圖 | 商業價值 | 現況覆蓋 |
|---|---|---|---|---|
| **核心泛字** | 台南外燴、台南外燴推薦、外燴 | 高量、高競爭、意圖雜 | 中（難排、轉換雜） | 首頁 + `tainan-catering-guide` + `corporate-catering-tainan` |
| **場域 venue** | 大臺南會展中心外燴、台南美術館外燴、成大會議茶點、南科外燴、飯店會議外燴 | 中量、**高意圖**、低競爭 | **高**（在地+高意圖好成交） | 部分（ICCTN/美術館有；南科/成大/飯店 GAP） |
| **買家角色** | 行政外燴推薦、HR 活動餐點、公關公司外燴、秘書 訂 會議茶點 | 低量、**極高意圖** | **高**（B2B 決策者） | **GAP**（無專頁） |
| **活動類型** | 開幕茶會、會議茶點、研討會外燴、記者會茶點、尾牙、週歲派對、婚宴、家庭派對 | 中量、高意圖 | 高 | 覆蓋多（開幕/茶點/婚禮/週歲都有），但分散+互搶 |
| **菜單 menu** | 茶點外燴、一口點心、甜點桌、午餐餐盒、咖啡茶點、canapes | 中量、中意圖 | 中（輔助頁、內鏈樞紐） | 部分（custom-menu/menu-guide；canapes 僅婚禮版） |
| **費用 / FAQ** | 台南外燴費用、外燴怎麼估價、會議茶點份量、外燴 vs 餐廳 | 高量、研究意圖 | 中（養信任、攔截比價） | 覆蓋多但**互搶**（≥3 個 cost 頁，見 §5） |
| **案例 / 證據** | 台南企業外燴案例、品牌活動外燴案例、會議茶點案例 | 低量、高信任 | 高（轉換臨門 + 內鏈權威） | 少（ICCTN/美術館案例；多數活動無案例頁） |
| **品牌 / 周邊** | MAPLAB、牛肉湯故事、花藝合作、加盟 | 品牌字 | 低（護城河） | 有（about/牛肉湯/花藝/加盟） |

---

## 3. 文章 → 關鍵字 映射（live_referenced，需 §6 REST 確認 title/分數）

> 以下 slug 皆在 repo 真實內容多次引用（`live_referenced`），主/次關鍵字由 slug 語意推論。標 ✅ 者另有 2026-05-11 前台實查（`verified_public`）。

### 核心 / B2B 企業
| Slug | 主關鍵字（推論） | 次關鍵字 | 證據 |
|---|---|---|---|
| `corporate-catering-tainan` (586) | 台南企業外燴推薦 | 品牌活動/展會/記者會 | ✅ verified |
| `tainan-catering-guide` | 台南外燴指南/推薦 | 外燴總覽 | live_referenced |
| `tainan-waihui-changdi-tuijian` | 台南外燴場地推薦 | 場地 | ⚠️ 與下列重複 |
| `tai-nan-wai-hui-chang-di-tui-jian` | 台南外燴場地推薦 | 場地 | ⚠️ **疑似重複頁**（見 §5-3） |

### 場域 venue / 案例
| Slug | 主關鍵字 | 證據 |
|---|---|---|
| `icc-tainan-catering` (1829) | 大臺南會展中心外燴 | ✅ 2026-06-15 publish |
| `daxin-art-museum-opening-catering` | 台南美術館開幕外燴 | live_referenced |
| `vip-expo-catering-business-meeting` | 展覽/VIP 商務接待外燴 | live_referenced |
| `tainan-catering-venue-7` | 台南外燴場地（7 選） | live_referenced ⚠️ venue 互搶 |
| `tainan-catering-venue-selection-2026` | 台南外燴場地選擇 2026 | live_referenced ⚠️ venue 互搶 |
| `tainan-catering-venue-guide` | 台南外燴場地指南 | live_referenced ⚠️ venue 互搶 |

### 開幕 / 品牌 / ESG
| Slug | 主關鍵字 | 證據 |
|---|---|---|
| `tainan-corporate-opening-tea-catering` (1205) | 台南企業開幕茶會外燴 | ✅ verified |
| `brand-esg-catering-service` (945) | 品牌 ESG 活動外燴 | ✅ verified |
| `esg-event-catering-tainan` | ESG 活動外燴 台南 | live_referenced ⚠️ 與 brand-esg 互搶 |
| `tainan-launch-event-catering` | 台南產品發表/launch 外燴 | live_referenced |
| `business-opening-party-ideas` | 開幕活動點子 | live_referenced |
| `tainan-opening-houseparty-catering` | 台南開幕/house party 外燴 | live_referenced |
| `press-conference-catering` | 記者會茶點外燴 | live_referenced |

### 會議茶點 — Pillar/Child 已定案（2026-07-07 SEO 三人小組覆核）

| Slug | 角色 | 主關鍵字 | 證據 |
|---|---|---|---|
| `corporate-tea-party-desserts` (924) | **★ Pillar** | 企業茶會點心外燴 | ✅ verified；B3 廣告漏斗主 landing |
| `corporate-tea-party-catering-tips` | Child（tips 子意圖） | 企業茶會外燴 tips | live_referenced，內容轉「操作技巧」角度，內鏈回 924 |
| `tainan-corporate-tea-catering` | Child（在地子意圖） | 台南企業茶點外燴 | live_referenced，內容強化「台南在地」角度，內鏈回 924 |

> 決策：保留 924 當 pillar，其餘兩篇轉子意圖（tips / 在地）並內鏈支援，不合併、不 301。

### 週歲 / 彌月 / gender reveal — Pillar/Child 已定案（2026-07-07）

| Slug | 角色 | 主關鍵字 | 證據 |
|---|---|---|---|
| `catering-one-year-old-party-tainan` (498) | **★ Pillar**（週歲/性別派對共用） | 台南週歲派對外燴 | ✅ verified；已補「性別揭曉派對外燴」H2 段落草稿，見 `workbook/outputs/seo-gap-drafts/gender-reveal-section-catering-one-year-old-party-tainan.md` |
| `tainan-full-moon-baby-catering` | 獨立主題（彌月，非週歲） | 台南彌月外燴 | live_referenced，主題不同不合併 |
| `gender-reveal-party-tips` | Child（獨立 SEO 頁保留，廣告受眾不拆） | 性別揭曉派對 | live_referenced；07-07 決策：**不獨立 Meta 受眾包**，併入 `cold-c-birthday`；SEO 頁本身保留 |

### 婚禮 — Pillar/Child 已定案（2026-07-07 SEO 三人小組覆核，原「⚠️ 群內互搶高」已解決）

| Slug | 角色 | 主關鍵字 | 證據 |
|---|---|---|---|
| `tainan-outdoor-wedding-catering` (1215) | **★ Pillar** | 台南戶外婚禮外燴 | ✅ verified_public（2026-07-07 REST 現查）；對上 Meta 廣告 `cold-c-wedding` 熱層字詞；草稿見 `workbook/outputs/seo-gap-drafts/wedding-pillar-consolidation-tainan-outdoor-wedding-catering.md` |
| `wedding-catering-vs-banquet-tainan` (238) | Child（決策比較型） | 婚禮外燴 vs 婚宴 | ✅ verified_public |
| `tainan-wedding-welcome-canapes` (1217) | Child（菜單子項型） | 台南婚禮迎賓點心/canapes | ✅ verified_public |
| `tainan-wedding-celebration-party-catering` (1220) | Child（形式區隔型） | 台南婚禮派對外燴 | ✅ verified_public |
| `tainan-small-wedding-catering` (1213) | Child（規模區隔型） | 台南小型婚禮外燴 | ✅ verified_public |
| `tainan-wedding-catering-cost` (1218) | Child（費用型，維持獨立不合併） | 台南婚禮外燴費用 | ✅ verified_public |

> 決策：pillar 頁補開場段落 + 文末 cluster 連結區塊（5 篇子頁一次到位，不新開 slug）。⚠️ 修正：廣告文件（`ad-funnel-battle-plan.md`/`ad-buildout-plan.md`）原寫的 landing slug `outdoor-wedding-catering-venue` 經 REST 查證回 404，實際應為 `tainan-outdoor-wedding-catering`，待廣告文件同步修正。

### 派對 / 家庭 / 其他活動
| Slug | 主關鍵字 | 證據 |
|---|---|---|
| `tainan-birthday-party-catering` | 台南生日派對外燴 | live_referenced |
| `tainan-family-gathering-catering` | 台南家庭聚會外燴 | live_referenced |
| `tainan-corporate-gathering-catering` | 台南企業聚餐外燴 | live_referenced |
| `tainan-anniversary-catering` | 台南週年慶外燴 | live_referenced |
| `tainan-picnic-catering` | 台南野餐外燴 | live_referenced |
| `tainan-year-end-party-catering-2026` | 台南尾牙外燴 2026 | live_referenced |

### 菜單 / 流程 / 費用 / FAQ
| Slug | 主關鍵字 | 證據 |
|---|---|---|
| `tainan-custom-catering-menu` | 台南客製外燴菜單 | live_referenced |
| `tainan-catering-menu-guide` | 台南外燴菜單指南 | live_referenced |
| `tainan-catering-service-process` | 台南外燴服務流程 | live_referenced |
| `tainan-catering-cost-guide` | 台南外燴費用 | live_referenced ⚠️ cost 互搶 |
| `tainan-corporate-catering-cost` | 台南企業外燴費用 | live_referenced ⚠️ cost 互搶 |
| `tainan-catering-faq` | 台南外燴常見問題 | live_referenced |
| `tainan-catering-vs-restaurant` | 台南外燴 vs 餐廳包廂 | live_referenced（post 1231）|

### 品牌 / 周邊 / 制度
| Slug | 主關鍵字 | 證據 |
|---|---|---|
| `tainan-beef-soup-story-kinguang` | 台南牛肉湯故事（品牌） | live_referenced |
| `florist-partners-tainan` | 台南花藝合作夥伴 | live_referenced |
| `policy-cancellation` | 定金/取消條款（post 1027） | live_referenced |

> 上述約 40 個 slug + 6 pages ≈ 已涵蓋全站絕大多數。**剩餘補到 57 篇的完整列、每篇 Rank Math focus keyword 與分數，由 §6 Codex authenticated REST 回填。**

---

## 4. 已知 404 — 禁當 live target（planned_404，2026-05-11 REST 實查）

`catering-corporate-tainan`、`catering-birthday-party-tainan`、`catering-wedding-tainan`、`opening-event-catering-tainan`、`meeting-refreshment-catering-tainan`、`brand-event-catering`、`school-event-catering-tainan`

> 這些是舊 workbench 規劃 slug，REST 查 0、前台 404。**新文章內鏈一律用 `[INTERNAL_LINK_RECHECK_REQUIRED]` 佔位，verify live 後才連；不可連這 7 個。**

---

## 5. Cannibalization（互搶）信號 — 待 §6 REST 確認後處理

> 多篇搶同一關鍵字/意圖會稀釋排名。以下為**高信心信號**（同意圖多 slug），確切排名重疊需 GSC query 重疊資料佐證。

1. **場地 venue 群（最嚴重）**：`tainan-catering-venue-7` + `tainan-catering-venue-selection-2026` + `tainan-catering-venue-guide` + page `tainan-party-venue`（15）→ **4 個頁面搶「台南外燴場地」**。建議：選 1 篇當 pillar，其餘改寫成不同子意圖（場地清單 vs 場地挑選法 vs 派對流程）或 301 合併。
2. **費用 cost 群**：`tainan-catering-cost-guide`（泛）vs `tainan-corporate-catering-cost`（企業）vs `tainan-wedding-catering-cost`（婚禮）→ 企業/婚禮分眾合理，但泛字 cost-guide 可能吃掉分眾頁。建議：cost-guide 當 pillar，分眾頁強化各自 modifier 並互鏈。
3. **疑似重複頁（近確定）**：`tainan-waihui-changdi-tuijian` 與 `tai-nan-wai-hui-chang-di-tui-jian` → **同一主題「台南外燴場地推薦」兩個拼音 slug**。多半是重複/誤建，優先 §6 確認後 301 其一。
4. **企業茶會群**：`corporate-tea-party-desserts`（924, hero）vs `corporate-tea-party-catering-tips` vs `tainan-corporate-tea-catering` → 3 篇搶「企業茶會/茶點」。保留 924 當 pillar，其餘轉子意圖（tips / 在地）或內鏈支援。
5. **ESG/品牌**：`brand-esg-catering-service`（945, hero）vs `esg-event-catering-tainan` → 保留 945，後者轉「ESG 專項」子角度或合併。

---

## 6. 高價值 GAP 規劃（Top 5）— 有 Drive 素材、無現有 owner

> Drive 母夾「2026maplab外燴紀錄」(`1pKfGSOZXBpG7qXcJrW5T7aoHX4nqB1Tt`) 持續新增 dated 案例夾，是零外拍成本的視覺素材。

### GAP-1　飯店場域會議茶點案例（venue + 案例，雙缺）
- **為什麼**：venue 字高意圖低競爭；目前無「飯店內會議」案例頁。
- **主關鍵字**：台南飯店會議茶點外燴｜**次**：富信飯店/會議茶歇/社團法人活動餐點
- **素材**：Drive `20260614富信飯店-社工公會會議`(`1A_OOrIm9ATvqc_D2E_NY7T8LnQ2DTJKX`)
- **內鏈**：→ `corporate-tea-party-desserts`、`corporate-catering-tainan`、`icc-tainan-catering`

### GAP-2　開幕茶會案例 ×2（活動類型 + 案例）
- **為什麼**：`tainan-corporate-opening-tea-catering` 是指南型，缺真實案例佐證；兩場新開幕素材現成。
- **主關鍵字**：台南開幕茶會外燴案例｜**次**：品牌開幕/店面開幕/貴賓接待
- **素材**：Drive `20260614-醞舞流舞蹈教室開幕`(`1rkCIgvVgWb4sUc9TwXbMRTPB0EUv8ndx`)、`20260621說事實木地板開幕`(`1KoC_rBsbVhR7OsKbw64pMxruzA3jqjY0`)
- **內鏈**：→ `tainan-corporate-opening-tea-catering`、`business-opening-party-ideas`

### GAP-3　買家角色 guide：行政/HR/秘書 如何規劃會議茶點（買家角色，全缺）
- **為什麼**：極高意圖 B2B 決策者字，全站無對應頁；競品（Fooditude/Social Pantry）都有 buyer-role 內容。
- **主關鍵字**：行政外燴推薦 / HR 活動餐點規劃｜**次**：會議茶點怎麼訂/份量/預算審核/approval-ready
- **素材**：通用企業案例圖（可重用 ICCTN / 富信）
- **內鏈**：→ `corporate-catering-tainan`、`tainan-corporate-catering-cost`、`corporate-tea-party-desserts`

### GAP-4　南科 / 成大 在地產業頁（場域，缺）
- **為什麼**：南科科技公司、成大會議是台南高消費 B2B 客群，無在地頁。
- **主關鍵字**：南科企業外燴 / 成大會議茶點｜**次**：科技公司活動餐點/研討會
- **素材**：`needs_owner_evidence`（先確認 MAPLAB 服務範圍與是否有實際案例，再寫；無案例先做指南型）
- **內鏈**：→ `corporate-catering-tainan`、`icc-tainan-catering`

### GAP-5　一口點心 / canapes 站立式接待菜單頁（菜單，半缺）
- **為什麼**：canapes 僅有婚禮版（`tainan-wedding-welcome-canapes`），缺企業/酒會通用版；是 menu 內鏈樞紐。
- **主關鍵字**：台南一口點心外燴 / canapes 接待｜**次**：站立式活動/酒會/finger food
- **素材**：食物特寫類（多數案例夾可選）
- **內鏈**：→ `corporate-tea-party-desserts`、`vip-expo-catering-business-meeting`

> 優先序：先清 §5 互搶（不花外拍、直接提升現有資產）→ 再做 GAP-1/2（素材現成、可配 Google Ads 開幕字）→ GAP-3 買家角色 → GAP-4/5。**全部走 draft，發布前出 owner_approval_card。**

---

## 7. Codex 盤點 dispatch（maker；A2 = checker）

> 本圖的「精準層」由 Codex 在 Mac mini 用 authenticated WP REST 跑一次回填。A2 負責驗收與更新本圖。

**要 Codex 做的（read-only，不改站）：**
1. `GET /wp-json/wp/v2/posts?per_page=100&_fields=id,slug,title,link,categories,date,modified` → 匯出**完整 57 篇**真實清單（id/slug/title/分類/日期）。
2. 對每篇 `GET /wp-json/rankmath/v1/getMetaBulk`（或逐篇 meta）→ 抽 **Rank Math focus keyword + SEO 分數**。
3. （若可）`GET /rankmath/v1/an/postsRows` → 各篇 GSC 排名/點擊，標出實際 query 重疊（確認 §5 互搶）。
4. 產出 CSV：`id, slug, title, category, focus_keyword, seo_score, top_query, clicks, impressions`。

**回填本圖：** 用 CSV 補齊 §3 全 57 列 + 把 `live_referenced` 升級為 `verified`，§5 互搶用真實 query 重疊確認，刪除任何查無的 slug。

**邊界：** 不發布、不改 Rank Math 付費/設定、不改 Ads；secret 不落地（依 `skills/credentials/wordpress-api.md` + Notion vault 路由）。

---

## 8. 維護規則

- 每次寫新文章**前**讀本圖 → 確認主關鍵字無 §5 互搶 → 挑 §6 GAP 或強化現有 → 內鏈用佔位待 verify。
- 每次 §7 Codex 盤點後、或新增/合併文章後，更新本圖並 `checkpoint.sh`。
- 與 live WP 衝突時以 REST 為準，回寫修正本圖。
- 疑似重複 / 互搶 / 死連結**先進 §9 封存觀察區，不即刪**；確認無流量影響再決定 301/移除。

---

## 9. 封存觀察區（Archive & Observe）

> **治理原則：先封存、後觀察、再決定 —— 不即刪，避免誤殺。** 標記日起約 2 個月回看；只有在「判定依據」的訊號成立（多為 GSC 無流量/無排名）後，才 301 或從舊文件移除。回看前一律**保留現狀**。
> 標記日：2026-07-23 ｜ 預計回看：2026-09-23 ｜ 回看時先跑 §7 Codex 盤點取得 GSC/Rank Math 實據再判。

| # | 項目 | 類型 | 判定依據（成立才動手） | 回看前處置 |
|--:|---|---|---|---|
| 1 | `tai-nan-wai-hui-chang-di-tui-jian`（vs `tainan-waihui-changdi-tuijian`） | 疑似重複頁（兩個拼音 slug 同主題） | REST 確認兩頁皆 live；GSC 其一 0 點擊/0 排名 → 301 到有流量的那頁 | 保留兩頁，不 301 |
| 2 | 場地 venue 4 頁：`tainan-catering-venue-7` / `-venue-selection-2026` / `-venue-guide` / page `tainan-party-venue` | 互搶「台南外燴場地」 | GSC query 重疊 + 各頁點擊；保留最高流量者當 pillar，其餘轉子意圖或 301 | 全保留，先只在內鏈上互指 |
| 3 | 費用 cost 3 頁：`tainan-catering-cost-guide`（泛）/ `tainan-corporate-catering-cost` / `tainan-wedding-catering-cost` | 泛字頁疑似吃掉分眾頁 | GSC 看分眾頁是否被 cost-guide 壓排名；有才調整 | 全保留，分眾頁強化各自 modifier |
| 4 | 7 個 404 規劃 slug（§4） | 死 slug 殘留在舊文件 | 全 repo grep 已無「當 live」引用 + 無廣告 final URL 指向 → 從舊文件清掉字串 | 保留字串，但**禁當 live target**（已在 §4 標） |
| 5 | 廣告文件錯誤 slug `outdoor-wedding-catering-venue`（404，應為 `tainan-outdoor-wedding-catering`） | 廣告死連結 | 廣告文件（`ad-funnel-battle-plan.md` / `ad-buildout-plan.md`）已同步改為正確 slug → 此項關閉 | 修正前廣告 final URL **不可**上線指向 404 |

**回看 SOP（2026-09-23 起）：** ① 跑 §7 Codex authenticated REST 取 GSC 點擊/排名 → ② 逐項比對上表「判定依據」→ ③ 訊號成立才 301/移除，並記進 `CHANGELOG` + `checkpoint.sh`；訊號不成立就把回看日再往後推、維持觀察。**任何移除都走 git commit（可回滾），不做不可逆刪除。**
