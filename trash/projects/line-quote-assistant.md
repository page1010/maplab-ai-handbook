# LINE 業務報價助手系統 — MAPLAB Kitchen
版本：v1.0 | 建立：2026-03-29 | 維護者：A0 + A1
狀態：Phase 0 — 規劃完成，待落地

---

## SECTION 0 — 系統目標

### 核心問題
業務的修正經驗沒有被記錄，也沒有反饋回系統。
每一次報價都是從零開始，相同類型案件重複犯相同錯誤。

### 系統目標
建立「會因為業務實際使用而變強的報價系統」。
不是聊天機器人，是修正行為驅動的學習迴圈。

### 設計原則
1. 前期優先優化 A5 輸出（sheet / slide），不優先做 NLP / fine-tune
2. 以「修改行為」為核心，不是「對話內容」
3. 業務流程不能被打斷，不增加操作步驟
4. 免費與最小阻力優先（Google Sheet / Slides）
5. A6 是業務助手，不是決策者
6. A7 前期只做資料整理，不做高階語意理解

---

## SECTION 1 — 系統架構

### 三層資料模型

```
A: Reality Log（真實業務資料）
   ├── 客戶需求（LINE / 電話 / 面談）
   ├── 業務回覆
   ├── 補問過程
   ├── 是否報價 / 是否成交
   └── 最終版本

B: Collaboration Log（A6 協作資料）
   ├── 業務對 A6 的指令
   ├── A6 的輸出（報價草稿 / slide 建議）
   ├── 業務修改後版本
   ├── 修改原因（標籤化）
   └── 哪些區塊被改

C: Optimization Task（優化任務）
   ├── 哪些模板需要改
   ├── 哪些欄位需要新增
   ├── 哪些報價邏輯需要調整
   └── 哪些 slide 結構需要優化
```

### 資料流

```
[LINE OA]──webhook──→ [CONVERSATION_LOG] ←── A層：真實對話（自動，業務無感）
     ↑                       ↓
     │              [SALES_INTAKE]（進件，由系統或業務建立）
  業務自己管                  ↓
  LINE 對話            [A6 讀取需求] ──→ [CONVERSATION_LOG] ←── B層：A6協作對話
                             ↓
                      [A5 計算報價]
                             ↓
                   [QUOTE_WORKBENCH]
                             ↓
                     [業務修改最終版]
                             ↓
                     [REVISION_LOG]（修改紀錄）
                             ↓
                   [C 層：優化任務產出]
                             ↓
                     [回饋到 A5 模板]
```

### 關鍵設計：CONVERSATION_LOG 統一存所有對話

LINE 真實對話（A 層）和 A6 協作對話（B 層）存在同一張表，用 source 欄區分：
- source=LINE → 客戶與業務的真實對話（webhook 自動寫入，業務零操作）
- source=Telegram/Sheet → 業務與 A6 的協作對話
- 同一個 case_id 下，兩種對話自然排在一起，完整還原案件脈絡

**LINE 對話自動收集：**
LINE OA Messaging API webhook → Google Apps Script → 寫入 CONVERSATION_LOG
業務完全無感，繼續用 LINE 跟客戶聊天就好。不需要手動貼對話、不需要匯出。

---

## SECTION 2 — Agent 分工

| Agent | 角色 | 職責 | 輸入 | 輸出 |
|-------|------|------|------|------|
| A0 | 調度 | 跨系統調度、監督存檔、記憶橋接 | Owner 指令 | 任務分派 |
| A5 | 引擎 | 計算報價、成本、毛利（唯一報價計算者） | 品項+數量+條件 | QUOTE_WORKBENCH 草稿 |
| A6 | 助手 | 面對業務：整理需求、產補問清單、調用 A5（不碰 LINE、不碰客戶） | 業務 Telegram 指令 | 報價草稿 + 補問清單 |
| A7 | 整理 | 前期只做 CONVERSATION_LOG 資料整理（FAQ/常見問題歸納） | CONVERSATION_LOG | 結構化需求摘要 |
| A1 | 系統 | REVISION_LOG diff 比對、CONVERSATION_LOG 維護、優化任務產出 | 修改紀錄 + 對話紀錄 | C 層優化建議 |
| Apps Script | 橋接 | LINE webhook → CONVERSATION_LOG（純存檔，不做邏輯處理） | LINE 訊息 | CONVERSATION_LOG 寫入 |

