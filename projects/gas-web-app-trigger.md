# Plan B — GAS Web App HTTP 觸發報價單產出

> ⚠️ **【結論已撤銷 — 2026-04-07】**
> 本文件記錄的 GAS Web App URL（v12）是被誤用的 LINE 對話 GAS 專案部署（Script ID: 1Fkl34P7p395k0YzwY8hyhz7DAAsgA3CBgyumx9ImSOFoXu771lFABSi7）。
> createQuote + createSlides 路由在 2026-04-04 因 .clasp.json 指錯被推送到 LINE 專案，屬於幻覺需求。
> **正確 Slide 邏輯在報價系統 GAS 專案的 `generateProposal_v2.gs`（Script ID: 1JIiPW_OUwNzB4VHS4k0KHi7LYDdPlFgHWejotsY4KE3KdLTc3EB-0vpc）。**
> 本文件保留作歷史紀錄，不可依據此計畫繼續執行。

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

## Web App 資訊（v12，已上線）

- **URL**：`https://script.google.com/macros/s/AKfycbyMvc3-gl1sI_9prPjzp0zg0N353f9fL5jzR-9wm_xYPZ8A8IsTJSoTjbmDefYFI0o/exec`
- **部署版本**：v12（Execute as: Me, Access: Anyone）
- **舊部署**：v1 已封存，v11 待封存

## curl 呼叫範例

```bash
curl -L \
  -H "Content-Type: application/json" \
  -d '{"action":"createQuote","clientName":"客戶名","eventType":"私廚餐會","eventDate":"2026-04-10","pax":"8","phone":"0912345678"}' \
  "https://script.google.com/macros/s/AKfycbyMvc3-gl1sI_9prPjzp0zg0N353f9fL5jzR-9wm_xYPZ8A8IsTJSoTjbmDefYFI0o/exec"
```

⚠️ **重要踩坑**：不要加 `-X POST`。curl 加了 `-X POST` 後，302 redirect 會打到 `/macros/echo` 並返回 405 Method Not Allowed。只用 `-d` 讓 curl 自動設為 POST，302 後自動轉 GET 取回結果。

## 測試結果

✅ 成功（報價單 ID：Q20260403222140）

## 狀態

- [x] 取得 Apps Script 原始碼
- [x] 撰寫 doPost() 版本
- [x] Owner 部署 Web App
- [x] 測試 curl 觸發
- [x] 寫進 A6 技能書（skills/a6-rapid-quote-sop.md SECTION 8）

最後更新：2026-04-03 A0（doPost v12 上線完成）
