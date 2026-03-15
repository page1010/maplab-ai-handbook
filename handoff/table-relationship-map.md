# MAPLAB Kitchen ERP — Table Relationship Map

版本：v0.1 | 建立：2026-03-15 | 負責：A5 Master Data Agent

---

## 表關係總覽

```
+------------------+       +------------------+
|   Customers      |       |   Items          |
|------------------|       |------------------|
| customer_id (PK) |       | item_id (PK)     |
| name_zh          |       | item_name_zh     |
| phone            |       | category         |
| email            |       | unit_price       |
| order_count      |       | unit             |
| ...              |       | is_active        |
+--------+---------+       +--------+---------+
         |                          |
         | 1                        | M
         v                          v
+------------------+       +------------------+
|   Orders         |       |   OrderLines     |
|------------------|       |  (future v0.2)   |
| order_id (PK)    |<----->|------------------|
| customer_id (FK) |  1:M  | order_id (FK)    |
| event_date       |       | item_id (FK)     |
| event_type       |       | qty              |
| total_amount     |       | unit_price       |
| status           |       | line_total       |
+--------+---------+       +------------------+
         | 1
         v
+------------------+
|   Events         |
|------------------|
| event_id (PK)    |
| order_id (FK)    |
| event_name       |
| guest_count      |
| difficulty_level |
| ...              |
+------------------+
```

---

## 主鍵 / 外鍵說明

| 表名 | 主鍵 (PK) | 外鍵 (FK) | 指向 |
|------|----------|----------|------|
| Customers | customer_id | 無 | — |
| Orders | order_id | customer_id | Customers.customer_id |
| Events | event_id | order_id | Orders.order_id |
| Items | item_id | 無 | — |
| OrderLines (未來) | id | order_id, item_id | Orders + Items |

---

## 資料流向說明

**建立一筆訂單的流程：**

**Step 1.** 客戶資料 → 建立/查找 Customers 記錄（取得 customer_id）  
**Step 2.** 建立 Orders 記錄（帶入 customer_id）  
**Step 3.** 建立 Events 記錄（帶入 order_id）  
**Step 4.** 從 Items 選取品項 → 寫入 OrderLines（帶入 order_id + item_id）  
**Step 5.** 自動計算 Orders.total_amount = SUM(OrderLines.line_total)

---

## 現階段 v0.1 範圍

- 目前實作：**4 張主表**（Customers / Orders / Events / Items）
- OrderLines 列為 **v0.2 擴展項目**，目前用 Orders.total_amount 手動結算替代
- ITEM_MASTER 對應關係：Items 表 = MasterData Sheets 的 `1_ITEM_MASTER`，同一命名規則

---

## 版本紀錄

| 版本 | 日期 | 說明 |
|------|------|------|
| v0.1 | 2026-03-15 | 初稿：4 張表 PK/FK 關係圖 + 資料流向 |
