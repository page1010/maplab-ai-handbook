# Master Data Agent — MAPLAB Kitchen ERP 技術文件

版本：v1.6 | 建立：2026-03-13 | 更新：2026-03-24 | 狀態：Items 清洗完成 + T-A5-001 完成 + QUOTE_DRAFT 框架規劃 + Slides 整合設計

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
4. 確認進度：CURRENT_STATUS.md + TASK_QUEUE.md（GitHub 唯一真相）

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
| ITEM_MASTER Items 品項清洗 | ✅ 完成（300→139 筆，BEV 容量分離+去重+後綴清除）| 🔴 最高 |
| 甜點（DST）去重 + 全品項重新編碼 | ⏸️ 等使用者手動去重（T-A5-001） | 🔴 最高 |
| QUOTE_DRAFT 極簡報價單 MVP | ✅ 完成（下拉選品項→VLOOKUP 帶出成本）| 🟡 高 |
| QUOTE_DRAFT 增強（飲料容量/保冰桶/招待）| 🔲 待開始（T-A5-002，需 T-A5-001 完成）| 🟡 高 |
| TimeTree 2025 全年外燴密集日清單 | ✅ 完成 | 🟡 高 |
| 熱客招待品項定義 | 🔲 待開始（T-A5-003）| 🟠 中 |
| 使用者填 Items.D 欄 default_price | ⏸️ 等使用者（T-A5-004）| 🔴 最高 |
| PRICE_MASTER 資料填入 | 🔲 待開始 | 🟡 高 |
| ASSET_MASTER 與 Drive 圖片對應 | 🔲 待開始 | 🟡 高 |
| MENU_MASTER 套餐組合建立 | 🔲 待開始 | 🟠 中 |
| Dashboard #REF! 修復 | ✅ 完成 | — |
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

## SECTION 10 — Schema v0.1 任務書（A5 啟動任務，已完成）

**任務狀態：✅ 已完成（Schema v0.1 framework 在 SECTION 1-3 定義，Items 品項已清洗至 139 筆）**

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

**產出 4：`handoff-to-A4.md`**h
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

*版本：v1.5 | 更新：2026-03-19 | A1 巡查修正：任務狀態更新 + SECTION 編號修正 + 移除 Notion 引用*

> 新技能書：skills/sheets-data-cleaning-guide.md — A5 資料清洗公式+腳本工具箱


## SECTION 11 — QUOTE_DRAFT 完善框架設計（A5 研究，2026-03-24）

### 11.1 現狀盤點

**現有 QUOTE_DRAFT（v0.1 — 目前線上使用中）**

QUOTE_DRAFT 是目前實際使用的報價表格，結構為「類報價單」格式，直接面向客戶輸出：

| 區域 | 列範圍 | 內容 | 說明 |
|------|--------|------|------|
| 表頭 | Row 1 | MAP LAB KITCHEN 私廚/外燴 訂單 | 品牌標題 |
| 客戶資訊 | Row 2-4 | 客戶名、日期、活動類型、電話、時間 | 手動填入 |
| 品項區段 | Row 6-19 | 分三類：鹹食小點(APP)/甜點(DST)/8L壺裝飲品(BEV) | D欄下拉選品項，G欄VLOOKUP帶出單位成本 |
| 招待區 | Row 20-21 | 熱客招待 Complimentary | 精選小西點等 |
| 費用加項 | Row 23-30 | 餐點/10%服務費/加購餐點/租借長桌/一次性餐具/車馬費/2F搬運費 | 項目+金額+備註 |
| 成本匯總 | Row 31-33 | 額外成本/總金額/訂單成本/毛利率 | 公式自動計算 |
| 條款 | Row 35+ | 簽約使用條款及細則（訂金/付款/取消/不可抗力） | 固定文字 |

核心公式：`=IF(D9="","",IFERROR(VLOOKUP(D9,Items!C:E,3,0),"N/A"))` — 品項名稱 → Items!default_cost

