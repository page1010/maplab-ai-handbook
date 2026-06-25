# A2 SEO Plan Refresh — maplabkitchen 外燴站

日期：2026-06-23  
角色：A2 SEO 內容  
狀態：approval_ready / file-only proposal  
邊界：只讀 public web / public REST GET / public sitemap；不登入後台、不發布、不改線上頁、不碰 secrets、不 push、不 commit。

## Startup Check

- 我是 A2 搜尋流量作戰部，任務是刷新 maplabkitchen 外燴站 SEO 發佈計畫。
- 品牌價值：自然、溫暖、安靜、細緻、有質感、專業、穩定、有分寸；不靠低價、不硬賣。
- 品牌語氣來源：`skills/brand-voice-guide.md`。本計畫避免誇張促銷、價格導向、說服式對比句型，案例文以場景與接待節奏為主。
- 視覺來源：`skills/maplab-visual-spec.md`。若進入 execution，圖片與頁面視覺應走暖米、深橄欖、暖棕、鼠尾草等既有品牌系統。
- Live 狀態來源：優先 public WordPress REST；2026-06-24 已補核完整 public posts/pages inventory，證據保存於 `docs/a2a3/a2-rest-inventory-20260624.md`。
- 高風險邊界：WordPress 發布/更新、Google Ads、Meta Ads、GTM/Pixel、Rank Math 設定、credential 取用都需要 Owner/A1 精確批准。

## Evidence Log

### 2026-06-24 Public REST + Sitemap Check

證據檔：`docs/a2a3/a2-rest-inventory-20260624.md`

目標 endpoint：

- `https://www.maplabkitchen.com/wp-json/wp/v2/posts?per_page=100&page=1&_fields=id,date,modified,slug,link,title,status,type`
- `https://www.maplabkitchen.com/wp-json/wp/v2/pages?per_page=100&page=1&_fields=id,date,modified,slug,link,title,status,type`
- `https://www.maplabkitchen.com/post-sitemap.xml`

本輪結果：

- Posts REST：HTTP 200，`X-WP-Total: 58`，`X-WP-TotalPages: 1`，body count `58`。
- Pages REST：HTTP 200，`X-WP-Total: 6`，`X-WP-TotalPages: 1`，body count `6`。
- `icc-tainan-catering`：REST confirmed live post `1829`，status `publish`，type `post`，link `https://www.maplabkitchen.com/icc-tainan-catering/`。
- `post-sitemap.xml`：HTTP 200，`<url>` count `57`；`icc-tainan-catering` not found。
- 新候選 slugs `campus-seminar-catering-tainan`、`nanke-tech-company-catering`、`reception-center-vip-catering-tainan` 未撞 public posts/pages REST；`school-event-catering-tainan` 也未撞 public REST/sitemap。

判讀：6/23 的 REST 缺口已由 6/24 public GET 收斂。ICC 是 live post，但未進 `post-sitemap.xml`；這是 sitemap/indexing registration drift，不是 unpublished evidence。public REST 仍不能看 private drafts、scheduled posts、trash、Rank Math meta、GSC indexing 或 authenticated duplicate drafts。

### 2026-06-23 Front-End Checks

已由前台 HTML 確認下列公開頁可讀：

