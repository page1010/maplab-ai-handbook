# MAPLAB Kitchen 術語表

> 版本：v1.0 ｜ 建立：2026-04-08 ｜ 維護：A0/A1
>
> **任何 cold-start session 必讀。** 本文件是 MAPLAB 專案內部術語的唯一權威來源。
> 若對話中出現未定義的新詞彙，追加進來並 commit（訊息格式：`docs: glossary 追加「XXX」定義`）。
>
> 踩坑防範 → `skills/pitfalls/SKILL.md`（怎麼避免踩坑，與本文互相 link）

---

## 1. 角色（Agent Roles）

| 代號 | 中文名稱 | 英文角色 | 核心職責 |
|------|---------|---------|---------|
| **A0** | 總調度秘書 | Dispatch Secretary | 跨系統調度、委派 Code task 給 A1；在 Claude Cowork 分頁，**非** terminal |
| **A1** | 系統總管中心 | System Admin / Orchestrator | 任務看板管理、agent 狀態巡檢、版本管理；**= Claude Code terminal，常駐 Mac mini** |
| **A2** | 搜尋流量作戰部 | SEO / GA Growth Unit | 關鍵字研究、SEO 文章、GA/GSC 數據 |
| **A3** | 社群與廣告成長部 | Meta Ads / Social Growth Studio | Meta 廣告、IG/FB 社群 |
| **A4** | 影像資產整理部 | Photo Archive / Asset Library | 照片分類、素材庫 |
| **A5** | 報價與提案引擎部 | Quotation Engine | 品項資料庫、成本毛利、報價公式、Slide 生成 |
| **A6** | 業務快反應部隊 | Sales Rapid Response Unit | 急件報價、快速提案 |
| **A7** | 客服與對話轉單部 | Smart Reply / Service Desk | 客戶詢問分類、標準回覆、導向報價 |

> ⚠️ A0（Cowork 分頁）≠ A1（Code terminal）。操作 repo/GAS 是 A1 的工作。見 pitfalls P6。

---

## 2. 核心 ID 速查

### 2.1 Google Spreadsheet

| 名稱 | Spreadsheet ID | 說明 |
|------|---------------|------|
| **主試算表**（MAPLAB_外燴系統_v0.1） | `1fn_woqYI_RY9ggGHVidB5SMygAzwe4CL_SOPLhe91Jg` | 所有分頁的根（QUOTE_DRAFT / Items / CONVERSATION_LOG 等） |

### 2.2 Google Slides

| 名稱 | Slides ID | 說明 |
|------|----------|------|
| **文學館標準母版** | `1s4VJY3hIoIDd5gF_WcKVlTNzoAYr6YIq69oZ0lDnU5E` | generateProposal_v2.gs 複製的來源，**預設「母版」即此** |
| **文學館案例實例** | `16R9Ivi-BTND7mWu8LkZ9cWnTG_wMCBBF7fXfP8lYhFo` | 成功交付客戶的成品，**不是範本** |

### 2.2b 快照警告

> `data/items_master.json` — **Dead snapshot，只有 102 筆，不可信**
> 真實 Items Sheet 有 108 筆。任何程式邏輯以 Google Sheet 為唯一真相來源，不讀此 JSON。

### 2.3 Google Drive 資料夾

| 名稱 | Folder ID | 說明 |
|------|----------|------|
| MAPLAB_DATA（根目錄） | `19RKLsBfNKuoCHVPFzT9D7tJrAdkTSmpt` | 所有資料的根 |
| **MAPLAB_Proposals** | `1uGBCSTLFRVm5ZPh6v10G-tImf2QB5deu` | generateProposalV2 產出的 Slide 存放處 |
| MAPLAB_Items_Photos | `1Z62HUIiVutGNqLJMGyTfBCZ-D5g2vnOT` | 品項圖片（2026-04-03 建立） |
| MAPLAB_ASSETS | `1L0udpuXLy3vEbHmzBbaLqNVDut2FFpCe` | 活動素材 |

