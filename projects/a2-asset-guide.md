---
# A2 SEO 團隊 — MAPLAB 相片素材查找指南
版本：v1.0 | 建立：2026-03-24 | 維護：A4 Pipeline Agent
---

## SECTION 0 — 這份文件是什麼

本文件提供 A2 SEO 團隊查找、篩選 MAPLAB Kitchen 相片素材的方法與規則。
素材由 A4 Pipeline Agent 自動分類（Gemini AI + GPS 座標），結果儲存在 MAPLAB_ASSET_LOG 試算表中。

**A2 的工作範圍：** 使用已分類好的素材做 SEO 內容規劃，不需要操作分類流程。

---

## SECTION 1 — 素材總表位置

| 項目 | 值 |
|------|---|
| 名稱 | MAPLAB_ASSET_LOG |
| 類型 | Google Sheets |
| 連結 | https://docs.google.com/spreadsheets/d/1nlxlMdaLdGEAmOjP70BYspRWqu_eYpsiRyZaujEZkYI/ |
| 帳號 | lb99104@gmail.com |
| 擁有者 | lb99104 |

> 如果看到「檔案已移至擁有者的垃圾桶」，請聯繫 lb99104 帳號復原。

---

## SECTION 2 — 欄位說明

### 批次資料（Row 12 起，佔 99% 資料量）

| 欄 | 欄位名 | 內容 | A2 用途 |
|----|--------|------|---------|
| A | year | 拍攝年份（2022-2026） | 按年份篩選 |
| B | filename | 原始檔名 | 對照原始檔案 |
| C | file_id | Google Drive 檔案 ID | 組成預覽連結（見 SECTION 4） |
| D | category | 三大分類：外燴/旅遊/日常 | **主要篩選欄位** |
| E | keywords | 3-5 個中文關鍵詞 | SEO meta keywords |
| F | alt_text | 30 字內中文描述 | HTML img alt 屬性 |
| G | seo_name | SEO 英文檔名建議 | WebP 重新命名用 |
| H | tokens | Gemini API token 數 | A2 可忽略 |
| I | status | done = 已完成分類 | 篩選已完成項目 |
| J | timestamp | 處理完成時間 UTC | A2 可忽略 |

### 先鋒資料（Row 2-11，僅 10 筆）

欄位順序不同（A=file_id, B=original_name, C=seo_name），含 drive_url 直連。
S14 步驟會統一格式，A2 可先忽略。

---

## SECTION 3 — 分類規則與邏輯

### 三大分類

| 分類 | English | 判斷邏輯 | 典型內容 |
|------|---------|----------|----------|
| 外燴 | catering | Gemini Vision AI 辨識 | 餐點擺盤、自助餐檯、食材備料、外燴佈置、客人互動、廚房、單據 |
| 旅遊 | travel | Gemini Vision AI 辨識 | 風景、觀光景點、飯店、家庭出遊、交通工具 |
| 日常 | daily | 以上皆非（預設分類） | 家庭生活、自拍、小孩、寵物、居家活動 |

### 日常子分類（S5.5 GPS 細分）

日常照片依 GPS 座標細分：

| 子分類 | 規則 | 地址 | GPS |
|--------|------|------|-----|
| home | 距離 < 500m | 台南市安中路2段336巷11號 | 23.0475324, 120.1841133 |
| shop | 距離 < 500m | 台南市北區和緯路2段450號 | 23.0125038, 120.2025030 |
| other | 兩者皆 > 500m | — | — |
| no_gps | 照片無 GPS 資料 | — | — |

home 與 shop 距離約 4.4km，500m 半徑不會重疊。
GPS 來源：Google Takeout JSON metadata（非 AI 判斷）。

### SEO 命名規則

seo_name 格式：{category}-{description}-{detail}

範例：
- catering-birthday-buffet-setup（外燴生日自助餐佈置）
- catering-banana-cupcake（香蕉杯子蛋糕）
- daily-baby-first-birthday-party（寶寶生日派對）
- travel-parent-child-boat-sea（親子搭船出海）

