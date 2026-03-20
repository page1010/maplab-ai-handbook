# MAPLAB Kitchen ERP — Field Naming Rules

版本：v0.1 | 建立：2026-03-15 | 負責：A5 Master Data Agent

---

## 基本原則

- 所有欄位名稱使用 **snake_case**（小寫 + 底線隔開）
- 不使用 camelCase、PascalCase、kebab-case
- 不在欄位名稱中使用中文
- 不使用縮寫（除非已列入標準縮寫表）

---

## ID 欄位命名規則

| 表名 | 主鍵格式 | 範例 |
|------|----------|------|
| Customers | CUS-{SEQ3} | CUS-001 |
| Orders | ORD-YYYYMM-{SEQ3} | ORD-202603-001 |
| Events | EVT-YYYYMM-{SEQ3} | EVT-202604-001 |
| Items | {TYPE}-{SUBTYPE}-{SEQ3} | DES-MAC-001 |

**{SEQ3} 說明：** 3位數字流水號，從 001 開始、不跨表共用

**Items TYPE 對照：**

| TYPE | 中文 | SUBTYPE 範例 |
|------|------|----------|
| DES | 甜點類 | MAC (馬卡龍), CKE (蘏活), PIE (派) |
| SAV | 鹹食類 | APZ (開胃輕食), PLT (盤香) |
| DRK | 飲品類 | NCA (無酒精), ALC (含酒精) |
| EQP | 設備道具 | TBL (桌子), CHR (椅子) |
| PKG | 套餐包 | WED (婚禮), CRP (企業) |
| SVC | 服務費用 | DEC (佈置), TRN (運輸) |

---

## 日期欄位規則

| 格式 | 用途 | 範例 |
|------|------|------|
| YYYY-MM-DD | 日期欄位（date type） | 2026-03-15 |
| HH:MM | 時間欄位（string type） | 09:00 |
| YYYYMM | ID 中的年月字就（如 order_id） | 202603 |

- created_at / updated_at 必填，不得空白
- 所有日期一律用 YYYY-MM-DD，不用 MM/DD/YYYY 或其他格式

---

## 常用欄位名稱標準化

| 用途 | 標準名稱 | 說明 |
|------|----------|------|
| 主鍵 | {table_singular}_id | 如 order_id, customer_id |
| 外鍵 | {referenced_table_singular}_id | 如 customer_id 在 Orders 表 |
| 狀態欄位 | status | 必填 enum 型態 |
| 是否啟用 | is_active | boolean，TRUE/FALSE |
| 計算欄位 | {noun}_count / {noun}_total | 如 order_count, line_total |
| 金額欄位 | {scope}_amount / {scope}_price | 如 total_amount, unit_price |
| 備注 | notes | 內部備注，不對外顯示 |
| 建立日 | created_at | 必填 |
| 更新日 | updated_at | 必填 |

---

## Enum 允許値規後

| 欄位名 | 允許値（全小寫 + 底線） |
|------|----------|
| status (Orders) | draft / confirmed / completed / cancelled |
| event_type | catering / takeaway / delivery |
| client_type | marketing_co / family / takeaway / corporate |
| difficulty_level | easy / medium / hard |
| category (Items) | DES / SAV / DRK / EQP / PKG / SVC |
| unit | 個 / 份 / 盤 / 桌 / 式 / 人份 / 組 |
| is_active | TRUE / FALSE |

**規則：** Enum 値一旦定義就不得任意新增，需經 A1 回寫 CHANGELOG 才能修改。

---

## 錠就禁止

- 不得用名稱做關聯鍵（应該用 id）
- 不得手填 order_count / line_total 等自動計算欄位
- 不得自行初巧新的 enum 値（需確認後更新表）
- 不得將成本價（cost_per_unit）對外揭露或寫入公開文件

---

## 版本紀錄

| 版本 | 日期 | 說明 |
|------|------|------|
| v0.1 | 2026-03-15 | 初稿：ID 格式 / 日期格式 / Enum 規後 / 禁止事項 |