| URL / slug | 前台標題 | 現況判讀 |
|---|---|---|
| `/` | `台南外燴｜MAPLAB Kitchen CATERING SERVICE` | 首頁近期文章列出 `大臺南會展中心活動外燴｜企業茶點與貴賓接待｜MAPLAB`，證明 ICC 文章至少在首頁前台可見。 |
| `corporate-catering-tainan` | `台南企業外燴推薦｜會議茶點、開幕茶會與品牌活動規劃｜MAPLAB` | B2B pillar live；內文有殘字 `f`、促銷式「優惠/折扣」語氣、品牌與案例段可優化。 |
| `corporate-tea-party-desserts` | `台南會議茶點外燴｜研討會、講座與企業活動餐點｜MAPLAB` | 會議茶點頁 live；已有成功大學、長榮 EMBA 等案例段，應優化舊文而非另開泛用會議茶點頁。 |
| `tainan-corporate-opening-tea-catering` | `台南開幕茶會外燴｜開幕典禮流程與品牌接待餐點｜MAPLAB` | 開幕茶會頁 live；FAQ 含價格區間，與 B2B 本批「不寫價格」規則衝突，建議改為估價因素。 |
| `brand-esg-catering-service` | `台南品牌活動外燴｜發表會、VIP 接待與展覽開幕餐點｜MAPLAB` | 品牌活動頁 live；有重複段落、圖片未能載入字樣、具名品牌密度偏高，優先清理。 |
| `vip-expo-catering-business-meeting` | `展覽外燴推薦｜VIP 點心吧與商務派對接待首選服務:MAPLAB Kitchen` | 展覽/VIP 接待頁 live；會與「大臺南會展中心」泛展覽字相近，應調整成 generic expo/VIP，ICC 保持 venue-specific。 |
| `press-conference-catering` | `記者會餐點推薦｜讓品牌活動更有記憶點的關鍵一刻` | 記者會頁 live；可優化為品牌發表/媒體接待的支援頁，不另開泛用記者會茶點新文。 |
| `daxin-art-museum-opening-catering` | `展覽開幕茶會外燴紀錄：2025 大新美術館藝術與餐飲交集｜MAPLAB` | 文化場館案例已存在；文化場館新素材先補這篇與品牌活動頁，不另開泛用文化場館主頁。 |

## Diff Against 2026-05-24 Audit

5/24 audit 基準：

- Published pages: 6
- Published posts: 57
- B2B live map：`corporate-catering-tainan`、`corporate-tea-party-desserts`、`tainan-corporate-opening-tea-catering`、`brand-esg-catering-service`、`press-conference-catering`、`vip-expo-catering-business-meeting`、`daxin-art-museum-opening-catering`

5/24 後已知新增：

| Date | Type / ID | Slug | Title | Evidence | Plan impact |
|---|---:|---|---|---|---|
| 2026-06-15 | post 1829 | `icc-tainan-catering` | `大臺南會展中心活動外燴｜企業茶點與貴賓接待｜MAPLAB` | 6/15 A2 execution bundle + 6/23 首頁近期文章前台可見 | 不再新寫「大臺南會展中心外燴」泛文；改為優化既有 ICC venue page。 |

2026-06-24 補核結論：

- Public REST 完整 posts/pages slug+title+date 清單已保存於 `docs/a2a3/a2-rest-inventory-20260624.md`。
- 5/24 audit 的 `57 posts / 6 pages` 已更新為 `58 posts / 6 pages`；新增差異仍是 `icc-tainan-catering` post `1829`。
- `post-sitemap.xml` 仍漏收 `icc-tainan-catering`，但 REST/live URL 已證明文章公開，需作 sitemap/indexing 後續檢查。

## Current Inventory For Planning

### Pages

2026-06-24 public REST confirms `6` published pages.

| Slug | ID | Title | Date | Modified |
|---|---:|---|---|---|
| `privacy-policy` | 1674 | `隱私權政策` | 2026-04-20T12:32:27 | 2026-04-20T12:32:55 |
| `homepage-v2` | 1250 | `台南外燴｜MAPLAB Kitchen CATERING SERVICE` | 2026-03-16T13:53:49 | 2026-03-23T10:31:53 |
| `join-maplab-catering-partner` | 209 | `外燴加盟合作平台-加入我們` | 2025-03-12T15:55:37 | 2025-06-20T21:33:43 |
| `about-us-maplabkitchen` | 44 | `About us` | 2025-02-13T11:39:04 | 2025-05-08T22:44:37 |
| `%e5%b7%a5%e5%95%86%e4%bb%a3%e8%b3%bc%e6%9c%8d%e5%8b%99` | 46 | `工商代購服務` | 2025-02-12T23:03:44 | 2025-05-04T15:25:51 |
| `tainan-party-venue` | 15 | `派對流程怎麼規劃？場地、餐點、預算一次搞懂！｜MAPLAB 外燴教學文` | 2025-02-12T21:22:45 | 2025-07-14T11:50:22 |

### B2B Posts In Scope

