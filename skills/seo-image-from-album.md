# 技能：從既有 SEO 相簿專案抽精選圖

版本：v1.0 | 建立：2026-07-03 | 維護：A2 / A4
> 目的：讓任何 Agent 能獨立從 MAPLAB 已整理好的 SEO 相簿專案中，找到正確的 webp 圖片並安全地用於 WordPress 文章精選圖與內文圖，不重複詢問 Owner「圖在哪裡」。

---

## 第一段：去哪找 SEO sheet（資料來源）

### 相簿母專案

| 項目 | 值 |
|---|---|
| 資料夾名稱 | `JOB-A2-B2B-CASE-ADS-20260526` |
| Google Drive 資料夾 ID | `1-LhhR18v6sSBk9gkIPti5flWW_rvP3ID` |

### SEO 對應表（真相來源）

| 項目 | 值 |
|---|---|
| 檔案名稱 | `asset_conversion_manifest`（CSV） |
| round_001 CSV ID | `101iIsznsgb7idWYasnPVzKHZhWpxo7AI` |
| 格式 | CSV，每列一個圖片素材 |

**`asset_conversion_manifest` 欄位完整說明：**

| 欄位 | 說明 |
|---|---|
| `source_path` | 原始圖在 Drive 的相對路徑 |
| `source_filename` | 原始圖檔名 |
| `cluster` | 主題群（例：corporate_meeting / wedding） |
| `landing_slug` | 對應目標文章 slug |
| `case_name` | 案例名稱（人話） |
| `slot` | 輸出用途：`hero_16x9` / `story_9x16` / `meta_4x5` / `case_4x3` |
| `target_width` / `target_height` | 裁切目標尺寸（px） |
| `crop_anchor` | 裁切錨點：`food_table` / `venue_context` / `center` |
| `crop_note` | 裁切備注（自由文字） |
| `output_filename` | 最終 webp 檔名（SEO 命名格式） |
| `alt_text` | WP alt 文字（直接用，不自行改寫） |
| `caption` | WP caption |
| `description` | WP media description |
| `ad_ok` | 廣告可用：`yes` / `no` |
| `ad_restriction` | 廣告限制說明 |
| `needs_face_crop` | 是否有人臉需裁切：`yes` / `no` |
| `needs_logo_crop` | 是否有外部 logo 需裁切：`yes` / `no` |
| `needs_alcohol_avoid` | 是否含酒精需迴避：`yes` / `no` |
| `priority` | 優先順序（數字，越小越優先） |
| `owner_review_status` | Owner 審核狀態 |

### SEO 命名成品資料夾

| 項目 | 值 |
|---|---|
| 資料夾名稱 | `wordpress_assets_round_008` |
| Google Drive 資料夾 ID | `1T2fFn_rLoA2_1kL0DYgN6oZCzTbFEuIT` |
| 格式 | 全部 `.webp`，檔名即 `output_filename` 欄位值 |

---

## 第二段：怎麼把 sheet 和相片對上

### 比對邏輯

1. **找圖**：用 `output_filename` 欄位值，在 `wordpress_assets_round_008` 資料夾內找同名 `.webp`。檔名一對一，不猜測。

2. **對應文章**：用 `landing_slug` 比對目標文章的 slug；`cluster` 和 `case_name` 輔助確認主題吻合，避免把婚宴案例圖配進企業外燴文章。

3. **直接用 `alt_text`**：manifest 裡的 `alt_text` 已依 A 式格式（`台南{場景}外燴—{具體描述}`）寫好，WP 上傳後直接貼入，不自行改寫。如果 `alt_text` 欄位為空，回報 Owner，不要自行補寫。

4. **發布前必查三個合規欄位**（缺一不可）：

| 欄位 | 規則 |
|---|---|
| `needs_face_crop` | `yes` → 禁止上傳，需 A4 先裁臉再用；`no` → 可上傳 |
| `ad_ok` | `no` → 只能用於 SEO 文章，不可進廣告素材；`yes` → 兩者皆可 |
| `ad_restriction` | 有填寫 → 上傳前確認限制內容，並在 WP media description 備注 |