### 關鍵分工原則
- A6 永遠只是「調用 A5 + 包裝輸出」，A6 不自己算報價
- A5 是唯一的報價計算引擎
- 業務是最終決策者，AI 只是輔助

---

## SECTION 3 — Google Sheet 表結構

### 位置：MAPLAB_外燴系統_v0.1（ID: 1fn_woqYI_RY9ggGHVidB5SMygAzwe4CL_SOPLhe91Jg）

#### 新增分頁：SALES_INTAKE（資料 A）

| 欄 | 欄位名 | 類型 | 說明 |
|----|--------|------|------|
| A  | case_id | TEXT | 自動編號 CASE-YYYYMMDD-NNN |
| B  | created_at | DATETIME | 進件時間 |
| C  | source | TEXT | LINE / Telegram / 電話 / 面談 |
| D  | client_name | TEXT | 客戶名稱 |
| E  | client_phone | TEXT | 電話 |
| F  | event_type | TEXT | 週歲 / 婚禮 / 企業 / 開幕 / 其他 |
| G  | event_date | DATE | 活動日期 |
| H  | pax | NUMBER | 人數 |
| I  | budget | TEXT | 預算（可能模糊：「大概兩萬」） |
| J  | location | TEXT | 地點 |
| K  | raw_request | TEXT | 原始需求（業務貼上或對話接口寫入） |
| L  | status | TEXT | 新進件 / A6處理中 / 已報價 / 已成交 / 未成交 |
| M  | assigned_to | TEXT | 業務名稱 |
| N  | a6_output_link | TEXT | A6 產出的 QUOTE_WORKBENCH 連結 |
| O  | notes | TEXT | 備註 |

#### 新增分頁：REVISION_LOG（資料 B — 系統核心）

| 欄 | 欄位名 | 類型 | 說明 |
|----|--------|------|------|
| A  | revision_id | TEXT | 自動編號 REV-YYYYMMDD-NNN |
| B  | case_id | TEXT | 對應 SALES_INTAKE |
| C  | revision_at | DATETIME | 修改時間 |
| D  | section | TEXT | 被修改的區塊（品項 / 數量 / 價格 / 條款 / slide） |
| E  | original_value | TEXT | A6 原始輸出 |
| F  | revised_value | TEXT | 業務修改後 |
| G  | change_type | TEXT | 新增 / 刪除 / 修改金額 / 修改品項 / 修改條款 |
| H  | reason_tag | TEXT | 客戶要求 / 經驗判斷 / 成本考量 / 場地限制 / 其他 |
| I  | reason_note | TEXT | 簡述原因（選填） |
| J  | revised_by | TEXT | 業務名稱 |

#### 新增分頁：CONVERSATION_LOG（A+B 層對話紀錄 — 系統學習的原始素材）

| 欄 | 欄位名 | 類型 | 說明 |
|----|--------|------|------|
| A  | msg_id | TEXT | 自動編號 MSG-YYYYMMDD-NNNNN |
| B  | case_id | TEXT | 對應 SALES_INTAKE（用 LINE userId 或手動關聯） |
| C  | timestamp | DATETIME | 訊息時間 |
| D  | speaker | TEXT | 客戶 / 業務 / A6 / A7 / A5 / 系統 |
| E  | message | TEXT | 訊息原文 |
| F  | source | TEXT | LINE / Telegram / Sheet / 電話備註 / 面談備註 |
| G  | line_user_id | TEXT | LINE 用戶 ID（webhook 自動帶入，非 LINE 來源為空） |
| H  | reply_to_msg_id | TEXT | 回覆哪則訊息（串接對話脈絡） |

> CONVERSATION_LOG 是整個系統的學習素材。LINE webhook 自動寫入 A 層對話，A6 互動自動寫入 B 層對話。
> 業務不需要操作這張表。

