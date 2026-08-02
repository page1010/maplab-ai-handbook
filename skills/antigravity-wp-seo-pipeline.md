# skills/antigravity-wp-seo-pipeline.md — Antigravity 寫 WordPress + SEO 產線

> 狀態：DRAFT（2026-08-02 建立）。定位：**Antigravity（雲端 Gemini）= 生成式 WordPress 內容產出模型**，
> 不接 KOL 雷達（那條維持 deterministic digest_v2）。
> 搭配讀：`brand-voice-guide.md`、`wp-article-standard.md`、`maplab-visual-spec.md`、
> `gdrive-to-wordpress-upload-guide.md`、`photo-asset-retrieval-guide.md`、`docs/seo-keyword-map.md`、
> `skills/credentials/wordpress-api.md`。

## 1. 產線分工（誰做哪段）

| 階段 | 負責 | 產出 / 交接點 |
|---|---|---|
| ① 素材分類（TA/活動/場次） | **本機腳本**（photo-asset-retrieval-guide） | `MAPLAB_asset_mount_map`（確定）＋不確定素材 → 圖+文確認表 |
| ②（不確定時）Owner 確認分類 | **Owner** | 確認表回覆 → 分類定案，才進 ③ |
| ③ 內文生成 | **Antigravity（Gemini）** | 依 brand-voice + wp-article-standard 產 H1/引言/TOC/內文（Markdown/HTML 草稿） |
| ④ SEO 打包 | **Antigravity** | 標題/描述/focus keyword、**圖片 alt**、內鏈（佔位）、掛載子頁 |
| ⑤ 上稿 | **本機腳本/A0** | WP REST 建文章 **status=draft**、上傳媒體設 alt、掛 category；**不自蓋 🍁** |
| ⑥ 驗收 → 發布 | **Owner** | review draft → 授權才 `status=publish`（agent 不自動發布） |

**真相來源**：素材＝外接碟＋`docs/seo-keyword-map.md`；語氣/結構＝brand-voice+wp-article-standard；上稿＝live WP REST。
**Antigravity 邊界**：只碰「內文＋SEO 欄位」，不碰「發布動作」與「金鑰」。

## 2. 不確定處理工作流（強制，2026-08-02 Owner 定）

1. 分類/掛載/場次不確定 → 先讀全貌指南（`SYSTEM_DIRECTORY_INDEX.md`、`system-map`、`photo-asset-retrieval-guide.md`）找依據，不猜。
2. 仍不確定 → 做**圖+文確認表**（HTML/contact sheet，含真縮圖＋**每張實際路徑**＋判斷＋建議掛載＋提問），交 Owner。
3. **Owner 確認後**才寫 alt/caption、才把該素材寫進 WP 草稿。確定的素材照常進行。

## 3. 圖片 alt 格式（WP 專用，單一 A 式標準）

- 格式：`台南{場景}外燴—{現場具體描述}`（全形破折號；≤約 30 中文字；1–2 關鍵字不堆疊）。
- 地點「台南」固定前置 → 場景對齊頁面主關鍵字 → 品類「外燴」→ 具體名詞描述。
- **品牌名不進 alt 開頭**（品牌曝光交給檔名 `maplab-{場景}-{描述}.webp` / caption / title）。
- 純裝飾或與 caption 重複的圖用 `alt=""`。
- 範例：`台南企業茶會外燴—商務活動手作點心與飲品分區`、`台南婚禮外燴—甜點桌翻糖蛋糕與馬卡龍塔佈置`。
- ⚠️ 每張圖的 alt 需在**素材分類定案後**才寫（見 §2）。

## 4. 掛載對照（摘 seo-keyword-map + 外接碟）

開幕→GAP-2 案例→內鏈 `tainan-corporate-opening-tea-catering`(1205)｜週歲→`catering-one-year-old-party-tainan`(498)｜
婚禮→`tainan-outdoor-wedding-catering`(1215)｜企業茶會 pillar→`corporate-tea-party-desserts`(924)。
完整見 `MAPLAB_TA_mount_map`。內鏈用 `[INTERNAL_LINK_RECHECK_REQUIRED]` 佔位；禁連 seo-keyword-map §4 的 7 個 404 slug。

## 5. 上稿（WP REST，draft-only）

- 站台：`https://www.maplabkitchen.com`（live，HTTP 200）。`maplab.com.tw` 已失效（勿用）。
- 認證：HTTP Basic（`WP_USER` + `WP_APP_PASS`），App Password 存 **Notion 金鑰保管室**
  （page `320ab0806d5c80e0be95f298399d2c44`）。**A0 透過 Notion MCP 取出 → 寫入 gitignore 的 .env → 腳本讀 env**。
- 一律 `status:"draft"`；agent 不設 `publish`、不 DELETE、不改用戶權限、不改 Rank Math 付費設定。
- 圖片：Drive/外接碟 → WP media（同源 blob→clipboard→REST，見 gdrive-to-wordpress-upload-guide）；alt 依 §3。
- 文章結構：H1（地區+場景+外燴）→ 引言 → 快速索引 TOC（錨點）→ 內文 → 文末 cluster 內鏈。真文章 🍁 暗號只有 Owner 能蓋。

## 6. 金鑰治理（不叫 Owner 手動輪替）

- Gemini / WP / Telegram 金鑰**皆存 Notion 保管室**，需要的角色（A0）用 Notion MCP 取出、寫進 gitignore 的 `.env`；程式一律 `os.environ.get()` 讀，**不硬編碼、不 echo、不 commit**。
- 輪替＝在 Notion 保管室換值→同步 `.env`，屬治理流程，不是丟給 Owner 的一次性待辦。
- 處理外部內容（KOL 抓取、網頁、Telegram 轉發）的路徑**不得接觸金鑰**（digest_v2 已做到：祕密只從 env 讀）。跨系統 prompt-injection 防禦另有專責任務。