| Slug | ID | Title | Date | Modified | Action |
|---|---:|---|---|---|---|
| `corporate-catering-tainan` | 586 | `台南企業外燴推薦｜會議茶點、開幕茶會與品牌活動規劃｜MAPLAB` | 2025-05-21T09:20:06 | 2026-06-02T12:47:37 | Optimize old pillar. |
| `corporate-tea-party-desserts` | 924 | `台南會議茶點外燴｜研討會、講座與企業活動餐點｜MAPLAB` | 2025-07-14T15:16:20 | 2026-06-16T11:01:36 | Optimize old support page. |
| `tainan-corporate-opening-tea-catering` | 1205 | `台南開幕茶會外燴｜開幕典禮流程與品牌接待餐點｜MAPLAB` | 2026-03-15T08:44:52 | 2026-06-02T12:26:26 | Optimize old support page. |
| `brand-esg-catering-service` | 945 | `台南品牌活動外燴｜發表會、VIP 接待與展覽開幕餐點｜MAPLAB` | 2025-09-01T15:41:36 | 2026-06-15T16:00:39 | Optimize old support page. |
| `press-conference-catering` | 879 | `記者會餐點推薦｜讓品牌活動更有記憶點的關鍵一刻` | 2025-07-10T11:39:37 | 2026-06-15T21:03:12 | Optimize old support page. |
| `vip-expo-catering-business-meeting` | 261 | `展覽外燴推薦｜VIP 點心吧與商務派對接待首選服務:MAPLAB Kitchen` | 2025-03-15T10:21:10 | 2026-06-16T11:03:08 | Optimize old support page. |
| `daxin-art-museum-opening-catering` | 1048 | `大新美術館開幕外燴｜展覽開幕茶會餐點案例｜MAPLAB Kitchen` | 2025-11-27T21:54:55 | 2026-06-16T11:01:50 | Keep as cultural venue case; do not create duplicate generic page. |
| `icc-tainan-catering` | 1829 | `大臺南會展中心活動外燴｜企業茶點與貴賓接待｜MAPLAB` | 2026-06-15T15:25:12 | 2026-06-16T20:49:21 | Optimize existing venue case; no duplicate venue article. |

## Cannibalization Map

| Proposed keyword / topic | Existing live page collision | Decision |
|---|---|---|
| `台南企業外燴` | `corporate-catering-tainan` | Optimize old pillar, no new post. |
| `台南會議茶點外燴` / `研討會茶點` | `corporate-tea-party-desserts` | Optimize old page; new articles must be case-specific, not generic. |
| `台南開幕茶會外燴` | `tainan-corporate-opening-tea-catering` | Optimize old page; opening cases go into this page unless they are highly specific approved cases. |
| `台南品牌活動外燴` / `VIP 接待` | `brand-esg-catering-service` | Optimize old page; new case pages must target venue/industry proof, not generic brand activity. |
| `記者會餐點` / `新品發表會茶點` | `press-conference-catering` | Optimize old page; no generic new post. |
| `展覽外燴` / `VIP 點心吧` | `vip-expo-catering-business-meeting` | Optimize old generic expo page; ICC keeps venue-specific intent. |
| `大臺南會展中心外燴` | `icc-tainan-catering` | Optimize existing ICC page; do not create a second ICC guide until REST/GSC data shows need. |
| `台南文化場館外燴` / `美術館開幕茶會` | `daxin-art-museum-opening-catering` + `brand-esg-catering-service` | Optimize existing case/support pages first. |
| `台南校園活動外燴` / `學校講座茶點` | No public REST collision for `campus-seminar-catering-tainan` or `school-event-catering-tainan`; overlaps with `corporate-tea-party-desserts` | Candidate new case post after assets/permission check. |
| `南科企業外燴` / `科技公司會議茶點` | No public REST collision for `nanke-tech-company-catering`; partial overlap with `corporate-tea-party-desserts` | Candidate new case or location/industry guide, but needs service-area/evidence approval. |
| `接待中心茶點` / `建案 VIP 活動外燴` | No public REST collision for `reception-center-vip-catering-tainan`; partial overlap with `brand-esg-catering-service` | Candidate new case post if de-identified and asset-approved. |

## Old Posts To Optimize

### A2-OPT-001 — `corporate-catering-tainan`

Why: 這是 B2B pillar。現頁有企業外燴主關鍵字、延伸場景內連，但也有殘字、促銷式語氣與具名案例密度問題。

