# Master Data Agent — MAPLAB Kitchen ERP 技術文件

版本：v1.4 | 建立：2026-03-13 | 更新：2026-03-15 | 狀態：Dashboard 修復 + QUOTE_DRAFT 收尾 + 版本號修正

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
| Dashboard #REF! 修復 | ✅ 完成 | 🔴 最高 |
| QUOTE_DRAFT v0.3 建立 + 收尾 | ✅ 完成（分類中文化）| 🟡 高 |
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

## SECTION 8 — 報價系統改進分析（A5 研究，2026-03-13）

> 來源：Gemini 對話 https://gemini.google.com/share/e579c8655cd4 + 現有系統 v0.2 分析
>
> ### 現有系統（MAPLAB_外燴系統_v0.1 / v0.2）現況
>
> - Dashboard：Order Summary（88筆）、7天預警、Overdue/Unpaid（#REF! 待修正）
> - - Orders：訂單主表含客戶資訊、活動資訊（未含「客戶類型」欄位）
- OrderLines：品項明細，含 normalized_item_name、category、qty、unit_price、line_total
- - OrderCharges：加項/折扣/服務費（service_fee / extra / rental / discount / note）
  - - Items：品項主表（item_id、category、standard_name、default_price、cost、unit、batch_size、active）
    - - Specials：特殊品項追蹤（空白，待填入）
      - 
      ### 發現的問題與缺口
      
      1. **缺乏雙模式報價引擎**：目前 Orders 只記錄已確認訂單，無「報價草稿」與「正式訂單」分流
      2. 2. **無業務決策緩衝區**：沒有「建議售價 vs 最終報價」的 diff 欄位，業務調整無法追蹤
      3. **缺少客戶類型分類**：無法區分「行銷公司/一般家庭/外帶客人/企業全包」等客群，無法套用不同成本建議值
      4. **無逆向報價模式**：企業客戶給固定預算（如 NT$30,000 全包）時，系統無法從總預算回推可用食材預算
      5. **無難度係數（Pain Surcharge）**：搬運環境惡劣、溝通成本高等場地條件無法量化加成
      6. **Items 與 ITEM_MASTER 分離**：目前 v0.2 的 Items sheet 命名規則（如 DST001）與 MasterData 的 {TYPE}-{SUBTYPE}-{SEQ3} 不一致，需對齊
      7. 7. **無 Google Slides 串接**：尚未實現「選品項→自動替換簡報圖片→一鍵匯出 PDF」的完整流程
      8. **Dashboard 有 #REF! 錯誤**：Overdue/Unpaid 區塊公式斷連，需修復
      9.
      10. ### 報價系統改進方案（v0.3 目標）
      
      #### 模組 A：雙模式報價引擎
      - 新增 `QUOTE_DRAFT` sheet：報價草稿，選品後自動計算
      - 欄位：quote_id / order_id（空=草稿）/ client_type（行銷公司/一般家庭/外帶/企業全包）/ pricing_mode（standard=正向 / reverse=逆向）
      - - 正向模式：選品項 → 系統算建議售價 → 業務填最終金額 → 生成 PDF
      - 逆向模式：填客戶預算 → 扣固定成本 → 顯示可用食材預算
      
      #### 模組 B：業務決策緩衝區
      - `suggested_price`（系統計算）vs `final_price`（業務調整，必填才能生成 PDF）
      - 若 final_price < 成本底線 → 儲存格變紅色警告
      - 難度係數勾選框：搬運惡劣 +5%、高溝通成本 +5%、急單/特殊時段 +10%
      -
      #### 模組 C：Google Slides 整合
      - Slides 模板使用 `{{client_name}}`、`{{event_date}}`、`{{total_price}}` 佔位符
      - 圖片框用 Alt Text 命名對應品項 ID
      - - GAS 腳本：複製模板 → 替換文字 → 替換圖片 URL → 匯出 PDF → 存入 Drive → 回填 PDF 連結到 Orders
        - 
        #### 模組 D：客戶類型參考成本佔比表
        | 客戶類型 | 建議成本佔比 | 說明 |
        |---------|------------|------|
        | 行銷公司 | 25-30% | 溝通成本高，修改次數多 |
        | 一般家庭 | 35-40% | 價格較敏感 |
        | 外帶客人 | 45% | 服務/搬運成本極低 |
        | 企業全包 | 視固定成本扣除後決定 | 逆向報價模式 |

        ### 優先執行順序
        
        1. 🔴 修復 Dashboard #REF! 錯誤
        2. 🔴 對齊 Items 命名規則至 ITEM_MASTER 格式（需等其他 agent 完成 ITEM_MASTER 填入）
        3. 🟡 新增 QUOTE_DRAFT sheet + 業務決策欄位
        4. 4. 🟡 新增客戶類型 + 難度係數欄位到 Orders
        5. 🟠 GAS 腳本 MVP：至少達成「替換一個文字 + 匯出 PDF」
        6. 6. 🟢 逆向報價模式（企業全包案型）
        
        ---

        ## SECTION 9 — 版本紀錄
        
        | 版本 | 日期 | 說明 | 更新者 |
        |------|------|------|--------|
        | v1.0 | 2026-03-13 | 初始框架建立（來自 Gemini 對話 + Drive 結構分析）| Claude (Sonnet 4.6) |
        | v1.1 | 2026-03-13 | 新增 SECTION 8 報價系統分析：現況盤點、缺口識別、改進方案 v0.3 目標 | Claude (Sonnet 4.6) A5 |
