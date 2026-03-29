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
[LINE OA / Telegram] → [對話接口層] → [SALES_INTAKE Sheet]
                                              ↓
                                     [A6 讀取需求]
                                              ↓
                                     [A5 計算報價]
                                              ↓
                                  [QUOTE_WORKBENCH Sheet]
                                              ↓
                                    [業務修改最終版]
                                              ↓
                                    [REVISION_LOG 自動記錄]
                                              ↓
                                  [C 層：優化任務產出]
                                              ↓
                                    [回饋到 A5 模板]
```

---

## SECTION 2 — Agent 分工

| Agent | 角色 | 職責 | 輸入 | 輸出 |
|-------|------|------|------|------|
| A0 | 調度 | 接收對話接口訊息，分派給 A6 | LINE/Telegram webhook | SALES_INTAKE 寫入 |
| A5 | 引擎 | 計算報價、成本、毛利 | SALES_INTAKE 需求 | QUOTE_WORKBENCH 草稿 |
| A6 | 助手 | 整理需求、產出補問清單、呼叫 A5 | 業務指令 | 報價草稿 + slide 結構 + 補問清單 |
| A7 | 整理 | 前期只做資料整理（FAQ/常見問題） | 客戶對話紀錄 | 結構化需求摘要 |
| A1 | 系統 | REVISION_LOG diff 比對、優化任務產出 | 業務修改紀錄 | C 層優化建議 |

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

#### 現有分頁維持不變
- Items（品項主表，E 欄 default_cost）
- QUOTE_DRAFT（A5 報價引擎）
- DropdownHelper
- Orders / OrderLines / OrderCharges

---

## SECTION 4 — 對話接口設計（預留架構）

### 接口層抽象

```
[對話平台] → [Webhook Receiver] → [Message Parser] → [SALES_INTAKE]
    ↑                                                       ↓
    └──────────── [Response Builder] ←── [A6 Output] ←── [A5]
```

### 平台適配

| 平台 | 接口方式 | 狀態 | 優先級 |
|------|---------|------|--------|
| LINE OA | Messaging API webhook | 🔲 待建 | 高（業務日常使用） |
| Telegram | Bot API + Claude MCP plugin | ✅ A1 已有 | 中（內部測試） |
| Google Sheet 直接輸入 | 業務手動填 SALES_INTAKE | ✅ 立即可用 | MVP 首選 |

### LINE OA 接口規劃（短期落地）

技術方案：LINE Messaging API → Google Apps Script（Webhook Receiver）→ 寫入 SALES_INTAKE

```
LINE OA 設定：
- Webhook URL: Google Apps Script Web App URL
- 啟用 Webhook
- 關閉自動回覆

Apps Script 邏輯：
1. doPost(e) 接收 LINE webhook
2. 解析 message.text
3. 寫入 SALES_INTAKE（raw_request = message.text）
4. 呼叫 Claude API（A6 角色）整理需求
5. 回覆 LINE：「收到！正在為您準備報價，請稍候。」
6. A6 產出結果後，推送 LINE：「報價草稿已準備好：[Sheet連結]」
```

### Telegram 接口（已有基礎）

A1 tmux 環境已有 Telegram MCP plugin，可直接接收指令。
業務在 Telegram 輸入需求 → A1 轉發給 A6 → A6 輸出到 QUOTE_WORKBENCH。

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
