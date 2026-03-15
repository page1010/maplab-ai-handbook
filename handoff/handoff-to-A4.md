# A5 → A4 交接文件 — Schema v0.1 Handoff

版本：v0.1 | 建立：2026-03-15 | 交接方：A5 Master Data Agent | 接收方：A4 Pipeline Agent

---

## A4你好！這份文件是你需要知道的全部

A5 已完成 Schema v0.1 的所有必要產出。你可以根據本文件獨立開始 pipeline 設計。

---

## 你需要連接的資料來源

| 資料 | 位置 | 說明 |
|------|------|------|
| Schema 定義 | `handoff/schema-v0.1.md` | 4 張表完整欄位規格 |
| 表關係圖 | `handoff/table-relationship-map.md` | PK/FK + 資料流向 ASCII 圖 |
| 命名規則 | `handoff/field-naming-rules.md` | ID 格式 / 日期格式 / Enum 允許値 |
| 實際資料 | Google Sheets `MAPLAB_MasterData_Sheets` | 目前只有 Items 欄位定義，資料區空白 |

---

## 4 張表的核心資訊（快速參考）

**Customers**
- PK: `customer_id`（格式: CUS-{SEQ3}）
- 關鍵欄: name_zh, phone, email

**Orders**
- PK: `order_id`（格式: ORD-YYYYMM-{SEQ3}）
- FK: `customer_id` → Customers
- 關鍵欄: event_date, event_type, total_amount, status
- status 允許値: draft / confirmed / completed / cancelled

**Events**
- PK: `event_id`（格式: EVT-YYYYMM-{SEQ3}）
- FK: `order_id` → Orders
- 關鍵欄: guest_count, difficulty_level, venue

**Items**
- PK: `item_id`（格式: {TYPE}-{SUBTYPE}-{SEQ3}，如 DES-MAC-001）
- 關鍵欄: item_name_zh, category, unit_price, unit, is_active
- 對應: MasterData Sheets 的 `1_ITEM_MASTER`

---

## A4 你的任務范圍

根據以上 schema，設計並建立以下 pipeline：

**Step 1.** 資料讀入 pipeline
- 從 Google Sheets 讀取 ITEM_MASTER 資料
- 從 Google Drive Active Orders 對應 Orders / Customers 資料

**Step 2.** 資料驗證 pipeline
- 檢查 item_id 格式是否符合 {TYPE}-{SUBTYPE}-{SEQ3}
- 檢查 order_id FK 是否對應到存在的 customer_id
- 檢查日期格式是否為 YYYY-MM-DD
- 檢查 status / event_type 是否在允許 enum 値內

**Step 3.** 資料寫出 / 輸出 pipeline
- 將驗證後的資料寫入 Sheets 或產生輸出 JSON/CSV
- 將錯誤清單寫入 `pipeline-errors.log`（過後回寫給 A5）

**Step 4.** 交接結果寫入
- 完成後更新 `CURRENT_EXECUTION_BOARD.md` 的 A4 狀態區塊
- 將 pipeline schema 需求回寫給 A5／回寫給 A1

---

## 重要限制與注意事项

- 不得自行修改 Sheets 的欄位順序（Python 腳本依賴欄位順序）
- 不得直接寫入 cost_per_unit 到公開輸出
- 目前 Sheets 資料區為空白，資料讀入 pipeline 先跟空表驗證即可
- OrderLines 表列為 v0.2 擴展，目前不实作

---

## A5 還需要你對齊的項目

完成 pipeline 后，請回寫以下資訊給 A5：

- pipeline 驗證規則有否發現缺缺或衝突？
- Items 表有哪些欄位 A4 需要但 v0.1 沒有定義的？
- pipeline 錯誤清單有哪些常見問題需要 schema 修正？

---

## 版本紀錄

| 版本 | 日期 | 說明 |
|------|------|------|
| v0.1 | 2026-03-15 | A5 完成 Schema v0.1 全部產出，交接 A4 開始 pipeline |