Plan:

- SEO title: `台南企業外燴推薦｜會議茶點、開幕茶會與品牌活動｜MAPLAB`
- Meta: `MAPLAB 提供台南企業外燴、會議茶點、開幕茶會與品牌活動餐點規劃，依活動流程、人數與場地條件安排茶點、飲品與接待餐桌。`
- H2 adjust:
  - `台南企業外燴適合哪些活動`
  - `行政窗口需要先確認的 5 件事`
  - `會議茶點、開幕茶會與品牌活動的差異`
  - `企業外燴案例怎麼看：場地、人數、接待節奏`
  - `延伸閱讀：會議、開幕、品牌活動與 ICC 會展案例`
- Copy fixes:
  - 移除殘字 `f`。
  - 移除 `優惠`、`折扣`、`免費索取菜單 PDF` 等偏促銷字眼，改為 LINE 詢問活動資訊。
  - 客戶名只保留已確認可公開者；其他改成 `科技業辦公室開幕`、`接待中心活動`、`品牌發表會`。
- Internal links:
  - Link to `corporate-tea-party-desserts`
  - Link to `tainan-corporate-opening-tea-catering`
  - Link to `brand-esg-catering-service`
  - Link to `press-conference-catering`
  - Link to `icc-tainan-catering`

### A2-OPT-002 — `corporate-tea-party-desserts`

Why: 會議茶點頁已承接研討會、講座、企業會議，不應被新泛文搶字。前台已有成功大學、EMBA 等案例段，應整理成可掃讀的案例群。

Plan:

- SEO title: `台南會議茶點外燴｜研討會、講座與企業活動餐點｜MAPLAB`
- Meta: `適合企業會議、校園講座、研討會與內部訓練的台南會議茶點。MAPLAB 依議程時間、來賓人數與場地動線安排甜鹹點、飲品與補給節奏。`
- H2 adjust:
  - `會議茶點適合哪些議程`
  - `半日、全日與多場次會議的茶點安排`
  - `校園講座與學術研討會案例`
  - `企業內訓與辦公室會議案例`
  - `會議茶點 FAQ`
- Copy fixes:
  - 將泛稱 `某知名科技公司` 改為去識別化場景描述或 verified case。
  - 保留「成功大學會議茶點」等可公開案例前，需 Owner 確認可具名；否則改為 `校園學術會議茶點`。
  - 移除 `完美呈現`、`無懈可擊` 這類過度承諾。
- Internal links:
  - Link to `icc-tainan-catering`
  - Link to `corporate-catering-tainan`
  - Link to future campus case if approved.

### A2-OPT-003 — `tainan-corporate-opening-tea-catering`

Why: 開幕茶會頁已有明確 live target；不需要新開泛用開幕茶會文。現頁 FAQ 出現每人價格區間，與本批 B2B SEO 規則衝突。

Plan:

- SEO title: `台南開幕茶會外燴｜品牌空間、診所與辦公室開幕餐點｜MAPLAB`
- Meta: `台南開幕茶會外燴規劃，適合品牌空間、診所、辦公室與展間開幕。MAPLAB 依流程、賓客組成與拍照需求安排茶點、飲品與餐桌位置。`
- H2 adjust:
  - `開幕茶會的流程與餐點位置`
  - `品牌空間、診所與辦公室開幕的差異`
  - `開幕茶點怎麼避免干擾剪綵與拍照`
  - `開幕茶會案例：用場景描述取代客戶名堆疊`
  - `開幕茶會 FAQ`
- Copy fixes:
  - 將價格 FAQ 改成 `影響估價的因素有哪些`，不列價格區間。
  - 刪掉 `令人難忘`、`最佳方案` 這類偏強推字。
  - 具名 `AMD / 清清顏 / Grand Open` 等只在 Owner 確認可公開後使用；預設寫場景。
- Internal links:
  - Link to `brand-esg-catering-service`
  - Link to `press-conference-catering`
  - Link to `corporate-catering-tainan`

### A2-OPT-004 — `brand-esg-catering-service`

Why: 品牌活動頁是高價值 B2B support page。今天前台可見重複段落、`圖片未能載入` 字樣與多個具名品牌，需要先清理再導流。