### 2.4 GAS Projects（兩個獨立專案，push 前必確認）

| 名稱 | scriptId | 對應 .clasp.json | 職責 |
|------|---------|-----------------|------|
| **報價系統** (MAPLAB_外燴系統_v0.1) | `1JIiPW_OUwNzB4VHS4k0KHi7LYDdPlFgHWejotsY4KE3KdLTc3EB-0vpc` | `scripts/apps-script/.clasp.json` | Code.gs / generateProposal_v2.gs / Slide 生成 |
| **LINE 對話**（傳line對話到外燴系統sheet） | `1Fkl34P7p395k0YzwY8hyhz7DAAsgA3CBgyumx9ImSOFoXu771lFABSi7` | 獨立 clasp 專案 | LineWebhook.gs — 只負責 CONVERSATION_LOG 寫入 |

> ⚠️ 兩個 GAS 專案絕對不能混淆。clasp push 前必核對 scriptId。見 pitfalls P1。

---

## 3. 常見歧義術語（必讀）

### 「母版」
可能意義（按出現頻率排序）：

1. **(預設)** Google Slides 文學館標準母版 `1s4VJY3hIoIDd5gF...`（generateProposal_v2.gs 的複製來源）
2. QUOTE_DRAFT 分頁的乾淨空白版（未填資料的報價表模板）
3. Canva 的 presentation template

**Agent 規則**：Owner 說「母版」沒有上下文 → 預設為定義 1。不確定 → 立刻問。

---

### 「文學館」
- **(預設)** 文學館標準母版（Slides ID: `1s4VJY3hIoIDd5gF...`），第一個成功交付的客戶名成為內部代稱
- 可能指文學館客戶的成品實例（`16R9Ivi...`）
- **不是** Canva 設計

---

### 「報價系統」vs「LINE 系統」
- 兩個**獨立** GAS 專案，clasp push 前必確認 `.clasp.json` 的 scriptId
- 報價系統 = `1JIiPW_OUwNzB...`；LINE 系統 = `1Fkl34P7p395k0...`
- 詳細踩坑記錄 → `skills/pitfalls/SKILL.md` P1

---

### 「Slide」
- **預設**：Google Slides 應用或 generateProposalV2 產出的 .gslides 檔
- **不是** Canva presentation

---

### 「中英母版」/ 「中英雙語」
- Items 目前只有 `standard_name`（中文），**無 english_name 欄位**
- 「中英母版」= 版面上有英文佔位的母版，但程式目前只填中文
- **T-A5-004** 追蹤此缺口

---

### 「QUOTE_DRAFT」
- 主試算表內的一個**分頁名稱**（Sheet tab），不是獨立檔案
- 是業務填寫報價資訊的工作介面，也是 generateProposalV2 讀取的來源
- 有保護公式欄位，見第 5 節

---

## 4. Items 分頁欄位

> 來源：pitfalls P5 撤銷記錄 + CURRENT_STATUS.md

| 欄 | 欄位名 | 說明 |
|----|-------|------|
| A | item_id | 連號，共 108 筆（APP/DST/MAIN/BEV 前綴） |
| B | category | 品項分類 |
| C | standard_name | **中文品名，Slide 顯示用**，VLOOKUP 比對鍵 |
| D | default_price | ⚠️ **隱藏欄，不使用**，無任何流程讀取此欄 |
| E | default_cost | 成本（業務維護），QUOTE_DRAFT 公式 VLOOKUP 目標 |
| K | image_url | Google Drive 公開連結，generateProposalV2 動態讀取 |

---

## 5. QUOTE_DRAFT 欄位（關鍵 cell mapping）

> 唯一真相文件：`handoff/feedback/2026-04-02-quote-draft-v3-layout.md`