> seo_name 目前是建議名稱，實際重新命名在 S9 步驟執行。

---

## SECTION 4 — 如何快速找到素材

### 方法 1：按分類篩選
1. 開啟 MAPLAB_ASSET_LOG
2. D 欄 → 資料 → 建立篩選器
3. 篩選 = 外燴 / 旅遊 / 日常

### 方法 2：關鍵詞搜尋
Ctrl+F 搜尋 E 欄 keywords：
- 蛋糕、擺盤、自助餐、buffet、小孩、兒童、寶寶

### 方法 3：alt_text 搜尋
F 欄 30 字中文描述，可搜尋特定場景：
- 粉色玫瑰、木桌、戶外、室內

### 方法 4：預覽照片
用 C 欄 file_id 組成連結：
https://drive.google.com/file/d/{C欄的file_id}/view

### 方法 5：批次連結（進階）
在 Sheet 新增輔助欄位公式：
=HYPERLINK("https://drive.google.com/file/d/"&C2&"/view", "查看")

---

## SECTION 5 — 照片存放位置

### 原始檔案（Takeout）
路徑：MAPLAB/photos/Takeout/Google相簿/YYYY年的相片/
帳號：lb99104@gmail.com
Folder ID: 1jNUnnXPYMEq3GLDiJNC1GFZjQWRvwcCz

### 歸檔結構（目前）
MAPLAB_ASSETS/ (root: 1yVggYKiTkBJe4kd8CPoM3U75km0nVuNy)
  2022/ → catering/ travel/ daily/
  2023/ → catering/ travel/ daily/
  2024-2026/ → 同結構

### 最終歸檔結構（S9+ 完成後）
MAPLAB_ASSETS/
  catering/ → hero/ team/ events/{type}/ items/{item_id}/
  travel/ → {destination}/（小琉球/東京/薄荷島）
  daily/ → home/ shop/

---

## SECTION 6 — 目前進度

| 年份 | 照片數 | 狀態 | 備註 |
|------|--------|------|------|
| 2022 | 8,559 | 進行中 ~91% | 預計 2026-03-24 晚間完成 |
| 2023 | 19,459 | 待開始 | S5 完後接續 |
| 2024 | 17,834 | 待排程 | |
| 2025 | 9,883 | 待排程 | |
| 2026 | 4,424 | 待排程 | |
| 合計 | ~60,159 | | 約 4 週完成全部 |

A2 可先使用 2022 年已完成資料（7,700+ 筆），不需等全部完成。

處理速率：Gemini AI ~277 張/小時、GPS 細分 ~5,000 張/分鐘

---

## SECTION 7 — A2 注意事項

1. **唯讀**：ASSET_LOG 是 A4 自動化產出，A2 請勿修改。如需標記請另開工作表。
2. **seo_name 是建議**：G 欄名稱由 Gemini 產生，最終命名由 A4 在 S9 統一執行。
3. **準確度**：Gemini 分類準確度約 90%+，邊界案例可能不精確。
4. **日常子分類待完成**：home/shop 在 S5.5，預計 S5 完後 1 天內處理。
5. **特殊需求**：如需自訂篩選（如所有杯子蛋糕近照），透過使用者轉達給 A4。

---

## SECTION 8 — 關聯文件

| 文件 | 位置 | 說明 |
|------|------|------|
| maplab-pipeline.md | GitHub projects/ | A4 技術文件與完整進度 |
| CURRENT_STATUS.md | GitHub projects/ | 專案進度看板 |
| MAPLAB_ASSET_LOG | Google Sheets | 素材總表 |

---

## 版本紀錄

| 版本 | 日期 | 說明 | 更新者 |
|------|------|------|--------|
| v1.0 | 2026-03-24 | 初始版本 | A4 Pipeline Agent |
