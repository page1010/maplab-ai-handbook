# Google Sheets 資料清洗技能書
版本：v1.0 | 建立：2026-03-18 | 適用 Agent：A5 Master Data Agent
用途：系統化清洗 MAPLAB Kitchen ERP 中 Google Sheets 資料的工具、公式與 SOP

---

## SECTION 0 — 本技能書的目標讀者

你正在處理 MAPLAB Kitchen 的品項資料庫（Items sheet ~139 筆），以及相關的 OrderLines、QUOTE_DRAFT 等分頁。本文件提供一套實戰工具箱，讓資料清洗工作從「手動逐筆看」進化到「公式 + 腳本半自動化」。

**核心痛點（來自 A5 實戰經驗 v0.1–v1.5）：**
- 品名後綴不統一（_15份、_6L、括號格式混用）
- 重複品項辨識困難（同品不同名、同名不同 ID）
- Apps Script 批次迴圈無防重複 → 3041 行垃圾資料
- 欄位格式不一致（unit 欄位：份/個/盤/壺 混用）
- 缺少快速巡查機制（哪些行缺值、哪些行異常）

---

## SECTION 1 — 公式工具箱（純 Sheets，不需 Apps Script）

### 1.1 文字清洗公式

**TRIM + CLEAN — 移除多餘空白與不可見字元**
`=TRIM(CLEAN(A2))`
適用場景：品名前後有空格、從 PDF 複製貼上產生的隱藏字元。

**SUBSTITUTE — 批次取代指定字串**
`=SUBSTITUTE(A2, "_15份", "")`
適用場景：移除品名後綴（_15份、_20份、_30份）。
進階：多層巢狀移除
`=SUBSTITUTE(SUBSTITUTE(SUBSTITUTE(A2,"_15份",""),"_20份",""),"_30份","")`

**REGEXREPLACE — 正則表達式清洗（Google Sheets 獨有）**
`=REGEXREPLACE(A2, "_\d+份$", "")`
適用場景：一次移除所有「_數字+份」後綴，不需逐一列舉。
更多範例：
- 移除容量後綴：`=REGEXREPLACE(A2, "[_\(]\d+L[\)壺裝]*$", "")`
- 只保留中文品名：`=REGEXREPLACE(A2, "[a-zA-Z0-9_\-]", "")`

**PROPER / UPPER / LOWER — 英文名稱標準化**
`=PROPER(B2)` → Rose Macaron（首字母大寫）

### 1.2 重複偵測公式

**COUNTIF — 計算重複次數**
`=COUNTIF(C:C, C2)`
在輔助欄顯示該品名出現幾次，>1 即為重複候選。

**UNIQUE — 一鍵取得不重複清單**
`=UNIQUE(C2:C500)`
放在新分頁，快速產生去重品名清單，與原表比對。

**條件式格式 — 視覺化標記重複**
選取 C 欄 → 格式 → 條件式格式設定 → 自訂公式：
`=COUNTIF(C:C, C2) > 1`
背景色設為黃色 → 所有重複品名自動高亮。

### 1.3 資料驗證工具

**下拉選單 — 限制欄位輸入值**
選取 category 欄 → 資料 → 資料驗證 → 從清單中選取：
`DES, SAV, DRK, EQP, PKG, SVC`
確保新增品項不會出現打字錯誤的分類。

**VLOOKUP — 跨表格關聯查詢**
`=VLOOKUP(B5, Items!C:E, 3, FALSE)`
適用場景：QUOTE_DRAFT 選品項後自動帶出成本。
注意：VLOOKUP 只往右查，如果需要往左查用 INDEX+MATCH。

**INDEX + MATCH — 更靈活的跨表查詢**
`=INDEX(Items!E:E, MATCH(B5, Items!C:C, 0))`
適用場景：不受欄位順序限制的查詢。

### 1.4 快速巡查公式

**空值計數**
`=COUNTBLANK(D2:D500)` → 快速知道 default_price 有多少空格。

**非標準值偵測**
`=IF(NOT(REGEXMATCH(A2, "^(DES|SAV|DRK|EQP|PKG|SVC)-[A-Z]{3}-\d{3}$")), "⚠️ 格式異常", "✅")`
放在輔助欄，自動偵測 item_id 格式是否符合 {TYPE}-{SUBTYPE}-{SEQ3}。