#### 現有分頁維持不變
- Items（品項主表，E 欄 default_cost）
- QUOTE_DRAFT（A5 報價引擎）
- DropdownHelper
- Orders / OrderLines / OrderCharges

---

## SECTION 4 — 對話接口設計

### 核心原則
- **LINE 是業務的工具，業務自己管對話**，AI 不介入 LINE 對話
- **LINE webhook 只做一件事：自動把對話存到 CONVERSATION_LOG**，業務完全無感
- **A6 面對的是業務，不是客戶**。業務透過 Telegram 或 Sheet 跟 A6 互動

### 架構

```
[LINE OA] ──webhook──→ [Apps Script] ──→ [CONVERSATION_LOG]（自動，靜默存檔）
                                              ↑
[Telegram] ──A6互動──→ [A6 處理] ──寫入──→ [CONVERSATION_LOG]（A6 對話也存）
                            ↓
                     [SALES_INTAKE]（建立進件）
                            ↓
                     [A5 → QUOTE_WORKBENCH]（產出報價）
```

### LINE OA webhook（自動收集對話，不介入）

技術方案：LINE Messaging API → Google Apps Script → CONVERSATION_LOG

```
LINE OA 設定：
- Webhook URL: Google Apps Script Web App URL
- 啟用 Webhook
- 不關閉自動回覆（業務自己設定 LINE OA 回覆）

Apps Script 邏輯（極簡）：
1. doPost(e) 接收 LINE webhook
2. 解析 message：userId / text / timestamp
3. 寫入 CONVERSATION_LOG（speaker=客戶或業務, source=LINE）
4. 不回覆、不處理、不觸發 AI — 純存檔
```

> LINE webhook 的目的不是做聊天機器人，是**建立 A 層 Reality Log**。
> 業務繼續用 LINE 跟客戶聊天，系統在背景靜默記錄所有對話。

### A6 協作接口（業務 → A6）

| 接口 | 方式 | 狀態 | 說明 |
|------|------|------|------|
| Telegram | 業務在 Telegram 跟 A6 對話 | ✅ A1 已有 MCP | 主要協作通道 |
| Google Sheet | 業務填 SALES_INTAKE | ✅ 已建好 | 備用（簡單案件直接填） |

A6 的每一輪回覆都自動寫入 CONVERSATION_LOG（source=Telegram, speaker=A6）。

### case_id 關聯邏輯

- LINE 對話用 line_user_id 分群
- 業務在 Telegram 跟 A6 說「幫王小明報價」→ A6 建 SALES_INTAKE 一筆 → 生成 case_id
- A6 同時在 CONVERSATION_LOG 搜尋相近的 line_user_id 對話 → 自動關聯
- 關聯不到的（電話/面談進來的）→ case_id 先空，業務之後手動補或不補

---

## SECTION 5 — 修改紀錄最小成本落地

### 核心思路
業務零額外工作。修改紀錄由系統自動產出。

### 實作方式

**Phase 1（MVP）— 手動標記**
- 業務在 QUOTE_WORKBENCH 改完後，在 REVISION_LOG 簡單填：改了什麼、為什麼改
- 最小操作：下拉選 change_type + reason_tag，兩個欄位

**Phase 2 — 半自動 diff**
- A1 定期（每天一次）比對 QUOTE_WORKBENCH 的版本紀錄
- 自動偵測哪些 cell 被改了
- 自動寫入 REVISION_LOG 的 section / original_value / revised_value
- 業務只需要補 reason_tag（下拉選單，5 秒完成）

**Phase 3 — 全自動**
- Google Apps Script onEdit trigger 即時追蹤修改
- 自動分類 change_type
- 每週自動產出「本週高頻修改報告」→ 回饋到 A5

---

## SECTION 6 — MVP 實作步驟

### Week 1：基礎建設

| Step | 任務 | 負責 | 產出 |
|------|------|------|------|
| 1 | 在 Sheet 建 SALES_INTAKE 分頁 | A1 | 分頁 + 欄位 + 下拉驗證 |
| 2 | 在 Sheet 建 REVISION_LOG 分頁 | A1 | 分頁 + 欄位 + 下拉驗證 |
| 3 | 寫 A6 rapid quote skill | A1 | skills/a6-rapid-quote-sop.md |
| 4 | 業務手動在 SALES_INTAKE 填 3-5 筆測試需求 | Owner/業務 | 測試資料 |
| 5 | A6 讀取 → 產出報價草稿到 QUOTE_WORKBENCH | A6 | 報價草稿 |

