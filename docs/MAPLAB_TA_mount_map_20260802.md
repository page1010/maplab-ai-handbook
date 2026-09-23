# MAPLAB 素材 TA → 活動 → 掛載子頁 對照表（確定部分）

> 真相來源：外接碟實際資料夾名 `/Volumes/MacExternal/MAPLAB_素材_依TA_20260724/`
> ＋ `docs/seo-keyword-map.md`（canonical）。建立：2026-08-02。
> 只列**已確定**項；不確定的 3 項見 `MAPLAB_asset_confirmation_20260802.html`（等 Owner 確認）。

## 0. Owner 速記 → 實際對應（解碼）

| Owner 速記 | 實際 pillar / slug | Post ID |
|---|---|---|
| 開幕 → GAP-2 | GAP-2「開幕茶會案例」→ 內鏈指南頁 `tainan-corporate-opening-tea-catering` | **1205** |
| 週歲 → 498 | `catering-one-year-old-party-tainan`（週歲/性別派對共用 pillar） | **498** |
| 婚禮 → 1215 | `tainan-outdoor-wedding-catering`（戶外婚禮 pillar） | **1215** |
| （企業茶會） | `corporate-tea-party-desserts`（企業茶點 pillar，B3 廣告主 landing） | **924** |

> ⚠️ 校正：Owner 先前記憶「TA1=開幕/企業、TA3=週歲」與外接碟實況相反。
> 實際：**TA1_週歲、TA2_婚禮、TA3_HR（企業/HR，含開幕茶會）**。本表以外接碟為準。

## 1. 確定對照（可直接進產線）

| 外接碟資料夾（實際） | 活動類型 | 掛載 pillar / 子頁 | 對應 landing slug | 信心 |
|---|---|---|---|---|
| `TA1_週歲/抓周甜點桌_0719` | 抓周／週歲派對 | `catering-one-year-old-party-tainan` **498** | `/first-birthday-catering/` | 高 |
| `TA2_婚禮/證婚_東門教會_0627` | 婚禮／證婚 | `tainan-outdoor-wedding-catering` **1215**；子頁迎賓點心 `tainan-wedding-welcome-canapes` **1217** | 婚禮 pillar cluster | 高 |
| `TA3_HR/開幕茶會_Clea` | 品牌店面開幕茶會（Cléa 服飾選品店，6/26 開幕） | **GAP-2 開幕茶會案例** → 內鏈 `tainan-corporate-opening-tea-catering` **1205** + `business-opening-party-ideas` | 開幕/企業 | 高（已看實圖） |
| `TA3_HR/會議_工研院` | 企業會議茶點（工研院） | `corporate-tea-party-desserts` **924**；案例 `corporate-catering-tainan` **586** | `/buffet-catering/`、企業案例 | 中高 |
| `TA3_HR/研發日_科林` | 企業研發日活動（Corning 科林） | **924**／**586**；場域可補 **GAP-4 南科/科技公司** | 企業/科技 | 中高 |
| `TA3_HR/論壇_三立` | 論壇／媒體活動茶點（三立） | **924**／案例 **586**；記者會 `press-conference-catering` | 企業/記者會 | 中 |
| `TA3_HR/說明會_遊學` | 說明會／教育機構活動 | **924**／**586**（機構活動茶點） | 企業/機構 | 中 |

## 2. 需 Owner 確認後才掛載（見 HTML 確認表）

| 資料夾 | 為何不確定 | 我的建議掛載 |
|---|---|---|
| `TA2_婚禮/婚禮風格甜點桌_候選_未確認` | 夾名自標「未確認」 | 確認為真婚禮→1215/1217；否則→通用甜點桌池 |
| `TA1_週歲/托嬰畢業甜點桌_0717` | 托嬰畢業 ≠ 嚴格週歲；可能有幼童臉 | 週歲 pillar **498** 當子案例，或獨立「幼兒畢業」角度 |
| `甜點桌_跨TA_20260725/2022–2025`（約 4,300 張，SEO 檔名） | 設計上跨 TA 復用，單張 TA 不可靠 | 當「菜單/canapes 通用配圖庫」→ **GAP-5**，不逐張綁 TA |

> `TA*/_A4回收_疑似截圖排除`：實查 0 檔（已清空），無需處理。

## 3. 內鏈與 404 守則（來自 seo-keyword-map）

- 新文章內鏈一律用 `[INTERNAL_LINK_RECHECK_REQUIRED]` 佔位，verify live 後才連。
- 禁連 7 個 404 slug（見 seo-keyword-map §4）。
- 與 live WP 衝突時：**live WP REST > 本表 > 其他 repo 紀錄**。
