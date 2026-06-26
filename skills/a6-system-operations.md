# A6 系統操作手冊 — MAPLAB 報價系統

> **讀者**：A6（你）。你是 Mina 的報價加速器。這份手冊告訴你系統怎麼用。
> **目標**：Mina 說一句話，你 3 秒產出 100 分報價單 + Slide 提案。
> **前提**：你會透過 Claude Code 或 MCP 工具操作 Google Sheets API + Google Apps Script。

---

## 1. 系統架構總覽

### 1.1 主試算表

**Spreadsheet ID**：`1fn_woqYI_RY9ggGHVidB5SMygAzwe4CL_SOPLhe91Jg`
**名稱**：MAPLAB_外燴系統_v0.1

**你會用到的分頁**：

| 分頁 | 用途 | 你的操作 |
|------|------|---------|
| `QUOTE_DRAFT` | 報價單模板（master copy） | **不直接改** — createQuote 會 makeCopy |
| `Items` | 品項主表（108+ 品項 + 成本） | **讀取**查品項、成本、圖片 URL |
| `SALES_INTAKE` | 進件紀錄（每個案件一行） | **寫入**新案件 / **讀取**查歷史 |
| `REVISION_LOG` | 修改紀錄 | 未來寫入（目前手動） |
| `CONVERSATION_LOG` | LINE + Telegram 對話紀錄 | 讀取（LINE webhook 自動寫入） |

### 1.2 Apps Script 模組

| 檔案 | 功能 | 你會呼叫的函式 |
|------|------|---------------|
| `Code.gs` | 報價單產出核心 | `createQuote(formData)` |
| `generateProposal_v2.gs` | Slide 提案產出 | `generateProposalV2()` |
| `contractTerms.gs` | 合約條款 v4.0 | `resolveContractVersion(formData)` / `getContractTermsV4(version, eventDate, depositAmount)` |
| `quoteHelpers.gs` | 車馬費 + 搬運費計算 | `calcTransportFee(address)` / `calcFloorFee(mode)` |

### 1.3 關鍵 Drive 資料夾

| 資料夾 | 用途 |
|--------|------|
| `MAPLAB_報價單/{year}/` | 每年的報價單 copy 存放處（createQuote 自動建） |
| `1uGBCSTLFRVm5ZPh6v10G-tImf2QB5deu` | Slide 提案存放處（generateProposalV2 自動建） |

---

## 2. 操作路徑 A：產出報價單

### 2.1 你收到什麼

Mina 在 Telegram 跟你說類似：

> 報價 李晴宜 週歲 20人 15000含服務費 12/21 上午11點 台南安南區安和路三段190巷 室內 不要羊 部分長輩不吃牛 輕食A

### 2.2 你要做什麼（step by step）

**Step 1：解析 Mina 的指令 → 組成 formData 物件**

```javascript
var formData = {
  customer: '李晴宜',            // 客戶名
  date: '2026-12-21',            // 活動日期 YYYY-MM-DD
  time: '11:00',                 // 活動時間
  address: '台南市安南區安和路三段190巷71弄17號',  // 完整地址
  eventType: '生日派對',         // 活動類型（對應 QuoteForm 下拉選項）
  headcount: '20',               // 人數
  eventName: '週歲抓周',         // 活動名稱
  totalItems: '',                // 留空（系統不用這個，品項你自己填）
  depositAmount: '3000',         // 訂金（個人 baseline 3000）
  dietaryNotes: '不要羊 部分長輩不吃牛 串燒可以',  // 飲食禁忌
  floorFeeMode: 'none',         // 樓層搬運：none / with_help / no_help
  noDeposit: false,             // 不收訂金例外（個人永遠 false）
  isMarketingAgency: false      // 行銷公關（個人永遠 false）
};
```

**QuoteForm 活動類型下拉對應**：
生日派對 / 企業聚會 / 婚禮 / 外燴到府 / 尾牙/春酒 / 節日聚餐 / 其他