| v1.2 | 2026-03-13 | QUOTE_DRAFT v0.3 建立完成：雙模式報價系統（正向/逆向）、15品項參考表、2組Demo資料 | Claude (Sonnet 4.6) A5 |
| v1.3 | 2026-03-14 | Dashboard #REF! 修復（QUERY LIMIT 10）+ QUOTE_DRAFT 品項分類中文化（甜點/餐食小點/主食/飲品）| Claude (Opus 4.6) A5 |


---

## SECTION 3 — Schema v0.1 任務書（A5 啟動任務）

**任務狀態：⚡ 待啟動**

**任務目標：** 建立 MAPLAB Kitchen ERP 最小可用 schema v0.1，讓 A4 Pipeline Agent 可以接手規劃資料流程。

**負責 Agent：** A5 Master Data Agent

**完成期限：** 啟動後第一個工作週期

### 必須產出的 4 個文件

**產出 1：`schema-v0.1.md`**
包含以下 4 張表的基本欄位定義：
- Orders（訂單表）：訂單編號、客戶ID、活動日期、活動類型、地點、總金額、狀態
- Customers（客戶表）：客戶ID、姓名、聯絡電話、Email、歷史訂單數
- Events（活動表）：活動ID、活動名稱、日期、地點、人數、關聯訂單ID
- Items（品項表）：品項ID、品項名稱、類別、單價、單位、是否有庫存

**產出 2：`table-relationship-map.md`**
說明 4 張表之間的主鍵/外鍵關係，以及資料流向。

**產出 3：`field-naming-rules.md`**
統一命名規則（例如：ID欄位格式、日期格式、狀態欄位的允許值清單）。

**產出 4：`handoff-to-A4.md`**
交接文件，說明 A4 需要知道的：schema 的使用方式、pipeline 需要對接的欄位、命名規則。

### 成功條件

- [ ] 4 張表的基本欄位均已定義
- [ ] 主鍵邏輯清楚（每張表都有唯一識別欄位）
- [ ] 命名規則有明確規範
- [ ] A4 可以根據 handoff 文件獨立開始工作
- [ ] A1 已回寫 PROJECT_CONTEXT 與 CHANGELOG

### 啟動方式

任何 Agent（或 Gemini）接到 A5 任務時，先讀：
1. 本文件 SECTION 0–3
2. CURRENT_EXECUTION_BOARD.md 的 A5 區塊
3. AGENT_STARTUP_PROTOCOL.md

---

*版本：v1.4 | 更新：2026-03-14 | 新增 SECTION 3 Schema v0.1 任務書*
