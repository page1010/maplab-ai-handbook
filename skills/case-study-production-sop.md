# skills/case-study-production-sop.md — 個案（活動場次）內容產線 SOP

> 狀態：DRAFT（2026-08-02）。一支技能把「一個活動場次 → WP 文章 + 影片」的產線歸一。
> **不重造輪子**：本 SOP 只做「編排 + 缺口」，實作全部指到既有技能/規範（見 §0）。
> 核心紀律：A2/A3/A4 先產文＋確認 → **確認後才交 A8 建影片**；全程 draft/私人，Owner 點頭才公開。

## 0. 真相來源 / 既有技能（先讀，勿重寫）

**Owner canonical（Drive 母夾 1pKfGSOZ… 內，最高權威）**
- 【正式規範】MAPLAB A2/A4 內容產線格式＋規範 v1（`1mDm7pHD…`）＝量產統一標準。
- 【模板v3】A2 活動介紹文案-WordPress 式（`1tC_UMWs…`）＝上稿正文骨架（只換內容）。
- 【基準】品牌語氣＋色調 A2/A8 共用速查（`1fABfjRs…`）。

**Repo 技能（實作層）**
- 文章(A2)：`skills/wp-article-standard.md`、`skills/brand-voice-guide.md`、`docs/seo-keyword-map.md`、`docs/real-cases-to-seo-matrix.md`、`recalls/A2_recall.md`、`skills/seo-session-checklist.md`。
- 素材(A4)：`skills/photo-asset-retrieval-guide.md`、`skills/seo-image-from-album.md`、`skills/a4-fact-first-asset-matching.md`、`skills/a4-photo-asset-skills.md`、`skills/a2a3-workbench-material-library-guide.md`、`skills/maplab-photo-sourcing.md`。
- 廣告(A3)：`skills/a3-social-ads-skills.md`、`recalls/A3_recall.md`、`docs/ad-funnel-battle-plan.md`。
- 影片(A8)：`skills/a8-produce-to-publish-sop.md`、`skills/a8-video-pipeline-skills.md`、`skills/a8-local-motion-integration.md`、`recalls/A8_recall.md`。
- 上稿/憑證：`skills/gdrive-to-wordpress-upload-guide.md`、`scripts/wp_publish_draft.py`（Notion vault 取密、draft-only）、`skills/credentials/wordpress-api.md`。

## 1. 檔案組織（沿用既有 Drive 慣例）

- 母夾：`真實案例`＝Drive `1pKfGSOZXBpG7qXcJrW5T7aoHX4nqB1Tt`（＝「2026maplab外燴紀錄」）。
- 專案子夾命名（照現況慣例）：`{MMDD 或 YYYYMMDD}{客戶}-{活動}`，例：`0718-服飾店開幕茶會Clea'`、`0717邦尼兔-托嬰畢業典禮`、`0621說事實木地板開幕`。
- 子夾內結構（產線寫回）：`raw/`（原始 HEIC/MOV）、`oriented/`（轉正）、`webp/`（A4 精選圖）、`publish/`（WP/影片/Pinterest 成品）。
- 本機 TA 視圖鏡像：`/Volumes/MacExternal/MAPLAB_素材_依TA_.../TAx_.../`（照 photo-asset-retrieval-guide；TA 是視圖，不是真相）。

## 2. 產線流程（單向，有 gate）

```
① A4 素材：挑素材乾淨場次 → 轉正(a8_auto_orient) → webp(cwebp q80) → SEO 命名 + alt + 合規旗標（§4）
② A2 文章：多源三角查證客戶 → 取關鍵字(seo-keyword-map) → 判掛載 → 依【模板v3】寫「圖文交錯×4」→ WP status=draft
   （SEO：標題/描述/focus keyword、圖片 alt、內鏈佔位、掛載 pillar）
③ A3 廣告(選配)：ad_ok=yes 的圖進廣告素材；對 ad-funnel landing
——— GATE：A2/A3/A4 產出 + 自查 QA(§5) + Owner/A2 確認分類與文案 ———
④ A8 影片：確認後才建；優先用「真影片檔」(非相片轉場)；a8_enhanced_video_draft.py(maplab_ig_soft)
   9:16 1080×1920、字幕 6–14 字過語氣 QA、固定連結串、場景 hashtag → YouTube 私人 Short 草稿
⑤ 對齊：WP 關鍵字 ↔ 影片 hashtag、客戶名/活動/品項/語氣一致 → 交 Owner 最後校對 → 核准才公開
```

