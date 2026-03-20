# MAPLAB Kitchen ERP — Schema v0.1

版本：v0.1 | 建立：2026-03-14 | 狀態：初稿 | 負責：A5 Master Data Agent

---

## 說明

本文件定義 MAPLAB Kitchen ERP 核心 4 張資料表的欄位規格。
目的是讓 A4 Pipeline Agent 有明確的資料結構可以規劃資料流程。

> 注意：這是 v0.1 最小可用版本（MVP Schema），以「能跑通第一條閉環」為原則，不追求完整性。

---

## TABLE 1 — Orders（訂單表）

**主鍵：** `order_id`  
**用途：** 記錄每一筆外熴/外帶訂單的核心資訊。

| 欄位名稱 | 資料型態 | 必填 | 說明 | 範例値 |
|---------|---------|------|------|--------|
| order_id | string | YES | 唯一訂單編號，格式：ORD-YYYYMM-{SEQ3} | ORD-202603-001 |
| customer_id | string | YES | FK Customers.customer_id | CUS-001 |
| event_date | date | YES | 活動日期 YYYY-MM-DD | 2026-04-15 |
| event_type | enum | YES | catering / takeaway / delivery | catering |
| venue | string | YES | 活動地點 | 台南市中西區 |
| total_amount | number | YES | 訂單總金額 TWD | 45000 |
| status | enum | YES | draft / confirmed / completed / cancelled | confirmed |
| client_type | enum | optional | marketing_co / family / takeaway / corporate | family |
| notes | string | optional | 業務備注 | 場地有電梯 |
| created_at | date | YES | YYYY-MM-DD | 2026-03-14 |
| updated_at | date | YES | YYYY-MM-DD | 2026-03-14 |

status 允許値：`draft` / `confirmed` / `completed` / `cancelled`

---

## TABLE 2 — Customers（客戶表）

**主鍵：** `customer_id`  
**用途：** 記錄每位客戶的基本資料與歷史訂單摘要。

| 欄位名稱 | 資料型態 | 必填 | 說明 | 範例値 |
|---------|---------|------|------|--------|
| customer_id | string | YES | 唯一客戶編號，格式：CUS-{SEQ3} | CUS-001 |
| name_zh | string | YES | 客戶姓名 | 陳小明 |
| phone | string | YES | 聯絡電話 | 0912-345-678 |
| email | string | optional | Email | chen@example.com |
| order_count | integer | optional | 歷史訂單總數（自動計算，勿手填） | 3 |
| first_order_date | date | optional | 第一筆訂單日期 YYYY-MM-DD | 2025-08-01 |
| last_order_date | date | optional | 最後一筆訂單日期 YYYY-MM-DD | 2026-03-01 |
| preferred_type | enum | optional | catering / takeaway / delivery | catering |
| notes | string | optional | 內部備注 | 習慣提前2個月預訂 |
| created_at | date | YES | YYYY-MM-DD | 2026-03-14 |
| updated_at | date | YES | YYYY-MM-DD | 2026-03-14 |

---

## TABLE 3 — Events（活動表）

**主鍵：** `event_id`  
**用途：** 記錄每場活動的詳細資訊，1筆訂單對1場活動。

| 欄位名稱 | 資料型態 | 必填 | 說明 | 範例値 |
|---------|---------|------|------|--------|
| event_id | string | YES | 唯一活動編號，格式：EVT-YYYYMM-{SEQ3} | EVT-202604-001 |
| order_id | string | YES | FK Orders.order_id | ORD-202603-001 |
| event_name | string | YES | 活動名稱 | 陳小明婚禮外熴 |
| event_date | date | YES | 活動日期 YYYY-MM-DD | 2026-04-15 |
| venue | string | YES | 地點 | 台南市中西區 |
| guest_count | integer | YES | 預估人數 | 80 |
| setup_time | string | optional | 備場時間 | 09:00 |
| service_start | string | optional | 服務開始時間 | 12:00 |
| difficulty_level | enum | optional | easy / medium / hard | medium |
| special_requirements | string | optional | 特殊需求 | 需要廩師現場備料 |
| notes | string | optional | 備注 | 戸外場地，需自備電源 |
| created_at | date | YES | YYYY-MM-DD | 2026-03-14 |

difficulty_level：`easy`（一般室內）/ `medium`（輕度困難）/ `hard`（搀運惡劣/溝通複雜/急單）

---

## TABLE 4 — Items（品項表）

**主鍵：** `item_id`  
**用途：** 所有可販售品項的主檔（對應 MasterData Sheets 的 1_ITEM_MASTER）。

| 欄位名稱 | 資料型態 | 必填 | 說明 | 範例値 |
|---------|---------|------|------|--------|
| item_id | string | YES | 唯一品項編號，格式：{TYPE}-{SUBTYPE}-{SEQ3} | DES-MAC-001 |
| item_name_zh | string | YES | 中文品項名稱 | 法式珫瑰馬卡龍 |
| item_name_en | string | optional | 英文名稱 | Rose Macaron |
| category | enum | YES | DES / SAV / DRK / EQP / PKG / SVC | DES |
| subcategory | string | optional | 次分類 | 法式甜點 |
| unit | enum | YES | 個/份/盤/桌/式/人份/組 | 個 |
| unit_price | number | YES | 標準售價 TWD | 65 |
| cost_per_unit | number | optional | 成本價（業務填，不對外） | 45 |
| min_qty | integer | optional | 最低訂購數量 | 12 |
| is_active | boolean | YES | TRUE / FALSE | TRUE |
| allergens | string | optional | 過敏原（逗號分隔） | 麵質,蛋 |
| notes | string | optional | 備注 | 需冷藏保存 |
| created_at | date | YES | YYYY-MM-DD | 2026-03-14 |
| updated_at | date | YES | YYYY-MM-DD | 2026-03-14 |

**category 對照表：**

| TYPE | 中文 | 範例 |
|------|------|------|
| DES | 甜點類 | 法式馬卡龍 |
| SAV | 鹹食類 | 義式香腸獵鳥盤 |
| DRK | 飲品類 | 無酒精氣泡飲 |
| EQP | 設備道具 | 6尺長桌 |
| PKG | 套餐包 | 婚禮外熴基本套 |
| SVC | 服務費用 | 場地佈置費 |

---

## 版本紀錄

| 版本 | 日期 | 說明 |
|------|------|------|
| v0.1 | 2026-03-14 | 初稿：4 張核心表定義，對應 A5 任務書 SECTION 3 |