**Step 2：呼叫 createQuote**

```javascript
var result = createQuote(formData);
// result = { success: true, caseId: 'Q20261221110000', fileName: '20261221_李晴宜', url: 'https://docs.google.com/...' }
```

**createQuote 做了什麼（你不用管，但要知道）**：
1. 開主試算表 → 產生 caseId（Q + 時間戳）
2. makeCopy 複製整個 Spreadsheet → 存到 Drive `MAPLAB_報價單/2026/`
3. 刪掉 copy 裡 QUOTE_DRAFT 和 Items 以外的分頁
4. 改名 QUOTE_DRAFT → 報價單
5. 寫入客戶資料到 D2/F2/D3/F3/D4/F4/D5/F5（框線內值欄）
6. 寫入系統資訊到 H1/H2（caseId/時間）和 M/N 欄
7. 設定 N5 報價狀態下拉 / N7 付款狀態下拉
8. 隱藏 row 17-19（熱客招待區）
9. 還原 E25 租借長桌公式
10. 自動算車馬費（Maps API）→ 寫 E27 + L11/L12 備註
11. 自動算搬運費 → 寫 E28 + L13 備註
12. 帶入合約條款（contractTerms.gs）→ 寫 C32/C33
13. 寫 K10/L10 飲食禁忌
14. 在 SALES_INTAKE 新增一行（writeToIntake_）含 IMPORTRANGE 動態連結
15. 回傳 { success, caseId, fileName, url }

**Step 3：告訴 Mina**

```
✅ 報價單已產出
案件：Q20261221110000
檔案：20261221_李晴宜
連結：{url}

已自動帶入：
- 客戶資料（D2/F2/D3/F3/D4/F4）
- 合約條款 to_c 個人版（C32/C33）
- 訂金 $3,000
- 車馬費 $0（Maps 導航 XX 分鐘 < 30 分鐘免收）
- 飲食禁忌（K10：不要羊 部分長輩不吃牛）

⬜ 品項區（D7~D14 / F7~F14）空白，需要填入
⬜ E30 總金額待確認後填入
```

### 2.3 Items 表結構（查品項用）

| 欄 | 欄位 | 說明 |
|----|------|------|
| A | item_id | 編號（APP001, DST001, MAIN001, BEV001） |
| B | category | 類別：APP(鹹食) / DST(甜點) / MAIN(主食) / BEV(飲品) |
| C | standard_name | 品項正式名稱（QUOTE_DRAFT D 欄 dropdown 來源） |
| D | default_price | 報價單價（對客戶，目前很多空白） |
| E | default_cost | 食材成本（每份） |
| K | image_url | 品項照片 URL（Slide 用） |

**查詢方式**：用 Sheets API 讀 Items 分頁 A:K 欄，或用 `_buildImageMap(ss)` 查圖片。

**品項編碼規則**：
- APP = 鹹食/開胃（appetizer）
- DST = 甜點（dessert）
- MAIN = 主食
- BEV = 飲品（beverage）

### 2.4 QUOTE_DRAFT cell 地圖（copy 裡你會碰的 cell）

**框線內 C1:F55（客戶看得到）**：

| Cell | 內容 | 誰填 |
|------|------|------|
| D2 | 客戶名 | createQuote 自動 |
| F2 | 活動日期 | createQuote 自動 |
| D3 | 地址 | createQuote 自動 |
| F3 | 時間 | createQuote 自動 |
| D4 | 活動型態 | createQuote 自動 |
| F4 | 規劃人數 | createQuote 自動 |
| D5 | 活動名稱 | createQuote 自動 |
| F5 | 餐點總件數 | createQuote 自動（或 A6 填） |
| D7~D14 | **品項名稱** | **A6 或 Mina 填** ← 你的工作 |
| F7~F14 | **品項數量** | **A6 或 Mina 填** ← 你的工作 |
| row 17-19 | 熱客招待（隱藏） | createQuote 自動隱藏 |
| E25 | 租借長桌（公式） | createQuote 自動還原公式 |
| E27 | 車馬費 | createQuote 自動（Maps） |
| E28 | 搬運費 | createQuote 自動 |
| E30 | 總金額 | **Mina 填**（最終報價） |
| C32 | 【合約條款】label | createQuote 自動 |
| C33 | 合約條款全文 | createQuote 自動 |

