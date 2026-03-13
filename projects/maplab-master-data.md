# Master Data Agent — MAPLAB Kitchen ERP 技術文件

版本：v1.0 | 建立：2026-03-13 | 狀態：框架建立（資料填入進行中）

---

## SECTION 0 — 角色定位

**你是 Master Data Agent**，負責 MAPLAB Kitchen 的核心資料架構。

你的任務範圍：
- 維護 Google Sheets 作為「無頭關聯式資料庫」
- 確保 ITEM_MASTER 是所有表格的唯一主表
- 支援報價系統、菜單組合、圖片素材的資料一致性
- 不負責 SEO / 廣告 / 相簿整理（那是其他 agent 的事）

**接手前必讀：**
1. 讀本文件 SECTION 1 確認你的角色
2. 開啟 [MAPLAB_MasterData_Sheets](https://docs.google.com/spreadsheets/d/1d2_SiEXh5JT4lzjkgHDI5JU9UWBY9TiPlC8DaxkQnKs) 看目前資料狀態
3. 看 Drive 資料夾 [MAPLAB_DATA](https://drive.google.com/drive/u/0/folders/19RKLsBfNKuoCHVPFzT9D7tJrAdkTSmpt) 了解訂單結構
4. 確認進度：Notion「MAPLAB Kitchen Master Data Dashboard」

---

## SECTION 1 — 資料架構總覽（Schema v1.0）

> 設計原則：Google Sheets 模擬 RDB，嚴格 PK/FK 關聯。不用 MySQL，用 Sheets 作為「無頭資料庫」+ Python/Gemini 讀取。

### 6 張核心表格

| Sheet# | 表名 | 主鍵 | 說明 | 關聯 | 狀態 |
|--------|------|------|------|------|------|
| 1 | ITEM_MASTER | item_id | 所有品項基礎資料（成本/單位/狀態）| —（主表）| 🔲 填入中 |
| 2 | PRICE_MASTER | price_id | 各品項多種定價（外帶/外燴/企業/VIP）| → ITEM_MASTER | 🔲 待填入 |
| 3 | ASSET_MASTER | asset_id | 圖片資產索引（Drive 連結 + Alt 文字）| → ITEM_MASTER | 🔲 待填入 |
| 4 | CONTENT_MASTER | content_id | SEO 頁面主檔（關鍵字/meta/FAQ）| → ITEM_MASTER（可空）| 🔲 待填入 |
| 5 | MENU_MASTER | menu_id | 套餐/菜單組合主檔 | — | 🔲 待填入 |
| 6 | MENU_ITEMS | id（流水）| 套餐明細：品項 × 菜單多對多 | → MENU_MASTER + ITEM_MASTER | 🔲 待填入 |

### item_id 命名規則

格式：`{TYPE}-{SUBTYPE}-{SEQ3}`  例：`DES-MAC-001`

| TYPE | 中文 | 範例 |
|------|------|------|
| DES | 甜點類 | DES-MAC-001 法式馬卡龍 |
| SAV | 鹹食類 | SAV-APZ-001 義式香腸獵鳥盤 |
| DRK | 飲品類 | DRK-NCA-001 無酒精氣泡飲 |
| EQP | 設備道具 | EQP-TBL-001 6尺長桌 |
| PKG | 套餐包 | PKG-WED-001 婚禮外燴基本套 |
| SVC | 服務費用 | SVC-DEC-001 場地佈置費 |

---

## SECTION 2 — ITEM_MASTER 欄位規格

| 欄位名稱 | 資料型態 | 必填 | 說明 | 範例值 |
|----------|----------|------|------|--------|
| item_id | string | ✅ 必填 | 唯一識別碼 {TYPE}-{SUBTYPE}-{SEQ3} | DES-MAC-001 |
| item_name_zh | string | ✅ 必填 | 中文品項名稱 | 法式玫瑰馬卡龍 |
| item_name_en | string | 選填 | 英文名稱，報價單/PPT 用 | Rose Macaron |
| category | enum | ✅ 必填 | 主類別前綴：DES/SAV/DRK/EQP/PKG/SVC | DES |
| subcategory | string | 選填 | 次分類，自由填寫 | 法式甜點 |
| unit | enum | ✅ 必填 | 計價單位：個/份/盤/桌/式/人份/組/組 | 個 |
| cost_per_unit | number | 選填 | 每單位成本（TWD）業務填寫，不對外 | 45 |
| min_qty | integer | 選填 | 最低訂購數量 | 12 |
| lead_time_days | integer | 選填 | 需提前幾天確認備料 | 3 |
| is_active | boolean | ✅ 必填 | 是否目前提供：TRUE / FALSE | TRUE |
| allergens | string | 選填 | 過敏原（逗號分隔）：麩質,蛋,堅果 | 麩質,蛋 |
| notes | string | 選填 | 內部備注 | 需冷藏保存 |
| created_at | date | ✅ 必填 | 建立日期 YYYY-MM-DD | 2026-03-04 |
| updated_at | date | ✅ 必填 | 最後更新日期 YYYY-MM-DD | 2026-03-04 |

---

## SECTION 3 — PRICE_MASTER 欄位規格

| 欄位名稱 | 資料型態 | 必填 | 說明 | 範例值 |
|----------|----------|------|------|--------|
| price_id | string | ✅ 必填 | 格式：{item_id}-{price_type} | DES-MAC-001-CAT |
| item_id | string | ✅ 必填 | 對應 ITEM_MASTER.item_id | DES-MAC-001 |
| price_type | enum | ✅ 必填 | takeaway / catering / corporate / vip / seasonal | catering |
| unit_price | number | ✅ 必填 | 里價（TWD） | 65 |
| currency | string | ✅ 必填 | 幣別，預設 TWD | TWD |
| min_qty | integer | 選填 | 此價格適用的最低數量 | 24 |
| valid_from | date | 選填 | 價格生效日（空=長期）YYYY-MM-DD | 2026-01-01 |
| valid_to | date | 選填 | 價格到期日（空=長期）YYYY-MM-DD | 2026-12-31 |
| is_active | boolean | ✅ 必填 | 是否啟用：TRUE / FALSE | TRUE |
| notes | string | 選填 | 備注（如：節慶加成 20%）| 聖誕旺季加20% |

**price_type 枚舉說明：**
- takeaway：外帶/自取價，基礎定價，天天都有
- catering：外燴現場報價，含人力、運送、場地
- corporate：企業客戶專屬優惠，活動加量大或長期合作
- vip：VIP 節慶活動加量搭贈
- seasonal：季節限定特殊方案，中秋/聖誕旺季

---

## SECTION 4 — Drive 訂單資料夾結構

> 位置：[MAPLAB_DATA](https://drive.google.com/drive/u/0/folders/19RKLsBfNKuoCHVPFzT9D7tJrAdkTSmpt)

| 資料夾 | 用途 | 說明 |
|--------|------|------|
| ai_reply_system | 自動回覆系統 | 詢問單自動分類與回覆 |
| MAPLAB_ASSETS | 圖片素材庫 | 對應 ASSET_MASTER 的圖片來源 |
| 未成交_Lost Quotes | 未成交報價 | 已結案但沒有成交的客戶報價 |
| 已結案_Completed Orders | 已完成訂單 | 已成功服務完成的外燴案件 |
| 進行中_Active Orders | 進行中訂單 | 目前確認且即將服務的案件 |
| MAPLAB_外燴系統_v0.1 | 外燴系統主文件 | 報價、合約、流程相關文件 |
| MAPLAB_MasterData_Sheets | Master Data 試算表 | 本文件對應的 Sheets 主體 |

---

## SECTION 5 — 關鍵設計決策（來自 Gemini 對話 2026-03-13）

> 參考來源：https://gemini.google.com/share/c17ac8406360

**為什麼用 Google Sheets 而不是 MySQL？**

| 考量 | Google Sheets | MySQL |
|------|---------------|-------|
| 進入成本 | 極低，UI 就是全部 | 高，需要伺服器、Schema 設計 |
| 數據約束 | 軟約束，需要 Gemini 輔助格式驗證 | 硬約束，型別錯誤就存不進去 |
| 適合場景 | 外燴業務規模（< 10,000 筆）| 高併發、大量程式寫入 |
| 長期債務 | Gemini 可輔助格式驗證，風險可控 | 結構穩定，但初期建置成本高 |

**Gemini 結論：短期 1-3 年繼續用 Sheets，中期若 Sheets API 配額不足再考慮 SQLite。**

**3 個必守規則（防止 Sheets 成為爛泥）：**
1. 永遠用 item_id 做關聯，不要用「名稱」做 Key（AI 辨識錯誤率高）
2. 讓 Gemini 在寫入時即時驗證格式（100倍效率，zero-error 寫入）
3. 第一行 Header 決定後絕對不改動位置（Python 腳本依賴欄位順序）

---

## SECTION 6 — 當前任務狀態

| 任務 | 狀態 | 優先度 |
|------|------|--------|
| ITEM_MASTER 資料填入 | 🔄 進行中（截圖 + 逐條新增）| 🔴 最高 |
| PRICE_MASTER 資料填入 | 🔲 待開始 | 🟡 高 |
| ASSET_MASTER 與 Drive 圖片對應 | 🔲 待開始 | 🟡 高 |
| MENU_MASTER 套餐組合建立 | 🔲 待開始 | 🟠 中 |
| Python 讀取 Sheets API 腳本 | 🔲 待開始 | 🟠 中（等資料填完） |
| 自動報價系統整合 | 🔲 待開始 | 🟢 低（依賴上方完成）|

> ⚠️ 重要：目前 Sheets 的「資料輸入區」欄位為空白，正在用截圖 + 手動方式逐條新增。  
> Agent 接手時**不要動**目前正在填寫的欄位，以免覆蓋人工輸入進度。

---

## SECTION 7 — 接手 SOP

1. **確認 Sheets 狀態**：開啟 MAPLAB_MasterData_Sheets，看 1_ITEM_MASTER 目前填了幾筆
2. **看 Drive Active Orders**：了解目前有哪些進行中案件，確認哪些品項需要優先建檔
3. **格式驗證**：新增任何 item_id 前先確認命名規則 {TYPE}-{SUBTYPE}-{SEQ3}
4. **不干擾進行中填寫**：如果看到資料輸入區有資料，詢問用戶目前填到哪裡
5. **完成後更新本文件** SECTION 6 的任務狀態

---

## SECTION 8 — 版本紀錄

| 版本 | 日期 | 說明 | 更新者 |
|------|------|------|--------|
| v1.0 | 2026-03-13 | 初始框架建立（來自 Gemini 對話 + Drive 結構分析）| Claude (Sonnet 4.6) |
