# 報價系統 v2 — 一鍵產出 + 狀態追蹤 + 營收分析
版本：v1.0 | 建立：2026-03-31 | 維護者：A0 Cowork
狀態：規格確認中

---

## SECTION 0 — 核心目標

把報價從「改模板」變成「一鍵產出獨立報價單」。
每筆報價自帶狀態追蹤和匯款追蹤。
3 個月後系統自動產出營收報告。

---

## SECTION 1 — 架構概覽

```
[業務按「產出報價單」] → [Apps Script 複製模板]
    → [新 Sheet：報價_客戶名_日期]
    → [存到 Drive 指定資料夾]
    → [SALES_INTAKE 新增一行 + 連結]
    → [DASHBOARD 計數器 +1]

[業務/A6 在新 Sheet 上改報價] → [每日 diff 腳本偵測變更]
    → [REVISION_LOG 自動記錄]

[成交後] → [業務改狀態為「已成交」+ 填成交金額]
    → [匯款追蹤：訂金/尾款/已結清]
    → [歸入歷史資料庫]

[每季] → [自動產出季度報告]
```

---

## SECTION 2 — 報價單產出流程

### 2.1 觸發方式
Apps Script UI 按鈕，放在 MAPLAB_外燴系統 Sheet 的選單列。

### 2.2 產出流程
1. 業務點按鈕 → 彈出表單（客戶名、活動類型、日期）
2. Apps Script 複製 QUOTE_WORKBENCH 模板 → 建新 Sheet
3. 新 Sheet 命名：`報價_[客戶名]_[YYYYMMDD]`
4. 自動填入客戶資訊到新 Sheet 的客戶區
5. 條款自動帶入（個人版 or 企業版，根據是否有公司名）
6. 新 Sheet 存到 Google Drive 資料夾：`MAPLAB_報價單/[年份]/`
7. SALES_INTAKE 新增一行：case_id + 客戶名 + Sheet 連結
8. DASHBOARD 報價計數器 +1

### 2.3 新 Sheet 結構
- **客戶資訊區**：名稱、電話、地址、活動類型、日期、人數
- **品項區**：從 Items 主表拉品項（A6 可改）
- **費用區**：餐點小計、服務費、車馬費、長桌、搬運費
- **條款區**：個人版/企業版（自動帶入，業務可改）
- **狀態區**（新增）：
  - 報價狀態：報價中 / 已成交 / 未成交 / 外帶自取
  - 成交金額：最終確認金額（可能跟報價金額不同）
  - 匯款狀態：未匯 / 已匯訂金 / 已匯尾款 / 已結清
  - 最後修改者：Owner / 業務 / A6 / 系統
  - 版本號：自動遞增

---

## SECTION 3 — 狀態追蹤

### 3.1 報價狀態流
```
新建 → 報價中 → 已成交 / 未成交 / 外帶自取
                    ↓
              填成交金額
                    ↓
              匯款追蹤開始
```

### 3.2 匯款追蹤
- 未匯 → 已匯訂金（金額 + 日期 + 後五碼）→ 已匯尾款 → 已結清
- 每次匯款狀態變更寫入 SALES_INTAKE 和對應 Sheet

### 3.3 REVISION_LOG 自動偵測
- Python diff 腳本每日 crontab 執行
- 比對每個行進中報價單的快照 vs 當前版本
- 自動填：section / original_value / revised_value / change_type
- 業務只需補：reason_tag（下拉，5 秒）

### 3.4 版本控制
- 新 Sheet 內有 version 欄，每次偵測到變更自動 +1
- REVISION_LOG 記錄每個版本的差異
- 「最後修改者」欄讓系統知道是誰改的（Owner / 業務 / A6）

---

## SECTION 4 — 數據分析（Phase 4，系統跑 3 個月後）

### 4.1 需要的資料來源

| 資料 | 來源 | 自動 or 手動 |
|------|------|-------------|
| 成交金額 | 報價系統 v2 狀態區 | 業務填（1 欄） |
| 成交狀態 | 報價系統 v2 狀態欄 | 業務選（下拉） |
| 匯款紀錄 | 報價系統 v2 匯款區 | 業務填（匯款後） |
| 品項明細 | 報價系統 v2 品項區 | 自動（從模板複製） |
| 活動類型 | SALES_INTAKE event_type | 自動（產出時填） |
| 日期 | SALES_INTAKE event_date | 自動 |
| 地區 | SALES_INTAKE location | 自動 |
| 歷史營收 | 銀行 CSV 匯入 | 一次性手動 |