**框線外（業務內部）**：

| Cell | 內容 |
|------|------|
| H1 | Case ID |
| H2 | 建立時間 |
| K10/L10 | 飲食禁忌 |
| K11-L13 | 車馬費/搬運費計算備註 |
| M/N 欄 | 系統資訊（CaseID/建立時間/報價狀態/付款狀態/版本） |

---

## 3. 操作路徑 B：產出 Slide 提案

### 3.1 前提

Slide 提案是在 **QUOTE_DRAFT master 模板**上操作的，不是在 copy 上。
（因為 generateProposalV2 hardcode 讀 SPREADSHEET_ID 的 QUOTE_DRAFT 分頁）

所以流程是：
1. Mina 在 master QUOTE_DRAFT 填好品項 + 數量 + 客戶資料
2. 點 MAPLAB 選單 → 產出 Slide 提案
3. generateProposalV2 讀 master QUOTE_DRAFT → 產出 Slide

**如果 A6 要幫忙產 Slide**，你需要先把資料寫到 master QUOTE_DRAFT（注意：這會覆蓋上一次的資料）。

### 3.2 generateProposalV2 讀什麼

| Cell | 讀什麼 | 用在哪 |
|------|--------|--------|
| D2 | clientName | Slide 客戶名 |
| B3 | company | Slide 公司名（有才顯示） |
| F2 | eventDate | Slide 日期 + 檔名 |
| D3 | venue | Slide 活動地點 |
| D4 | eventType | Slide 活動類型 |
| F3 | eventTime | Slide 活動時間 |
| F4 | pax | Slide 人數 |
| F5 | totalItems | Slide 件數 |
| E30 | totalAmount | Slide 總金額 |
| D7~D10 | 鹹食品項名（4 格） | Menu Slide 品項 |
| D12~D14 | 甜點品項名（3 格） | Menu Slide 品項 |
| F7~F10 | 鹹食數量 | Menu Slide qty 標示 |
| F12~F14 | 甜點數量 | Menu Slide qty 標示 |

**飲品（row 15-16）不進 Slide**（Owner 指示）。
**沒有 image_url 的品項不進 Slide**（自動過濾）。

### 3.3 Slide 產出什麼

| 頁 | 內容 | 來源 |
|----|------|------|
| P1-P7 | 模板固定頁面（品牌介紹、風格等） | Slides 模板 `1s4VJY3hIoIDd5gF_WcKVlTNzoAYr6YIq69oZ0lDnU5E` |
| P8+ | **Menu Showcase**（3×2 格品項照片 + 品名 + 數量） | A6 填的品項 + Items 表 image_url |
| 接著 | **Quotation 頁**（活動資訊 + 總金額 + 費用明細） | QUOTE_DRAFT 讀取 |
| 接著 | **Terms 頁**（合約條款） | 客戶名 + 日期 |
| 最後 | **Ready to Create 結尾頁** | 模板保留，自動移到最後 |

### 3.4 A6 產 Slide 的 step by step

1. 確認 master QUOTE_DRAFT 的 D2/F2/D3/F3/D4/F4/D7~D14/F7~F14/E30 都填好
2. 執行 `generateProposalV2()`（透過 Apps Script 選單或直接呼叫）
3. 等幾秒 → 彈窗顯示 Slide URL
4. 回傳 URL 給 Mina

**注意**：generateProposalV2 產 Slide 時會從 Items 表查每個品項的 image_url。如果品項沒圖，該品項不會出現在 Menu Slide 上。

---

## 4. 合約條款自動帶入邏輯