**現有 QUOTE_V2_FUTURE（v0.3 — 框架已建但未上線）**

QUOTE_V2_FUTURE 是 v0.3 版「雙模式報價引擎」的原型框架，由 quoteDraft_v03.gs 建立：

| 區段 | 欄位 | 說明 |
|------|------|------|
| [A] CLIENT INFO | client_name, pax, client_type, pain_% | 客戶類型下拉（general_family/enterprise_all_in等）+ 難度係數 |
| [B] ITEM SELECTION | item_id, item_name(auto), unit_price(auto) | 從 Items 表帶出品名+價格 |
| [C] FORWARD QUOTE | qty, food_cost, suggested_price, final_price | 正向報價：選品→算成本→建議售價→業務決定最終價 |
| [D] REVERSE QUOTE | total_budget, fixed_cost, avail_food_budget | 逆向報價：填總預算→扣固定成本→顯示可用食材額度 |
| [TOTAL] Row 24 | 各欄合計 | food_cost/suggested_price/final_price 加總 |

### 11.2 發現的關鍵問題與缺口

1. **v0.1 與 v0.3 斷裂**：QUOTE_DRAFT(v0.1) 是實際在用的報價單，但 QUOTE_V2_FUTURE(v0.3) 的結構設計完全不同，兩者之間缺乏遷移路徑
2. 2. **Items 資料連結不完整**：v0.1 用 VLOOKUP(D9,Items!C:E,3,0) 查 default_cost（E欄），但 Items 的 default_cost 全部是 0（T-A5-004 等使用者填入），導致成本欄顯示為 0 或 N/A
   3. 3. **缺少 default_price**：Items.D 欄 default_price 是對外報價的基礎，目前等使用者手動填入（T-A5-004 Blocker）
      4. 4. **品項分類不夠靈活**：v0.1 只有 APP/DST/BEV 三類固定區段，缺少主食(MAIN)類別，無法動態增減品項行數
         5. 5. **無客戶類型區分**：v0.1 無法根據客群（行銷公司/一般家庭/企業全包）套用不同成本建議值
            6. 6. **無業務決策記錄**：suggested_price vs final_price 的差異無法追蹤，業務調價沒有留痕
               7. 7. **Slides 串接斷裂**：已有 generateProposal.gs 和 slidesV2.gs 腳本，但與 QUOTE_DRAFT 的資料流尚未打通
                  8. 8. **報價單→訂單流程缺失**：草稿確認後無法一鍵轉為正式 Orders 記錄
                    
                     9. ### 11.3 完善後的 QUOTE_DRAFT 框架設計（v1.0 目標）
                    
                     10. 設計原則：保留 v0.1 的「對外報價單」外觀（客戶可看），內嵌 v0.3 的「業務決策引擎」（內部用）
                    
                     11. **區段 A：客戶資訊區（Row 1-5）**
                    
                     12. | 欄位 | 位置 | 來源 | 說明 |
                     13. |------|------|------|------|
                     14. | 品牌標題 | A1:F1 | 固定 | MAP LAB KITCHEN 私廚/外燴 |
                     15. | quote_id | A2 | 自動生成 | 格式：QD-YYYYMMDD-SEQ（如 QD-20260527-001）|
                     16. | client_name | C2 | 手動填入 | 客戶名稱 |
                     17. | event_date | C3 | 手動填入 | 活動日期 YYYY/MM/DD |
                     18. | event_type | E3 | 下拉選單 | 尾牙/婚宴/企業活動/家庭聚餐/生日派對/其他 |
                     19. | event_time | F2 | 手動填入 | 活動時間 |
                     20. | contact_phone | E4 | 手動填入 | 聯絡電話 |
                     21. | pax | G2 | 手動填入 | 用餐人數 |
                     22. | client_type | G3 | 下拉選單 | general_family / marketing_agency / enterprise_all_in / takeaway |
                     23. | pain_surcharge | G4 | 下拉選單 | normal(+0%) / heavy_transport(+5%) / high_communication(+5%) / combined(+15%) |
                    
                     24. **區段 B：品項選擇區（Row 7-22）— 動態連結 Items 資料庫**
                    
                     25. | 欄 | 欄位名 | 公式/來源 | 說明 |
                     26. |----|--------|----------|------|
                     27. | A | 序號 | 自動 | 1,2,3... |
                     28. | B | 類別標籤 | 合併儲存格 | 創意異國鹹食小點 / 手作精緻甜點 / 8L壺裝飲品 / 主食 |
                     29. | C | 品項分類 | 自動 | 根據 item_id 前綴判斷 APP/DST/BEV/MAIN |
                     30. | D | 品項名稱 | **下拉選單** | 資料驗證來源：DropdownHelper 依類別分組（LIST_APP/LIST_DST/LIST_BEV/LIST_MAIN）|
                     31. | E | item_id | 自動 | `=IFERROR(VLOOKUP(D_,Items!C:A,-2,0),"")` 反查 item_id |
                     32. | F | 數量 | **手動填入** | 業務填入訂購數量 |
                     33. | G | 單位成本 | 自動 | `=IFERROR(VLOOKUP(D_,Items!C:E,3,0),"N/A")` 查 Items.default_cost |
                     34. | H | 小計(成本) | 自動 | `=IF(F_="","",F_*G_)` |
                     35. | I | 單價(報價) | 自動 | `=IFERROR(VLOOKUP(D_,Items!C:D,2,0),"N/A")` 查 Items.default_price |
                     36. | J | 小計(報價) | 自動 | `=IF(F_="","",F_*I_)` |
                     37. | K | 單位 | 自動 | `=IFERROR(VLOOKUP(D_,Items!C:F,4,0),"")` 查 Items.unit |
                    
                     38. 品項下拉選單機制（DropdownHelper sheet 提供）：
                     39. - LIST_APP：餐食小點品項（APP001-APP050）的 standard_name 清單
                         - - LIST_DST：甜點品項（DST001-DST041）的 standard_name 清單
                           - - LIST_BEV：飲品品項（BEV001-BEV008）的 standard_name 清單
                             - - LIST_MAIN：主食品項（MAIN001-MAIN009）的 standard_name 清單
                               - - 由 reorganizeItems.gs 的 buildDropdownHelper() 函式維護
                                
                                 - **區段 C：費用加項區（Row 23-31）**
                                
                                 - | 列 | 項目 | 金額 | 備註 |
                                 - |----|------|------|------|
                                 - | 23 | 餐點小計 | =SUM(J品項區) | 品項報價合計 |
                                 - | 24 | 10%服務費 | =Row23*10% | 自動計算 |
                                 - | 25 | 加購餐點 | 手動 | 額外品項 |
                                 - | 26 | 租借長桌 | 手動 | 設備租借 |
                                 - | 27 | 加購一次性餐具 | 手動 | 耗材 |
                                 - | 28 | 車馬費 | 手動 | 交通運輸 |
                                 - | 29 | 2F搬運費 | 手動 | 樓層搬運 |
                                 - | 30 | 難度加成 | =小計*pain_surcharge% | 自動計算，依 pain_surcharge 選項 |
                                 - | 31 | **總金額** | =SUM(23:30) | 最終報價 |
                                
                                 - **區段 D：業務決策區（Row 32-35，內部用，列印時隱藏）**
                                
                                 - | 列 | 欄位 | 公式 | 說明 |
                                 - |----|------|------|------|
                                 - | 32 | 訂單成本 | =SUM(H品項成本區) | 食材成本合計 |
                                 - | 33 | 毛利率 | =(總金額-訂單成本)/總金額 | 自動計算，<30% 變紅色警告 |
                                 - | 34 | 建議售價參考 | 依 client_type 成本佔比反推 | 行銷公司25-30%/一般家庭35-40%/外帶45% |
                                 - | 35 | 價格檢查 | =IF(總金額<訂單成本,"⚠️ 低於成本!","✓ OK") | 底線警告 |
                                
                                 - ### 11.4 Google Slides 整合設計
                                
                                 - **實際應用場景（參考：WenXueGuan_20260527_23000 簡報）**
                                
                                 - 現有 Slides 模板為 6 頁企業提案簡報：
                                 - 1. **封面** — MAPLAB Kitchen / CATERING SERVICE / Premium Event Catering SINCE 2016
                                   2. 2. **About Us** — 公司介紹 + 數據亮點（200+ Events / 50+ Clients / 98% Satisfaction / 10yr）
                                      3. 3. **Our Services** — 三大服務：Birthday Party / Wedding Catering / Corporate Events
                                         4. 4. **Selected Works** — 四格作品集：AMD Corporate Event / Garden Wedding / Brand Launch Party / Year-End Gala
                                            5. 5. **Our Advantages** — 五大優勢：Local Roots / Custom Flexibility / Aesthetic Focus / Expert Team / Food Safety
                                               6. 6. **Trusted By** — 合作夥伴（與 Advantages 相同版面，替換圖片）
                                                 
                                                  7. **報價單→Slides 自動生成流程**
                                                 
                                                  8. 當報價草稿完成時，一鍵觸發 generateClientProposal() 函式：
                                                 
                                                  9. 1. **STEP 1 複製模板**：DriveApp.getFileById(MASTER_ID).makeCopy(newName)
                                                     2. 2. **STEP 2 讀取 Items**：從 Items sheet 取得品項資料（category/standard_name/active/item_id）
                                                        3. 3. **STEP 3 文字替換**：在模板 Slides 中替換佔位符
                                                           4.    - `{{client_name}}` → 客戶名稱
                                                                 -    - `{{event_date}}` → 活動日期
                                                                      -    - `{{event_type}}` → 活動類型
                                                                           -    - `{{total_price}}` → 總金額
                                                                                -    - `{{pax}}` → 用餐人數
                                                                                     - 4. **STEP 4 品項列表生成**：讀取 QUOTE_DRAFT 已選品項，按類別分組插入 Slides
                                                                                       5. 5. **STEP 5 圖片替換**：根據品項的 item_id 查找 ASSET_MASTER 對應圖片 URL，替換 Slides 中的 placeholder 圖片
                                                                                          6. 6. **STEP 6 匯出**：匯出為 PDF → 存入 Drive 對應訂單資料夾 → 回填 PDF 連結到 QUOTE_DRAFT
                                                                                            
                                                                                             7. **已有的 Apps Script 腳本盤點**
                                                                                            
                                                                                             8. | 腳本 | 函式 | 功能 | 狀態 |
                                                                                             9. |------|------|------|------|
                                                                                             10. | createSlides.gs | createMAPLABSlides() | 從零建立 6 頁品牌簡報（硬編碼版） | ✅ 可執行 |
                                                                                             11. | slidesV2.gs | createMAPLABSlidesV2() | V2 版品牌簡報（改良色彩/字型） | ✅ 可執行 |
                                                                                             12. | beautifyV2.gs | — | V2 美化輔助 | ✅ |
                                                                                             13. | generateProposal.gs | generateClientProposal() | 複製 Master 模板 → 讀 Items → 動態生成品項頁 | 🔲 框架完成，需與 QUOTE_DRAFT 串接 |
                                                                                             14. | quoteDraft_v03.gs | buildQuoteDraftSheet() | 建立 QUOTE_V2_FUTURE 表格框架 | ✅ 已建立框架 |
                                                                                            
                                                                                             15. ### 11.5 資料流全圖
                                                                                            
                                                                                             16. ```
                                                                                                 [使用者操作]                    [自動化]                     [輸出]
                                                                                                      |                            |                           |
                                                                                                   填客戶資訊 ──→ QUOTE_DRAFT ──→ 自動帶出品項資料    ──→ 報價單 PDF
                                                                                                      |              ↕                  ↕                      |
                                                                                                   選品項(下拉) ──→ Items sheet ──→ VLOOKUP 帶出          Slides 提案
                                                                                                      |              ↕           price/cost/unit              PDF
                                                                                                   填數量 ────→ 自動計算 ──→ 成本/毛利/建議售價      ──→ 業務決策
                                                                                                      |                            |                           |
                                                                                                   確認報價 ──→ 轉入 Orders ──→ 正式訂單               Drive 歸檔
                                                                                                 ```

                                                                                                 ### 11.6 現在的困難

                                                                                                 | 困難 | 嚴重度 | 依賴 | 說明 |
                                                                                                 |------|--------|------|------|
                                                                                                 | Items.default_price 全空 | 🔴 最高 | T-A5-004 等使用者 | 沒有報價基礎價格，VLOOKUP 無法帶出對外售價 |
                                                                                                 | Items.default_cost 全為 0 | 🔴 最高 | T-A5-004 等使用者 | 成本數據缺失，毛利率計算無意義 |
                                                                                                 | ASSET_MASTER 未建立 | 🟡 中 | 需建立 | Slides 圖片替換需要品項 → 圖片 URL 的對應表 |
                                                                                                 | PRICE_MASTER 未填入 | 🟡 中 | 需 Items 完成 | 多層級定價（外帶/外燴/企業）無法實現 |
                                                                                                 | v0.1 → v1.0 遷移風險 | 🟠 中高 | 需謹慎 | 現有 QUOTE_DRAFT 正在使用中（如 WenXueGuan 案），不能直接覆蓋 |
                                                                                                 | Slides Master 模板需更新 | 🟡 中 | 設計決策 | 現有模板是品牌形象簡報，需新增「報價明細」頁面模板 |

                                                                                                 ### 11.7 接下來的計畫（執行順序）

                                                                                                 **Phase 1：資料基底補齊（🔴 最高優先，依賴使用者）**
                                                                                                 1. T-A5-004：使用者填入 Items.D 欄 default_price — 所有後續功能的基礎
                                                                                                 2. 2. T-A5-004b：使用者填入 Items.E 欄 default_cost — 成本計算的基礎
                                                                                                    3. 3. 驗證：填入後跑一次 VLOOKUP 測試，確認 QUOTE_DRAFT 品項選擇能正確帶出 price/cost
                                                                                                      
                                                                                                       4. **Phase 2：QUOTE_DRAFT v1.0 升級（🟡 高優先）**
                                                                                                       5. 1. 在現有 QUOTE_DRAFT 旁邊新建 QUOTE_V1 sheet（不動現有表格）
                                                                                                          2. 2. 套用 11.3 框架設計：客戶資訊區 + 品項選擇區 + 費用加項區 + 業務決策區
                                                                                                             3. 3. 品項欄動態連結：D欄下拉 → VLOOKUP 帶出 item_id / cost / price / unit
                                                                                                                4. 4. 新增 client_type + pain_surcharge 下拉選單
                                                                                                                   5. 5. 新增條件式格式：毛利率 < 30% 變紅、final_price < cost 變紅
                                                                                                                      6. 6. 測試完成後，將 QUOTE_DRAFT 重命名為 QUOTE_DRAFT_legacy，新表改名為 QUOTE_DRAFT
                                                                                                                        
                                                                                                                         7. **Phase 3：Slides 整合（🟠 中優先）**
                                                                                                                         8. 1. 更新 Slides Master 模板：新增「報價明細」頁（品項表格 + 價格）
                                                                                                                            2. 2. 修改 generateProposal.gs：從 QUOTE_DRAFT 讀取客戶資訊 + 已選品項
                                                                                                                               3. 3. 佔位符替換：{{client_name}}/{{event_date}}/{{total_price}}/{{pax}} 等
                                                                                                                                  4. 4. 品項列表動態生成：按類別分頁或分區塊排列
                                                                                                                                     5. 5. PDF 匯出 + Drive 歸檔 + 連結回填
                                                                                                                                       
                                                                                                                                        6. **Phase 4：報價→訂單流程（🟢 低優先）**
                                                                                                                                        7. 1. 新增「確認報價」按鈕（Apps Script + UI 按鈕）
                                                                                                                                           2. 2. 一鍵將 QUOTE_DRAFT 轉為 Orders + OrderLines 記錄
                                                                                                                                              3. 3. 自動更新 Dashboard 統計
                                                                                                                                                
                                                                                                                                                 4. ### 11.8 Slides 提案簡報規格（與報價單同步輸出）
                                                                                                                                                
                                                                                                                                                 5. **目標**：報價確認後自動產出一份 Slides 提案簡報 PDF，內含：
                                                                                                                                                
                                                                                                                                                 6. | 頁次 | 內容 | 資料來源 |
                                                                                                                                                 7. |------|------|----------|
                                                                                                                                                 8. | 1 | 封面：MAPLAB Kitchen + 客戶名 + 活動日期 | QUOTE_DRAFT 客戶資訊區 |
                                                                                                                                                 9. | 2 | About Us：公司介紹 + 數據亮點 | 固定（Master 模板） |
                                                                                                                                                 10. | 3 | Our Services：三大服務項目 | 固定（Master 模板） |
                                                                                                                                                 11. | 4 | Selected Works：過往作品展示 | 固定/可選（ASSET_MASTER） |
                                                                                                                                                 12. | 5 | **Menu Proposal**：本次報價品項列表 + 價格 | QUOTE_DRAFT 品項選擇區 |
                                                                                                                                                 13. | 6 | **Menu Photos**：已選品項的實際照片拼圖 | ASSET_MASTER 圖片 URL |
                                                                                                                                                 14. | 7 | Our Advantages：五大優勢 | 固定（Master 模板） |
                                                                                                                                                 15. | 8 | Trusted By / Contact：合作夥伴 + 聯繫方式 | 固定（Master 模板） |
                                                                                                                                                
                                                                                                                                                 16. 第 5-6 頁是「動態頁」，根據 QUOTE_DRAFT 選擇的品項自動生成。
                                                                                                                                                
                                                                                                                                                 17. ---
                                                                                                                                                
                                                                                                                                                 18. ## SECTION 9 版本紀錄（更新）
                                                                                                                                                
                                                                                                                                                 19. | 版本 | 日期 | 說明 | 更新者 |
                                                                                                                                                 20. |------|------|------|--------|
                                                                                                                                                 21. | v1.6 | 2026-03-24 | 新增 SECTION 11：QUOTE_DRAFT 完善框架設計（現狀盤點 + v1.0 框架 + Slides 整合 + 困難 + 計畫） | Claude (Opus 4.6) A5 |
                                                                                                                                                 22. | v1.5 | 2026-03-19 | A1 巡查修正：任務狀態更新 + SECTION 編號修正 | A1 |
                                                                                                                                                 23. | v1.3 | 2026-03-14 | Dashboard #REF! 修復 + QUOTE_DRAFT 品項分類中文化 | Claude (Opus 4.6) A5 |
                                                                                                                                                 24. | v1.2 | 2026-03-13 | QUOTE_DRAFT v0.3 建立完成：雙模式報價系統 | Claude (Sonnet 4.6) A5 |
                                                                                                                                                 25. | v1.1 | 2026-03-13 | 新增 SECTION 8 報價系統分析 | Claude (Sonnet 4.6) A5 |
                                                                                                                                                 26. | v1.0 | 2026-03-13 | 初始框架建立 | Claude (Sonnet 4.6) |
                                                                                                                                                 27. 
