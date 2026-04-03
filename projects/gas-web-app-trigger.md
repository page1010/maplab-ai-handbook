# Plan B — GAS Web App HTTP 觸發報價單產出

## 要做什麼（What）

將現有 Google Apps Script「MAPLAB 按鈕」邏輯包裝成 Web App，新增 `doPost(e)` 入口，讓任何 Agent 或 webhook 可透過 HTTP POST 觸發，自動產出獨立報價單 Spreadsheet。

目標結果：
1. A6 可以 `curl -X POST <WEBAPP_URL> -d '{"客戶名":"...", "品項":[...], "報價":...}'` 直接產出報價單
2. 回傳新報價單 URL + 報價單 ID
3. 自動寫入 SALES_INTAKE（成交追蹤 + 匯款追蹤欄位）
4. 不需要 Chrome、不需要 Owner 或 A0 手動按按鈕

## 為什麼需要（Why）

**現況痛點**：
- 現有「MAPLAB 按鈕」只能在 Google Sheets 介面手動點擊
- A6 接到詢價後，需要 Owner 召喚 A0（Cowork），A0 再打開 Chrome 點按鈕，流程三個人跑一個動作
- A1 Claude Code terminal 沒有 Chrome MCP，無法自己按按鈕

**目標**：A6 獨立完成「收詢價 → 計算報價 → 產出報價單 → 回傳連結」全流程，Owner 完全不介入。

## 使用者情境（User Scenario）

```
客人 Telegram / LINE 傳訊：
  「我們要辦 Tea Time，60 人，預算 10,000，想要有甜點有鹹食」

A6 自動處理：
  1. 根據 SOP 計算品項與份數（確保毛利率 ≥ 65%）
  2. 呼叫 GAS Web App URL（HTTP POST）
  3. GAS 自動建立獨立報價單 Spreadsheet → 存進 MAPLAB_報價單/2026/
  4. GAS 自動寫一行進 SALES_INTAKE（含客戶名、日期、金額、狀態）
  5. A6 回傳報價單連結給業務或客人

Owner 不需做任何事。
```

## 技術計畫

### 步驟
1. Owner 複製現有 Apps Script 原始碼給 A1
2. A1 在現有邏輯基礎上加 `doPost(e)` 函數
3. Owner 貼回 Apps Script + 部署成 Web App（Execute as: Me, Access: Anyone with link）
4. A1 拿到 Web App URL → 寫進 A6 技能書 `skills/a6-rapid-quote-sop.md`

### doPost 預期介面（草稿）
```javascript
function doPost(e) {
  const params = JSON.parse(e.postData.contents);
  // params: { 客戶名, 活動日期, 人數, 品項陣列, 報價, 車馬費, 備注 }
  const result = generateQuoteSheet(params);
  // result: { sheetUrl, sheetId, quoteNo }
  return ContentService.createTextOutput(JSON.stringify(result))
    .setMimeType(ContentService.MimeType.JSON);
}
```

## 目前阻擋點

需要 Owner 提供 Apps Script 原始碼（試算表 → 擴充功能 → Apps Script）。

## 狀態

- [ ] 取得 Apps Script 原始碼
- [ ] 撰寫 doPost() 版本
- [ ] Owner 部署 Web App
- [ ] 測試 curl 觸發
- [ ] 寫進 A6 技能書

最後更新：2026-04-03 A1