### 4.2 季度報告自動產出

| 指標 | 計算方式 |
|------|---------|
| 本季報價單數量 | COUNT(SALES_INTAKE 本季) |
| 成交率 | 已成交 / 總報價 |
| 未成交原因分布 | REVISION_LOG + 人工標記 |
| 活動類型 × 營收 | 成交金額 GROUP BY event_type |
| 品項熱度排行 | 品項區 COUNT 排序 |
| 地區分布 | location GROUP BY |
| 平均報價金額 | AVG(成交金額) |
| 平均成交天數 | 成交日 - 報價日 |
| 下季度建議 | 基於趨勢自動生成 |

### 4.3 營收時間軸

```
報價日 → 成交日 → 訂金收款日 → 活動日 → 尾款收款日
```

「營收」以「收款日」為準（訂金 + 尾款都收到才算已結清）。
「應收帳款」= 已成交但未結清的金額。

---

## SECTION 5 — 客戶名冊

### 5.1 資料結構

| 欄位 | 來源 |
|------|------|
| client_name | SALES_INTAKE / 報價單 |
| phone | 報價單客戶區 |
| company | 報價單（有公司名 = 企業客戶） |
| event_type | SALES_INTAKE |
| event_date | SALES_INTAKE |
| location | SALES_INTAKE |
| pax | 報價單 |
| total_orders | COUNT(同一客戶的歷史報價) |
| total_revenue | SUM(同一客戶的成交金額) |
| is_corporate | 有 company = true |
| last_order_date | MAX(event_date) |

### 5.2 回購客判斷
- 同一 phone 或 client_name 出現 ≥ 2 次 = 回購客
- 回購客自動觸發 T-A5-003 熱客招待

---

## SECTION 6 — 實作步驟

### Phase 1（Week 1）— Apps Script 按鈕 + 產出流程
- [ ] 寫 Apps Script：產出報價單按鈕
- [ ] 測試：模板複製 + 命名 + 存 Drive + 寫 SALES_INTAKE
- [ ] 建 Drive 資料夾：MAPLAB_報價單/2026/

### Phase 2（Week 2）— diff 腳本 + REVISION_LOG
- [ ] 寫 scripts/diff-quote-revisions.py
- [ ] 建快照資料夾：data/quote_workbench_snapshots/
- [ ] crontab 每日執行
- [ ] 測試：改一筆報價 → 自動偵測 → 寫入 REVISION_LOG

### Phase 3（Week 3-4）— 匯款追蹤 + 客戶名冊
- [ ] 新 Sheet 加狀態區欄位（狀態/成交金額/匯款/修改者/版本）
- [ ] 寫 scripts/build-client-roster.py（從歷史報價建客戶名冊）
- [ ] 客戶名冊寫入 Sheet 新分頁 CLIENT_ROSTER

### Phase 4（Month 3+）— 季度報告
- [ ] 寫 scripts/quarterly-report.py
- [ ] 季報自動產出到 data/reports/
- [ ] 寫入 DASHBOARD 季度摘要區

---

## SECTION 7 — 與現有系統銜接

| 現有組件 | 銜接方式 |
|---------|---------|
| QUOTE_DRAFT | 作為模板，不再直接在上面改 |
| SALES_INTAKE | 每筆報價自動新增一行 |
| REVISION_LOG | diff 腳本自動填 |
| CONVERSATION_LOG | LINE webhook 對話 + A6 協作對話 |
| Items 主表 | 品項來源（E 欄 default_cost） |
| DASHBOARD | 自動更新計數器 + 季度摘要 |
| A6 skill | 讀 SALES_INTAKE 連結找到對應報價單 |
| 客戶名冊 | 回購客判斷 → 熱客招待 |
| T-A5-003 | 熱客招待自動觸發 |

---

## 版本紀錄

| 版本 | 日期 | 說明 | 更新者 |
|------|------|------|--------|
| v1.0 | 2026-03-31 | 初版規格（一鍵產出 + 狀態追蹤 + 營收分析） | A0 Cowork |

---

*Owner 確認規格後開始 Phase 1。*