Plan:

- SEO title: `台南品牌活動外燴｜發表會、VIP 接待與展覽開幕餐點｜MAPLAB`
- Meta: `台南品牌活動外燴規劃，適合發表會、VIP 接待、展覽開幕與會員活動。MAPLAB 依品牌調性、接待節奏與現場動線安排茶點與飲品。`
- H2 adjust:
  - `品牌活動餐桌要承接的三個任務`
  - `發表會、VIP 接待與展覽開幕的餐點差異`
  - `科技業、金融與文化場館活動案例`
  - `活動後場地復原與行政窗口需求`
  - `延伸閱讀：開幕、記者會、展覽與 ICC`
- Copy fixes:
  - 合併重複 `段落 15 / 段落 16`。
  - 修正 `[圖片未能載入...]`。
  - 具名品牌減量，優先寫 `科技業茶會`、`企業公益活動`、`文化場館展覽開幕`。
  - 移除過度主觀句，例如 `科技人更是享受生活`。
- Internal links:
  - Link to `press-conference-catering`
  - Link to `vip-expo-catering-business-meeting`
  - Link to `icc-tainan-catering`
  - Link to `daxin-art-museum-opening-catering`

### A2-OPT-005 — `press-conference-catering`

Why: 記者會/新品發表已存在 live page。新寫「台南記者會茶點」會 cannibalize。

Plan:

- SEO title: `台南記者會餐點｜品牌發表會茶點與媒體接待｜MAPLAB`
- Meta: `台南記者會與品牌發表會餐點規劃，MAPLAB 依媒體動線、拍攝需求與賓客停留時間安排好拿取的茶點、飲品與接待桌。`
- H2 adjust:
  - `記者會餐點要配合媒體動線`
  - `新品發表會與品牌說明會的茶點安排`
  - `茶點尺寸、飲品與拍攝畫面的注意事項`
  - `記者會餐點 FAQ`
- Copy fixes:
  - 移除 emoji、過度口語與未驗證的顧客引言，除非有可公開來源。
  - `多年經驗`、`多年支援市府` 類 claim 要有證據；否則改成場景描述。
- Internal links:
  - Link to `brand-esg-catering-service`
  - Link to `tainan-corporate-opening-tea-catering`
  - Link to `corporate-catering-tainan`

### A2-OPT-006 — `vip-expo-catering-business-meeting`

Why: 展覽/VIP 接待頁與 ICC venue page 相近。保留這頁作 generic expo/VIP support，ICC 作 venue-specific case。

Plan:

- SEO title: `台南展覽外燴｜VIP 點心吧、商務接待與品牌活動｜MAPLAB`
- Meta: `台南展覽與 VIP 接待外燴規劃，MAPLAB 依展間動線、來賓停留時間與品牌形象安排點心吧、飲品與商務交流餐桌。`
- H2 adjust:
  - `展覽點心吧適合哪些接待情境`
  - `VIP 接待與一般展攤茶點的差異`
  - `點心、飲品與品牌視覺怎麼配合`
  - `展覽外燴 FAQ`
- Copy fixes:
  - 移除 `提升業績`、`轉換率` 這類過強銷售承諾。
  - 減少酒精/啤酒吧作為主賣點；若保留，標成特定活動選項。
  - Link out to ICC venue page，避免與 `大臺南會展中心外燴` 互搶。

### A2-OPT-007 — `icc-tainan-catering`

Why: 5/24 後新增的高價值 venue case，首頁已可見。這篇要保護 `大臺南會展中心外燴` 位置，不再另開同關鍵字新文。

Plan:

- Keep SEO title: `大臺南會展中心活動外燴｜企業茶點與貴賓接待｜MAPLAB`
- Meta refine: `大臺南會展中心外燴與企業茶點案例。MAPLAB 依會議流程、貴賓接待與展覽動線安排手指食物、飲品補給與活動餐桌。`
- H2 add/adjust:
  - `大臺南會展中心活動外燴適合哪些場景`
  - `會議中場、展覽接待與貴賓停留的餐點配置`
  - `ICC 活動前要先確認的現場條件`
  - `延伸閱讀：會議茶點、展覽接待與品牌活動`
