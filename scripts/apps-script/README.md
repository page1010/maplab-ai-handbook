# 報價系統 v2 — Apps Script 部署說明

**Phase 1：一鍵產出報價單**
版本：v1.0 | 建立：2026-04-01

---

## 檔案說明

| 檔案 | 用途 |
|------|------|
| `Code.gs` | 主程式：選單、createQuote()、條款、SALES_INTAKE 寫入 |
| `QuoteForm.html` | 彈出表單 UI（多欄位輸入） |

---

## 部署步驟

### 1. 開啟 Apps Script Editor

1. 打開目標 Google Sheet（ID：`1fn_woqYI_RY9ggGHVidB5SMygAzwe4CL_SOPLhe91Jg`）
2. 選單列：**擴充功能 → Apps Script**

### 2. 建立 Code.gs

1. 左側專案面板預設有一個 `Code.gs`
2. 清空內容，貼上 `scripts/apps-script/Code.gs` 的全部內容
3. 儲存（Ctrl+S / Cmd+S）

### 3. 建立 QuoteForm.html

1. 左側「+」→ **HTML 檔案**
2. 命名為 `QuoteForm`（不含副檔名，Apps Script 會自動加 `.html`）
3. 清空內容，貼上 `scripts/apps-script/QuoteForm.html` 的全部內容
4. 儲存

### 4. 第一次執行授權

1. 在 Editor 選擇函式 `onOpen`，按執行（▶）
2. 跳出授權視窗 → **審查權限** → 選帳號 → **允許**
3. 授權範圍包含：Spreadsheets、Drive

### 5. 確認選單出現

重新整理 Google Sheet，上方選單列應出現 **MAPLAB** 選單，內有「產出報價單」。

---

## 前置條件確認

| 項目 | 要求 |
|------|------|
| `QUOTE_WORKBENCH` 分頁 | 必須存在，為模板 |
| `SALES_INTAKE` 分頁 | 必須存在，表頭已建好 |
| `SALES_INTAKE` 欄位順序 | A:case_id B:created_at C:source D:client_name E:company F:phone G:event_type H:event_date I:location J:pax K:sheet_url L–N:（預留）O:notes |

---

## QUOTE_WORKBENCH 模板欄位對應

Apps Script 複製模板後會寫入以下欄位，請確認模板的 **B 欄** 為填入區：

| 儲存格 | 內容 |
|--------|------|
| B2 | 客戶名稱 |
| B3 | 公司名稱 |
| B4 | 聯絡電話 |
| B5 | 完整地址 |
| B6 | 活動類型 |
| B7 | 活動日期 |
| B8 | 預計人數 |
| B9 | 活動地點 |
| H1 | case_id |
| H2 | 建立時間 |
| E2 | 報價狀態（初始值：報價中） |
| E3 | 成交金額（業務填） |
| E4 | 匯款狀態（初始值：未匯） |
| E5 | 最後修改者（初始值：系統） |
| E6 | 版本號（初始值：v1） |
| A30 | 條款標題 |
| A31 | 條款內文（個人版 or 企業版，自動帶入） |

> ⚠️ 若模板欄位位置不同，請對照修改 `Code.gs` 中 `createQuote()` 的儲存格座標。

---

## 條款判斷邏輯

- 表單「公司名稱」**有填寫** → 帶入**企業版條款**（含條款編號 + 活動日期）
- 表單「公司名稱」**留空** → 帶入**個人版條款**（匯款帳號 + 取消規則）

條款原文來源：`data/quote-terms-reference.md`

---

## 產出結果

每次按「產出報價單」後：

1. 複製 `QUOTE_WORKBENCH` → 新分頁命名為 `報價_[客戶名]_[YYYYMMDD]`
2. 填入客戶資訊 + 條款 + 狀態區初始值
3. 確認 Drive 中 `MAPLAB_報價單/[年份]/` 資料夾存在（自動建立）
4. `SALES_INTAKE` 新增一行，含 case_id、客戶資訊、sheet 連結
5. 彈出視窗顯示案件編號 + 報價單連結

---

## 常見問題

**Q：執行時出現「找不到 QUOTE_WORKBENCH」**
A：確認分頁名稱完全一致（含全形半形）。

**Q：SALES_INTAKE 寫在錯誤欄位**
A：確認表頭順序符合上方欄位對應表，或修改 `Code.gs` 中 `writeToIntake_()` 的 row 陣列順序。

**Q：Drive 資料夾建立失敗**
A：此為非必要功能，不影響報價單產出。確認帳號有 Drive 寫入權限即可。
