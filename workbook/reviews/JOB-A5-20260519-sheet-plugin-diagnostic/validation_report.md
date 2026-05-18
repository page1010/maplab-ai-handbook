# A5 Sheet 外掛報價路徑診斷 — 2026-05-19

## 結論

目前原本 Sheet 外掛路徑可以做到「複製 QUOTE_DRAFT 產生一份報價單 copy」，但不能可靠做到「直接產出 A/B/C 三份完整報價單」。

我沒有部署修復到 live GAS，原因是壞點牽涉到模板欄位、SALES_INTAKE 欄位、A6 觸發合約與菜單 payload，直接 push 會影響所有後續報價。

## 已讀關係與影響

- `workbook/task_modules/role_module_relation_graph.json`
- `docs/openclaw/relation-graph.md`
- `docs/a4/source-of-truth.md`
- `docs/a4/drive-map.md`
- `docs/a4/workflow.md`
- `projects/maplab-master-data.md`
- `projects/quote-system-v2.md`
- `docs/business-requirements/quote-pricing-logic.md`
- `handoff/feedback/2026-04-02-quote-draft-v3-layout.md`
- `docs/business-requirements/quote-sheet-print-range.md`

影響範圍：
- A5: Google Sheets master data / quote generation
- A6: Telegram quote workflow / proposal materials
- A7: customer answer rules
- A4: proposal asset dependency, not blocker for this Sheet bug

## 壞點

### 1. `createQuote()` 只產空殼，不吃 A/B/C 菜單明細

檔案：`scripts/apps-script/Code.gs`

現況：
- `createQuote(formData)` 只接客戶、日期、地址、人數等基本欄位。
- 它會 `makeCopy()` 整份主試算表，保留 `QUOTE_DRAFT` + `Items`，改名成 `報價單`。
- 它沒有接受 `menuItems`、`foodRevenue`、`finalTotal`、`addons`、`margin` 等 payload。

結果：
- 不能用同一個 API 一次產 A/B/C 三份完整方案。
- 若主 `QUOTE_DRAFT` 上殘留某個舊案內容，copy 會帶著那份舊案內容，不是 A/B/C。

### 2. `SALES_INTAKE` 欄位順序與 `writeToIntake_()` 不一致

Live header：

```text
A case_id
B created_at
C source
D client_name
E client_phone
F event_type
G event_date
H pax
I budget
J location
K raw_request
L status
M assigned_to
N a6_output_link
O notes
```

`writeToIntake_()` 目前假設：

```text
D client_name
E company
F phone
G event_type
H event_date
I location
J pax
K sheet_url
L quote_status
M payment_status
```

結果：
- 產出的 row 會欄位錯位。
- 例如有 phone 時會落到 `event_type` 欄。
- 報價單 URL 目前落在 `raw_request` 欄。
- M 欄 header 是 `assigned_to`，但實際被當付款狀態用。

### 3. A6/GAS 觸發合約只能觸發單張報價，不支援三版批次

檔案：
- `bot_a6/bot_a6.py`
- `scripts/apps-script/ApiEndpoint.gs`

現況：
- A6 只會 POST `{action:"createQuote", ...formData}`。
- `ApiEndpoint.gs` 只有 `createQuote` / `createSlide` / `addItem`。
- 沒有 `createQuoteVariants` 或 `createQuoteBatch`。

結果：
- Telegram / A6 不能把 A/B/C 三版 structured payload 傳給 Sheet 外掛。

### 4. 曾經存在的自動選品/寫品項邏輯已被移除，不能直接復活

歷史：
- v3.2-v3.7 有 `selectItemsForBudget_()` / `writeItemsToQuote_()`。
- 2026-04-04 曾發生公式/下拉被覆蓋事件。
- 後續 v3.8 移除品項寫入，回到保守 copy 模式。

結論：
- 不能直接把舊函數貼回去。
- 若要修，應新增只寫「產出的副本」的安全 helper，不寫 master `QUOTE_DRAFT`。

## 建議修復方式

### Phase 1: 安全修 `SALES_INTAKE` 對齊

- 修 `writeToIntake_()` 依 live header 寫入。
- 不改公式。
- 不改 `QUOTE_DRAFT`。
- 保持 URL 寫 K 欄，但同時把 L/M header 對齊為 `quote_status` / `payment_status`，或新增明確欄位。

### Phase 2: 新增 `createQuoteVariants`

新增 endpoint：

```json
{
  "action": "createQuoteVariants",
  "base": {
    "clientName": "奧利斯活動公司-吉笠",
    "eventDate": "2026-11-14",
    "eventType": "企業家庭日晚宴 Party",
    "location": "台南尖山埤度假村戶外主舞台",
    "pax": 200
  },
  "variants": [
    {
      "code": "A",
      "title": "小點補給版",
      "foodRevenue": 60000,
      "totalRevenue": 148000,
      "menuItems": [...]
    }
  ]
}
```

安全原則：
- 先 call `createQuote()` 產生副本。
- 只打開副本 `報價單` sheet 寫 D/F/E/I/J 等欄位。
- 不寫 master `QUOTE_DRAFT`。
- 不清 master data validation。
- 不改 master 公式。

### Phase 3: 副本驗證後才接 A6/Telegram

- 先用測試 payload 產 1 份副本。
- 檢查副本三件事：客戶可見區、內部成本/毛利、SALES_INTAKE row。
- 通過後再一次產 A/B/C 三份。
- 最後才讓 Telegram 顯示三份報價單連結。

## 目前不建議做的事

- 不建議直接用 `fromMaster`，因為需要先改 master `QUOTE_DRAFT`，和 Owner 剛剛的限制衝突。
- 不建議用舊 `writeItemsToQuote_()` 直接復活，歷史上它造成過公式/驗證受損。
- 不建議直接改 live master 欄位公式。