### Week 2：對話接口 + 修改追蹤

| Step | 任務 | 負責 | 產出 |
|------|------|------|------|
| 6 | LINE OA webhook 接口（Apps Script） | A1 | Webhook URL |
| 7 | Telegram 接口測試（用現有 MCP） | A1 | 驗證流程 |
| 8 | 業務修改後，手動填 REVISION_LOG | Owner/業務 | 修改紀錄 |
| 9 | A1 比對版本 diff，補全 REVISION_LOG | A1 | 自動化 diff |

### Week 3-4：優化迴圈啟動

| Step | 任務 | 負責 | 產出 |
|------|------|------|------|
| 10 | 分析 REVISION_LOG 高頻修改 | A1 | 優化建議清單 |
| 11 | 更新 A5 模板（報價 + slide） | A5 | 更新版模板 |
| 12 | 建立活動類型模板（週歲 / 婚禮 / 企業） | A5 | 3 套模板 |

---

## SECTION 7 — 風險與避坑

| 風險 | 嚴重度 | 預防 |
|------|--------|------|
| LINE webhook 技術卡關 | 中 | MVP 先用 Sheet 手動輸入，LINE 是 Week 2 才做 |
| 業務不填 REVISION_LOG | 高 | Phase 1 只要選兩個下拉，5 秒完成。Phase 2 自動化 |
| A6 跟 A5 職責模糊 | 中 | 硬性規則：A6 不算報價，只調用 A5 |
| QUOTE_WORKBENCH 版本衝突 | 低 | 每個 case 獨立一行，不共用同一張報價 |
| 對話接口訊息格式不統一 | 中 | A7 做前處理：結構化需求摘要，再給 A6 |
| Telegram bot 之前走過彎路 | 高 | 不重蹈覆轍：用 Claude Code terminal + MCP plugin，不寫 bot.py |

---

## SECTION 8 — 與現有系統銜接

| 現有資產 | 銜接方式 |
|---------|---------|
| QUOTE_DRAFT（A5 報價引擎） | A6 調用 A5，輸出到 QUOTE_WORKBENCH |
| Items 主表（102 品項 + default_cost） | A5 計算直接讀 Items |
| 932 份歷史報價分析（data/） | 初始化 A6 的報價經驗 |
| quote-terms-reference.md | A6 自動帶入對應條款（個人版 / 企業版） |
| quote-items-unmatched.md | 補問清單參考（品項不在 Items 表時提醒） |
| T-A5-003 熱客招待規則 | A6 自動判斷是否觸發招待 |
| slides-quotation-system.md | A6 產出 slide 結構時參考 |
| skills/credentials/ | API 存取（三層備援） |

---

## SECTION 9 — 短中長期目標

### 短期（0-30天）— 系統跑起來
- LINE / Sheet → A6 → 初版報價
- 建立 REVISION_LOG
- 開始累積「修改紀錄」

### 中期（1-3個月）— 優化 A5
- 分析高頻修改
- 更新報價模板 / slide 模板 / 欄位結構
- 建立不同客群模板（企業 / 週歲 / 婚禮）
- 減少業務修改次數

### 長期（3-6個月）— 系統自我優化
- 從 REVISION_LOG 自動產生優化建議
- 建立 rule / template library
- 再評估是否需要 fine-tune
- 讓系統「越用越準」

---

## 版本紀錄

| 版本 | 日期 | 說明 | 更新者 |
|------|------|------|--------|
| v1.0 | 2026-03-29 | 初版系統規劃（Owner 需求 + A0 架構修正） | A0 Cowork |

---

*本文件由 A0 Cowork 建立，基於 Owner 的系統方向說明 + 現有 MAPLAB 架構修正。*
*對話接口（LINE / Telegram）預留架構已設計，MVP 從 Google Sheet 直接輸入開始。*