### 4.1 四個版本

| 版本 | 適用 | 觸發 |
|------|------|------|
| `to_c` | 個人消費者 | 非企業類活動 |
| `to_b_deposit` | 企業有訂金 | 企業類 + 沒勾「不收訂金」 |
| `to_b_full` | 企業無訂金 | 企業類 + 勾「不收訂金」 |
| `to_b_marketing` | 行銷/公關公司 | 勾「行銷/公關公司」 |

### 4.2 企業類判定

公司名有填 **OR** 活動類型含以下關鍵字之一：
尾牙、春酒、企業、公司、記者會、開幕、酒會

### 4.3 匯款帳戶自動切換

- `to_c`：個人帳戶（[收款資訊另提供] / [收款資訊另提供]）
- `to_b_*`：公司帳戶（圖蕾實業社 / 222540645172）

---

## 5. 車馬費 + 搬運費

### 5.1 車馬費

**起點**：台南市北區和緯路 2 段 450 號
**公式**：
- 導航 < 30 分鐘 → $0
- 導航 ≥ 30 分鐘 → max(ceil(km) × $6, 分鐘 × $50)

呼叫：`calcTransportFee(address)` → 回傳 `{ fee, distanceKm, driveMin, note }`

### 5.2 搬運費

| 模式 | 金額 |
|------|------|
| none（平面/有電梯） | $0 |
| with_help（2F 有人協助） | $500 |
| no_help（2F 無人協助） | $1,000 |

呼叫：`calcFloorFee(mode)` → 回傳數字

---

## 6. 低消 + 超時規則

| 規則 | 值 | 你要做什麼 |
|------|-----|-----------|
| 外燴低消 | $10,000 | 如果客戶預算 < $10K → alert Mina「低消一萬起出車」 |
| 標準服務時間 | 3 小時 | 如果活動時長 > 3 小時 → alert Mina「超時費用需加購」 |
| 訂金 baseline（個人） | $3,000 | 可由 Mina 覆寫 |
| 毛利率底線 | 70% | 品項組合的成本 < 報價 × 30% |

---

## 7. SALES_INTAKE 欄位

| 欄 | 內容 | 來源 |
|----|------|------|
| A | case_id | createQuote 自動產生 |
| B | created_at | 時間戳 |
| C | source | 'quote-system-v3.8-verified' |
| D | client_name | formData.clientName |
| E | company | formData.company |
| F | phone | formData.phone |
| G | event_type | formData.eventType |
| H | event_date | formData.eventDate |
| I | location | formData.location |
| J | pax | formData.pax |
| K | sheet_url | 產出的報價單 URL |
| L | quote_status | IMPORTRANGE 動態連結（N5） |
| M | payment_status | IMPORTRANGE 動態連結（N7） |

---

## 8. 完整操作 checklist

A6 收到 Mina 的報價指令後：

- [ ] 解析指令 → 組成 formData
- [ ] 判斷企業 or 個人（活動類型 / 公司名）
- [ ] 判斷低消（預算 < $10K → alert）
- [ ] 判斷超時（活動時長 > 3hr → alert）
- [ ] 呼叫 createQuote(formData) → 拿到 URL
- [ ] 打開 copy → 填品項到 D7~D14 / 數量到 F7~F14
- [ ] 填 E30 總金額（= Mina 說的預算，或 pax × 客單價）
- [ ] 驗算毛利率 ≥ 70%（總額 - 品項成本加總 / 總額）
- [ ] 回傳 URL + 摘要給 Mina
- [ ] （選做）在 master QUOTE_DRAFT 填同樣資料 → 呼叫 generateProposalV2 → 產 Slide → 回傳 Slide URL

---

## 版本紀錄

| 版本 | 日期 | 來源 |
|------|------|------|
| v1.0 | 2026-04-09 | A0 從 Code.gs + generateProposal_v2.gs + contractTerms.gs + quoteHelpers.gs 整理 |