**日期格式檢查**
`=IF(ISNUMBER(M2), IF(AND(M2>DATE(2024,1,1), M2<DATE(2027,1,1)), "✅", "⚠️ 日期異常"), "⚠️ 非日期")`

---

## SECTION 2 — Apps Script 自動化工具

### 2.1 批次清洗腳本（安全版）

```javascript
/**
 * 批次清洗 Items 品名後綴
 * 使用方式：擴充功能 > Apps Script > 貼上 > 執行
 * 安全機制：先預覽變更，確認後才寫入
 */
function cleanItemNames() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName('Items');
  const range = sheet.getRange('C2:C' + sheet.getLastRow());
  const values = range.getValues();
  
  const patterns = [
    /_\d+份$/,      // _15份, _20份
    /_\d+L$/,       // _6L, _8L
    /\(\d+L壺裝\)$/, // (8L壺裝)
    /_\d+$/         // _1000
  ];
  
  let changes = [];
  values.forEach((row, i) => {
    let original = row[0];
    let cleaned = original;
    patterns.forEach(p => { cleaned = cleaned.replace(p, ''); });
    cleaned = cleaned.trim();
    if (cleaned !== original) {
      changes.push({ row: i + 2, from: original, to: cleaned });
    }
  });
  
  // 預覽模式：先 log 變更，不寫入
  Logger.log('預計變更 ' + changes.length + ' 筆：');
  changes.forEach(c => Logger.log('Row ' + c.row + ': ' + c.from + ' → ' + c.to));
  
  // 確認後取消註解下方程式碼執行寫入
  // changes.forEach(c => sheet.getRange('C' + c.row).setValue(c.to));
  // Logger.log('✅ 已寫入 ' + changes.length + ' 筆變更');
}
```

### 2.2 重複偵測與標記腳本

```javascript
/**
 * 偵測 Items 品名重複並在 I 欄標記
 * I 欄 = Y 表示建議刪除（保留最小 item_id）
 */
function detectDuplicates() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName('Items');
  const data = sheet.getRange('A2:C' + sheet.getLastRow()).getValues();
  
  const nameMap = {};
  data.forEach((row, i) => {
    const name = row[2]; // C欄 standard_name
    if (!nameMap[name]) nameMap[name] = [];
    nameMap[name].push({ row: i + 2, id: row[0] });
  });
  
  let dupCount = 0;
  Object.values(nameMap).forEach(group => {
    if (group.length > 1) {
      // 保留最小 item_id，其餘標記 Y
      group.sort((a, b) => a.id.localeCompare(b.id));
      for (let k = 1; k < group.length; k++) {
        sheet.getRange('I' + group[k].row).setValue('Y');
        dupCount++;
      }
    }
  });
  
  Logger.log('標記 ' + dupCount + ' 筆重複品項為 Y');
}
```

### 2.3 防重複匯入機制（修復 v0.5 問題）

```javascript
/**
 * 匯入前檢查 order_id 是否已存在
 * 防止 ORD-2025-001 重複匯入 10 次的問題
 */
function importOrderSafely(orderId, orderData) {
  const sheet = SpreadsheetApp.getActiveSpreadsheet()
    .getSheetByName('OrderLines');
  const existingIds = sheet.getRange('A2:A' + sheet.getLastRow())
    .getValues().flat();
  
  if (existingIds.includes(orderId)) {
    Logger.log('⚠️ ' + orderId + ' 已存在，跳過匯入');
    return false;
  }
  
  // 安全匯入...
  return true;
}
```

### 2.4 批次操作最佳實踐

**規則 1：永遠用 getValues() / setValues() 批次讀寫**
錯誤做法：逐格 `getRange('A'+i).getValue()` → 每格一次 API 呼叫，300 筆要 300 次
正確做法：`getRange('A2:A301').getValues()` → 一次讀取全部

**規則 2：超時保護（30 秒上限）**
```javascript
const startTime = Date.now();
for (let i = 0; i < rows.length; i++) {
  if (Date.now() - startTime > 25000) { // 25秒安全邊界
    Logger.log('⏰ 超時保護觸發，已處理 ' + i + '/' + rows.length);
    break;
  }
  // 處理邏輯...
}
```