- Internal links:
  - Back to `corporate-tea-party-desserts`
  - Back to `vip-expo-catering-business-meeting`
  - Back to `brand-esg-catering-service`
  - Back to `corporate-catering-tainan`
- Validation needed:
  - Public REST slug check complete on 2026-06-24.
  - Sitemap check complete on 2026-06-24: ICC absent from `post-sitemap.xml`.
  - Authenticated check still needed for duplicate ICC drafts/private posts.

## New Case Posts Proposed

### A2-NEW-001 — 校園講座 / 學校活動茶點案例

Status: approval_ready after asset permission + authenticated draft check  
Primary keyword: `台南校園活動外燴`  
Supporting keywords: `學校講座茶點`, `EMBA 活動茶點`, `校園研討會外燴`, `畢業典禮茶點`

Cannibalization:

- No confirmed live `school-event-catering-tainan` page in 5/24 audit.
- `corporate-tea-party-desserts` already includes school/academic cases, so this must be a case/proof page, not a generic school service pillar.

Proposed slug: `campus-seminar-catering-tainan`

SEO title:

`台南校園活動外燴案例｜講座、EMBA 與學術會議茶點｜MAPLAB`

Meta:

`台南校園活動與學術會議茶點案例。MAPLAB 依講座流程、來賓人數與中場休息節奏安排甜鹹點、飲品與接待餐桌，適合學校講座、EMBA 與研討會。`

H2 outline:

- `校園活動茶點要配合議程與中場節奏`
- `適合講座、EMBA、研討會與畢業活動的配置`
- `案例場景：校園講座中場茶點`
- `桌面、飲品與補給節奏`
- `校園活動詢問前可以先準備哪些資訊`
- `FAQ`

De-identification:

- 預設用 `校園講座`、`學術會議`、`EMBA 活動`，不直接寫校名。
- 若 Owner 批准可公開，才保留 `成功大學`、`長榮大學`、`南臺` 等名稱。

Internal links:

- `corporate-tea-party-desserts`
- `corporate-catering-tainan`
- `icc-tainan-catering`

Publish gate:

- 2026-06-24 public REST confirms no live `campus-seminar-catering-tainan` / `school-event-catering-tainan` collision.
- Authenticated WP check confirms no private draft/scheduled duplicate.
- A4 confirms assets no face/no logo/no sensitive signage.
- Owner confirms school names can be public or stays de-identified.

### A2-NEW-002 — 南科 / 科技公司會議茶點案例

Status: approval_ready after service-area + case evidence + authenticated draft confirmation  
Primary keyword: `南科企業外燴`  
Supporting keywords: `科技公司會議茶點`, `台南科技業外燴`, `企業研發活動茶點`

Cannibalization:

- Partial overlap with `corporate-tea-party-desserts` and `corporate-catering-tainan`.
- New post is justified only if framed as location/industry proof: 南科、科技公司、研發單位、平日會議茶點。

Proposed slug: `nanke-tech-company-catering`

SEO title:

`南科企業外燴案例｜科技公司會議茶點與研發活動餐點｜MAPLAB`

Meta:

`南科與台南科技公司會議茶點案例。MAPLAB 依平日會議、研發單位活動與企業接待需求，安排好拿取的甜鹹點、飲品與穩定補給。`

H2 outline:

- `科技公司會議茶點在意的是準時與低干擾`
- `南科與台南科技業活動常見餐點需求`
- `案例場景：研發單位會議與交流茶點`
- `人數、時段與補給方式怎麼抓`
- `科技公司活動詢問前可以準備的資訊`
- `FAQ`

De-identification:

- 預設不寫公司名，用 `科技公司`、`研發單位`、`半導體供應鏈活動`。
- `科林研發 / 美光 / 東京威力 / Lam Research` 這類名稱需 Owner 確認公開權限後才出現。

Internal links:

- `corporate-tea-party-desserts`
- `corporate-catering-tainan`
- `brand-esg-catering-service`

Publish gate:

- Owner confirms MAPLAB service area and keyword target can cover 南科。
- A4/Drive confirms at least one approved tech-company asset set.
- 2026-06-24 public REST confirms no `nanke-tech-company-catering` collision; authenticated WP check still needed for drafts/scheduled posts.