**交接點**：每案一個 Drive 專案夾即真相；A2 產出 `publish/` 內的 WP draft 連結 + 內部欄位（模板 v3 §內部用）→ A8 從同一夾取 `webp/` 或真影片建片。**A8 不自行開案、不各做各的。**

## 3. 掛載子頁對照（摘 seo-keyword-map / 正式規範 §七）

開幕茶會/店面開幕 → 內鏈 `tainan-corporate-opening-tea-catering`(1205) + `business-opening-party-ideas`（GAP-2 案例）｜
企業茶會/會議茶點 → ★`corporate-tea-party-desserts`(924)｜週歲/抓周/性別揭曉 → ★`catering-one-year-old-party-tainan`(498)｜
婚禮 → ★`tainan-outdoor-wedding-catering`(1215)＋5 子頁｜彌月 → `tainan-full-moon-baby-catering`（獨立）｜飯店會議 → GAP-1（內鏈回 924/586）。
內鏈用 `[INTERNAL_LINK_RECHECK_REQUIRED]` 佔位；禁連 seo-keyword-map §4 的 7 個 404 slug。

## 4. 相片命名 + alt 規則（讓新進相片自動命名、可檢索）

**每張新進相片走這條 pipeline（寫成可重複規則）：**
1. **轉正**：HEIC→`sips`／`tools/ai_workbook/a8_auto_orient.py`；不盲轉。
2. **轉檔**：webp（`cwebp q80`，長邊 1920）。
3. **檔名（自動）**：`maplab-{場景}-{描述}-{NN}.webp`（全小寫、連字號、無中文/空格）。
   - `{場景}` 由專案夾活動類型對映：開幕=`opening-tea`、週歲/抓周=`first-birthday`、婚禮=`wedding`、會議=`corporate-meeting`、論壇=`forum`、說明會=`seminar`、甜點桌通用=`dessert-table`。
   - `{描述}` 取畫面主體（cheesecake-tart-display / welcome-table / signage…）；`{NN}` 兩位序號。
4. **alt（自動，A 式單一標準）**：`台南{場景中文}外燴—{現場具體描述}`（15–30 字、1–2 關鍵字不堆疊、品牌名不進開頭；純裝飾用 `alt=""`）。
5. **合規三旗標（必填，A4 判）**：`needs_face_crop`（有人臉→先裁/模糊，**兒童臉一律排除**）、`needs_logo_crop`（他牌 logo→確認才用；本案客戶品牌 OK）、`ad_ok`（要進廣告才 =yes）。
6. **索引回填**：一列寫進 `MAPLAB_WORKSPACE/index/photo_alt_index.csv`（檔名/場景/描述/alt/drive_id/合規旗標/客戶/日期），讓之後可用關鍵字/場景直接撈（照 photo-asset-retrieval-guide）。

> 效果：相片持續新增時，只要落進 `{客戶}-{活動}` 專案夾，依 §4 即可自動命名＋alt＋入索引，A2/A8 之後用場景關鍵字一撈即得。

## 5. 交稿前 QA（摘正式規範 §十）

語氣：像 MAPLAB？無過度推銷？無禁用詞（§禁用＋A8 字幕加禁：取餐/順暢/動線穩/節奏…）？有寫場景？
視覺：7 色票、單畫面≤3 主色、場景色對應、暖調、文字不遮食物。
SEO：主關鍵字進標題/首段？無 §5 互搶？內鏈非 404？掛載 pillar 正確？
A8：9:16、前 3 秒 hook、字幕 6–14 字、無內部日期/檔名/人臉/私密資料。
合規：兒童臉已排除；他牌 logo 已確認。

## 6. 憑證 / 上稿（治理）

- WP：`https://www.maplabkitchen.com`（`maplab.com.tw` 已失效）。憑證＝WP App Password，存 Notion 保管室；A0 用 `scripts/wp_publish_draft.py`（或等效）於 runtime 取密、`status=draft` only、不 echo、不 commit。
- Cloudflare/Cloudways WAF 會擋非瀏覽器 UA（error 1010）→ REST 請帶瀏覽器 User-Agent。
- 一律 draft/私人；發布、改 Rank Math 付費設定、DELETE 皆需 Owner。

## 7. 不確定素材 → 走確認流程（沿用）

分類/場次不確定：先讀 §0 全貌指南找依據；仍不確定→做「圖+文確認表」（縮圖+實際路徑+判斷+提問）交 Owner，**確認後才寫 alt/上稿**。確定的照常。