**規則 3：寫入前先備份**
```javascript
function backupSheet(sheetName) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const source = ss.getSheetByName(sheetName);
  const backup = source.copyTo(ss);
  backup.setName(sheetName + '_backup_' + 
    Utilities.formatDate(new Date(), 'Asia/Taipei', 'yyyyMMdd_HHmm'));
}
```

---

## SECTION 3 — 資料清洗 SOP（A5 標準作業流程）

### 3.1 新品項新增 SOP

1. 確認 item_id 格式：{TYPE}-{SUBTYPE}-{SEQ3}
2. 在 Items 最後一行新增（確認 row 位置，避免覆蓋）
3. 必填欄位檢查：item_id、standard_name、category、unit、is_active
4. 執行 COUNTIF 確認品名不重複
5. 如需下拉選單，確認資料驗證範圍已包含新行

### 3.2 重複品項清洗 SOP

1. 執行 `detectDuplicates()` 或在輔助欄加 COUNTIF
2. 檢查高亮行，判斷是否為真正重複（品名相同≠品項相同）
3. 每組重複保留最小 item_id
4. I 欄標記為 N（待刪除）或 Y（保留）
5. 排序後批次刪除 I=N 的行
6. 更新 Items 總數紀錄

### 3.3 資料一致性巡查 SOP

每次 session 結束前執行：
1. `=COUNTBLANK(D2:D500)` — 檢查 default_price 空值數
2. `=COUNTBLANK(E2:E500)` — 檢查 default_cost 空值數
3. 條件式格式確認無重複品名
4. item_id 格式驗證輔助欄無 ⚠️

---

## SECTION 4 — MAPLAB 特定情境解決方案

### 4.1 OrderLines 重建策略（R6 任務用）

問題：2025 訂單 Apps Script 匯入失敗，品名欄位只有分類標籤。
解法：
1. 從 TimeTree 密集日清單找到目標週
2. 開啟對應 Google Sheet 的「本週訂單」分頁
3. 手動比對 Items.standard_name 找到匹配品項
4. 使用 `importOrderSafely()` 防重複匯入
5. 用 VLOOKUP 自動帶入 item_id

### 4.2 QUOTE_DRAFT 報價單維護

現有結構：
- B 欄：下拉選單（來源 Items!C2:C500）
- C 欄：VLOOKUP 自動帶出 default_cost
- C25：SUMIF 加總成本

增強建議（任務 B）：
- D 欄：數量（手動輸入）
- E 欄：小計 `=IF(C5="","",C5*D5)`
- 飲品行加 F 欄：volume（來源 Items!K:K 的 VLOOKUP）
- G 欄：備註（保冰桶/招待等）

### 4.3 甜點去重決策框架（任務 A）

DST 類品項最易重複的原因：
- 口味變體多（玫瑰馬卡龍 vs 檸檬馬卡龍 → 不同品項）
- 份數變體（馬卡龍塔_15份 vs 馬卡龍塔_20份 → 同品項不同規格）
- 命名不一致（手工馬卡龍 vs 法式馬卡龍 → 需人工判斷）

判斷規則：
- 核心食材 + 型態相同 → 合併（保留最小 ID）
- 口味不同 → 保留為獨立品項
- 份數不同 → 合併（數量在 OrderLines 處理）

---

## SECTION 5 — 工具版本與參考

| 工具 | 版本 | 說明 |
|------|------|------|
| Google Sheets | Web | 核心平台，免費 |
| Apps Script | V8 Runtime | 內建腳本引擎 |
| REGEXREPLACE | Sheets 內建 | Google Sheets 獨有的正則函數 |
| VLOOKUP / INDEX+MATCH | Sheets 內建 | 跨表查詢標準工具 |
| 條件式格式設定 | Sheets 內建 | 視覺化資料品質巡查 |
| 資料驗證（下拉選單）| Sheets 內建 | 限制輸入值防止錯誤 |

**外部資源：**
- Google Apps Script Best Practices: https://developers.google.com/apps-script/guides/support/best-practices
- Google Sheets 函數清單: https://support.google.com/docs/table/25273

---

*版本：v1.0 | 維護者：A1 Handbook Agent | 適用 Agent：A5 Master Data*