### A2-NEW-003 — 接待中心 / 建案 VIP 茶點案例

Status: approval_ready after case source check  
Primary keyword: `接待中心茶點`  
Supporting keywords: `建案活動外燴`, `VIP 接待外燴`, `賞屋活動茶點`, `台南建案外燴`

Cannibalization:

- Partial overlap with `brand-esg-catering-service`。
- New post is justified as a proof case for real estate / reception-center buyer intent, not a generic brand activity page.

Proposed slug: `reception-center-vip-catering-tainan`

SEO title:

`台南接待中心茶點案例｜建案活動與 VIP 接待外燴｜MAPLAB`

Meta:

`台南接待中心與建案 VIP 活動茶點案例。MAPLAB 依賞屋流程、來賓停留時間與品牌視覺安排甜鹹點、飲品與接待餐桌。`

H2 outline:

- `接待中心茶點要讓來賓自然停留`
- `建案活動與 VIP 接待的餐點重點`
- `案例場景：接待中心活動茶點`
- `桌面位置、飲品與拍照畫面的安排`
- `建案活動詢問前可以準備的資訊`
- `FAQ`

De-identification:

- 預設寫 `接待中心活動`、`建案 VIP 接待`、`賞屋活動`。
- `國泰原美 / 川御建設` 等名稱需 Owner 確認公開權限。

Internal links:

- `brand-esg-catering-service`
- `corporate-catering-tainan`
- `vip-expo-catering-business-meeting`

Publish gate:

- 2026-06-24 public REST confirms no `reception-center-vip-catering-tainan` collision; authenticated WP check still needed for drafts/scheduled posts.
- Asset set has no private buyer faces / no unapproved logo closeup.
- Owner confirms whether developer/project name can be public.

## Topics Not To Publish As New Posts Now

| Topic | Reason | Safer action |
|---|---|---|
| 大臺南會展中心外燴指南 | Collides with `icc-tainan-catering` | Expand ICC page. |
| 台南會議茶點外燴 | Collides with `corporate-tea-party-desserts` | Optimize old page. |
| 台南開幕茶會外燴 | Collides with `tainan-corporate-opening-tea-catering` | Optimize old page. |
| 台南品牌活動外燴 | Collides with `brand-esg-catering-service` | Optimize old page. |
| 台南記者會茶點 | Collides with `press-conference-catering` | Optimize old page. |
| 展覽 VIP 外燴 | Collides with `vip-expo-catering-business-meeting` | Optimize old page and link ICC. |
| 文化場館外燴 | Collides with `daxin-art-museum-opening-catering` + brand page | Improve existing case first. |

## Publishing Order

Precondition for any execution:

1. Public REST GET for posts/pages is complete and saved in `docs/a2a3/a2-rest-inventory-20260624.md`.
2. Confirm no authenticated draft/scheduled/private duplicate slugs for proposed new posts.
3. Confirm A4 asset manifests and public-safety gates.
4. Owner approves exact scope.

Recommended order:

1. `A2-OPT-007` — improve `icc-tainan-catering` first because it is the newest 5/24 diff and likely Ads landing target.
2. `A2-OPT-001` — clean `corporate-catering-tainan` pillar and add structured links to the cluster.
3. `A2-OPT-002` — clean `corporate-tea-party-desserts`, then it can support campus/tech cases.
4. `A2-OPT-004` — clean `brand-esg-catering-service`, especially duplicate/missing-image sections.
5. `A2-OPT-003`, `A2-OPT-005`, `A2-OPT-006` — optimize opening, press conference, expo/VIP support pages.
6. `A2-NEW-001` — publish campus seminar case if authenticated draft check is clear and assets are safe.
7. `A2-NEW-002` — publish 南科/tech case if service-area and assets are confirmed.
8. `A2-NEW-003` — publish reception-center/VIP case after permission check.

## Approval Card

TASK_ID: `A2-SEO-REFRESH-20260623`  
ROLE: A2 SEO 內容  
STATUS: `approval_ready`

WHY:

5/24 audit 已過期；6/15 後已新增 ICC Tainan venue case。B2B cluster 的重點已轉向保護既有 live pages、修正 cannibalization、把真案例變成可發佈的 proof layer。

EVIDENCE:

- 5/24 audit: 6 pages / 57 posts / B2B live map。
- 6/24 public REST: `58` posts / `6` pages, saved in `docs/a2a3/a2-rest-inventory-20260624.md`。
- 6/24 public REST: `icc-tainan-catering` post `1829` is `publish` / `post`。
- 6/24 sitemap: `post-sitemap.xml` has `57` URLs and does not include `icc-tainan-catering`。
- 6/24 public REST: new candidate slugs `campus-seminar-catering-tainan`, `nanke-tech-company-catering`, `reception-center-vip-catering-tainan` do not collide with public posts/pages.

PLAN:

- 不新增泛用 B2B 主頁。
- 先優化 7 篇既有 live posts。
- 只新增 3 篇 case-specific posts；public REST duplicate check 已過，仍需 authenticated draft check、A4 asset gate、Owner public-name permission。

EXPECTED_EFFECT:

- 降低同關鍵字互搶。
- 讓最新 ICC venue case 回到 B2B pillar / meeting / expo cluster。
- 用 de-identified proof cases 擴充校園、科技公司、建案/接待中心三個目前缺口。
- 降低促銷語、價格語、客戶名外露與 AI 重複段落造成的品牌風險。

IMPACT_SCOPE:

- WordPress posts only: `corporate-catering-tainan`, `corporate-tea-party-desserts`, `tainan-corporate-opening-tea-catering`, `brand-esg-catering-service`, `press-conference-catering`, `vip-expo-catering-business-meeting`, `icc-tainan-catering`。
- New draft candidates: `campus-seminar-catering-tainan`, `nanke-tech-company-catering`, `reception-center-vip-catering-tainan`。
- No Google Ads / Meta Ads / Rank Math paid settings / GTM / Pixel / budget changes in this plan.

RISKS:

- Public REST inventory is complete for public posts/pages, but authenticated drafts/scheduled/private/trash states remain unknown.
- `icc-tainan-catering` is public but absent from `post-sitemap.xml`; execution should include sitemap/indexing follow-up before treating SEO discovery as complete.
- Some existing pages are Elementor-rendered; execution must verify `content.raw`, `content.rendered`, and front-end HTML before claiming visible update.
- Public client names and logos require permission review.

ROLLBACK:

- For WordPress content updates, export before/after content before applying.
- Keep title/meta old values in execution receipt.
- If cannibalization appears after publish, noindex is not the first move; first revise internal links and page intent split.

VALIDATION:

- REST GET posts/pages inventory saved with slug/title/date in `docs/a2a3/a2-rest-inventory-20260624.md`.
- Front-end 200 check for each updated URL.
- HTML readback confirms H1/H2/meta/CTA/internal links.
- No prices, local paths, secrets, internal notes, unapproved client names, unapproved logos.
- If Ads uses any landing page, A3 separately validates final URL / UTM / conversion surface read-only.

OWNER_DECISION:

- `批准 A2-SEO-REFRESH-20260623，只產 WordPress 草稿，不發布`
- `批准只做 A2-OPT-007 + A2-OPT-001`
- `批准優化舊文，不新增案例文`
- `退回，先補 authenticated draft / Rank Math / GSC checks`
- `縮小，先只處理 ICC Tainan landing page`

## Resume Prompt

我是 A2 SEO 內容，接手 `docs/a2a3/a2-seo-plan-refresh-20260623.md`。先讀 `CURRENT_STATUS.md`、`pitfalls.md`、`docs/a2a3/a2-seo-plan-refresh-20260623.md`、`docs/a2a3/live-wordpress-audit.md`、`recalls/A2_recall.md`、`projects/a2-ads-seo-wordpress-patrol.md`、`projects/a2a3a4-approval-ready-automation.md`、`handoff/tasks/T-A2-006-ads-seo-wordpress-patrol.md`、`skills/brand-voice-guide.md`。本輪已補 2026-06-24 public REST/sitemap inventory，未發布、未改線上頁、未讀 secrets、未 commit。下一步若 Owner 批准 execution，第一件事是做 authenticated WP draft/scheduled/private duplicate check、Rank Math/GSC/sitemap follow-up、A4 asset permission，再依批准範圍建立 draft 或修改既有頁。