> **隱私原則**：`needs_face_crop = yes` 的圖片若未裁切就出現在公開前台，屬於系統錯誤（見 `docs/OPERATING_CULTURE.md` 隱私條款）。不確定就問 A4，不要假設「可能沒關係」。

---

## 第三段：怎麼裁切（slot 與尺寸對應）

### slot 用途對照

| slot | 適用場景 | 典型尺寸 | 是否適合 WP 精選圖 |
|---|---|---|---|
| `hero_16x9` | WP 精選圖、橫式橫幅 | 1920×1080 或等比例 | ✅ 優先選這個 |
| `story_9x16` | IG Story、直式合成圖（通常含文字浮水印） | 1080×1920 | ❌ 不適合（浮水印會露出在前台） |
| `meta_4x5` | Meta 廣告 | 1080×1350 | ❌ 不適合（裁切太緊，精選圖會裁壞） |
| `case_4x3` | 文章內文插圖、案例方塊 | 1200×900 或等比例 | 可用於內文，不推薦精選圖 |

### 裁切錨點說明

| crop_anchor | 意思 | 裁切時保留哪一側 |
|---|---|---|
| `food_table` | 以食物桌面為核心 | 保持餐點在畫面中央偏下 |
| `venue_context` | 以場地環境為核心 | 保持空間感，不緊貼食物 |
| `center` | 置中裁切 | 均等裁掉四邊 |

### WP 精選圖選圖原則

優先順序：
1. `slot = hero_16x9` + `needs_face_crop = no` + `needs_logo_crop = no`
2. `priority` 欄位數字越小越優先
3. `landing_slug` 或 `cluster` 與目標文章主題吻合
4. `owner_review_status` 已通過（非 pending / rejected）

**不選**：`story_9x16`（浮水印）、`needs_face_crop = yes`（隱私）、`needs_alcohol_avoid = yes`（若文章受眾是企業/HR）。

---

## 實例紀錄（本技能首次使用）

**文章**：《行政外燴推薦 HR 活動餐點規劃》（WP post 1992）  
**選用圖片**：`maplab-corporate-forum-cathay-wealth-management-hero.webp`  
**選用理由**：slot = `hero_16x9`、`needs_face_crop = no`、乾淨橫式、無浮水印  
**WP alt**：`MAPLAB 台南企業外燴，國泰建設財富管理論壇茶點桌`  
**上傳方式**：Owner 瀏覽器 session 手動上傳至 WP 1992 精選圖欄位  
**日期**：2026-07-03

> 注意：本次 `alt_text` 由 Owner 親自確認，格式為「品牌名 + 地區場景 + 活動名稱 + 描述」，略有別於純 A 式格式（`台南{場景}外燴—{描述}`）。原因是這張圖帶有明確案例名稱（國泰建設財富管理論壇），用案例全名可提升圖片搜尋相關性。如未來統一格式，以 A2 Conventions Lock 為準。

---

## 快速 SOP（冷啟動用）

```
1. 讀 asset_conversion_manifest CSV（ID: 101iIsznsgb7idWYasnPVzKHZhWpxo7AI）
2. 用 landing_slug / cluster 篩出目標文章相關列
3. 篩 slot = hero_16x9 且 needs_face_crop = no 且 needs_logo_crop = no
4. 按 priority 排序，取第一列
5. 確認 owner_review_status 非 rejected
6. 查 ad_ok / ad_restriction（文章 SEO 用途，ad_ok = no 也可用）
7. 取 output_filename → 在 wordpress_assets_round_008 找同名 .webp
8. 取 alt_text → 直接填 WP alt 欄位
9. 上傳至 WP media，設為精選圖
10. 回報：圖片名稱、alt、case_name、選用理由
```