| Cell | 用途 | 讀/寫 |
|------|------|-------|
| D2 | 客戶名 / 公司名+聯絡人 | 寫入 |
| E2 | 活動日期 | 寫入 |
| D3 | 地址（venue） | 寫入 |
| **F3** | **活動時間**（⚠️ 不是 E3） | 寫入 |
| D4 | 活動型態 | 寫入 |
| F4 | 規劃人數 | 寫入 |
| D5 | 活動名稱 | 寫入 |
| F5 | 餐點總件數 | 寫入 |
| D8:D22 | 品名（可寫入純文字，下拉驗證由程式清除） | 寫入 |
| G8:G22 | 數量 | 寫入 |
| **I/J 欄** | **VLOOKUP 公式 — 禁止覆蓋** | 唯讀 |
| K1–K5 | 系統狀態（Case ID / 建立時間 / 報價狀態 / 匯款狀態 / 版本） | 寫入 |
| E35 | 總金額（客戶報價） | 公式（唯讀） |

> ⚠️ **已知 bug**：generateProposal_v2.gs 讀 `E3` 取時間，但正確位置是 `F3`。見 pitfalls P4。

---

## 6. Slide 檔名格式

```
{yyyyMMdd}_{窗口姓名}_{公司名}_提案簡報
例：20260527_Mina_鴻達科技_提案簡報
```

---

## 7. 命名慣例

| 類型 | 格式 | 範例 |
|------|------|------|
| Drive 圖片 | `{item_id}_{中文品名}.jpg` | `APP002_義大利嫩煎香料豚肉球.jpg` |
| Python 腳本 | `動作_對象_用途.py` | `整理_品項圖片_pipeline.py` |
| Task card | `T-{role}-{nnn}.md` | `T-A5-004.md` |
| Feedback log | `handoff/feedback/{YYYY-MM-DD}-{topic}.md` | — |
| Commit | `{type}({role}): {動詞} {簡述}` | `fix(A5): 修正 F3 時間欄讀取` |

---

## 8. 工具詞彙

| 術語 | 定義 |
|------|------|
| **clasp push** | 把 repo 的 `.gs` 檔推到 GAS 專案（必須先確認 scriptId） |
| **checkpoint** | `bash scripts/checkpoint.sh "角色" "做了什麼"` — 自動 commit + cherry-pick + push |
| **母版複製** | GAS 中 `DriveApp.getFileById(TEMPLATE_ID).makeCopy(name, folder)` |
| **冷啟動 / cold-start** | 新 session 開始，無上下文，需走完啟動流程 |
| **BOUND SCRIPT** | GAS 與 Spreadsheet 綁定的腳本（不是獨立 standalone project） |

---

## 9. 文件狀態（過時 / Deprecated）

| 文件 | 狀態 | 說明 |
|------|------|------|
| `projects/slides-quotation-system.md` v0.5 | ⛔ **Deprecated** | 仍引用舊 `createSlides.gs` 世界觀（已被 pitfalls P3 判為幻覺函數，`createSlidesFromSheet()` 不存在）。以 **T-A5-004** 為準。 |
| `data/items_master.json` | ⚠️ **Dead snapshot** | 102 筆，Sheet 有 108 筆，見第 2.2b 節 |

---

## 10. 狀態與現實脫節案例

> 對應 pitfalls P6「Session/角色混淆」的延伸問題：Task card 可能落後於實際執行進度。

**典型案例（2026-04-08）**：
- `T-A5-004` Task card 標記「🔲 待啟動」
- 但 `generateProposal_v2.gs` 已完成 Phase 5 實作（`aa06a60`）
- **Agent 規則**：遇到 Task card 狀態與 git log 不符 → 以 git log 為準，同步更新 Task card

---

## 11. TBD（待補）

- `generateProposal_v2.gs` 讀 `B3` 取 company — layout doc 無 B3 記錄，**待確認是 bug 或舊版欄位殘留**
- LINE webhook GAS 的部署 Web App URL（每次重新部署都會變，勿存入本文）
- Items 英文名稱欄位（T-A5-004 追蹤，目前無 english_name 欄）

---

*如發現新歧義 → 在對應章節追加 → commit 訊息：`docs: glossary 追加「XXX」定義`*
