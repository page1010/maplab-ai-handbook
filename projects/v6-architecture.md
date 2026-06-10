# MAPLAB AI v6.0 架構設計文件
版本：v1.0 | 建立：2026-03-31 | 維護：A1

> 本文件從 `.claude/plans/iterative-yawning-eich.md` 落地到 repo，確保所有 session 可讀。

---

## 一、使用者核心需求

> 「我不是要一個 AI 工具，我是要一個看得懂、會回報、會變強的系統。」

| # | 需求 | 痛感 | 解法 |
|---|------|------|------|
| 1 | 我看不到系統在幹嘛（觀測性） | 🔴 | Sheets Dashboard + A0 Artifacts 渲染 + Telegram /status |
| 2 | 業務報價要能越用越準（閉環優化） | 🔴 | Shadow System — LINE 不動，AI 旁路學習 + REVISION_LOG 追蹤修改 |
| 3 | 系統不會停下來（策略循環） | 🟡 | A1 主導 Strategy Cycle，idle agent 產出候選任務 → Owner 確認 |

---

## 二、系統定位：Shadow System

```
真實世界（不動）          AI 系統（接在旁邊）
─────────────          ──────────────────
客戶 <-> 業務（LINE）  →  旁路抓對話（Data A）
業務做報價              →  A6 協助產出（Data B）
業務手動修改            →  REVISION_LOG 追蹤
最終送出報價            →  分析修改 → 優化 A5/A6/A7
                         ↓
                     系統越用越準
```

---

## 三、工具定位表

| 工具 | 定位 | 做什麼 | 不做什麼 |
|------|------|--------|---------|
| **LINE** | 不可動的真實操作層 + 資料來源 | 業務照常用；系統旁路抓對話存 Sheet | 不改流程、不接 AI bot |
| **A0 Cowork** | 外部操作 + 橋接 + Artifacts 渲染 | 人在外面時用、跨系統、遠端介入、渲染看板 | 不當唯一進度真相 |
| **A1 Claude Code** | 核心執行 + 監控 + 治理（三合一） | MCP/API 任務、Sheets 同步、巡查、strategy cycle、長任務 | UI 驗證 |
| **Chrome Tab** | UI 驗證 + 人工介入 | WordPress、GTM、網頁 QA、人工停止 | 資料清洗、Sheets 批量、長任務 |
| **Extension** | 角色召喚器 + 動態 prompt | 快速貼 recall prompt、角色切換 | 當看板或監控 |
| **Telegram** | 控制 + 通知入口 | 狀態查詢、異常推播、A6 業務協作 | 當主資料庫 |
| **Sheets** | 系統資料層 + 持久化看板 | Dashboard + 業務資料 + revision log | 當唯一 source of truth（那是 GitHub） |
| **Artifacts** | 互動式確認面板 | Owner 在 Cowork 看看板、確認策略、檢視進度 | 持久化（session 結束就沒了） |
| **GitHub** | 唯一 source of truth | 文件版本、斷點、recall prompt | 即時可視化 |

---

## 四、Dashboard 召喚方式

### 方式 1：A0 Cowork Artifacts（互動式）
在 claude.ai/chat（A0 Cowork session）對 A0 說：
- 「看板」「dashboard」「進度」「系統狀態」
- A0 會：(1) 用 Google Sheets MCP 讀 Task Board 分頁 (2) 渲染 Artifacts 表格（含狀態燈號 + 進度 + health）
- **限制**：Artifacts 是 session 內的互動面板，關閉 session 就消失，不是持久化

### 方式 2：直接開 Sheets（持久化）
- Sheets: `MAPLAB_外燴系統_v0.1`
- ID: `1fn_woqYI_RY9ggGHVidB5SMygAzwe4CL_SOPLhe91Jg`
- 分頁：`Task Board`（任務看板）+ `Owner Actions`（待辦事項）
- 欄位：task_id / task_name / owner / status / progress / current_step / last_update / output_link / health

### 方式 3：Telegram /status
- 對系統 bot 發 `/status` → A1 讀 CURRENT_STATUS.md 摘要回覆

### A1 巡查自動同步
- A1 每次巡查結束，用 MCP 同步 Sheets Task Board
- 已寫入 AGENT_RECALL_PROMPTS.md A1 段落

---

## 五、三階段落地計畫 + 進度

### Phase 1：觀測性 ✅ 完成（2026-03-31）

| Step | 內容 | 狀態 |
|------|------|------|
| 1.1 | Sheets Task Board 分頁（9 欄 + 12 筆任務） | ✅ |
| 1.2 | Sheets Owner Actions 分頁（5 筆待辦） | ✅ |
| 1.3 | A1 recall prompt 加「巡查同步 Sheets」 | ✅ |
| 1.4 | A0 recall prompt 加「Artifacts 看板渲染」 | ✅ |
| 1.5 | 初始資料填入 | ✅ |

### Phase 2：業務閉環 MVP 🔄 進行中

| Step | 內容 | 狀態 | 備註 |
|------|------|------|------|
| 2.1 | 4 個業務 Sheets 分頁 | ✅ | SALES_INTAKE/REVISION_LOG/CONVERSATION_LOG 已存在 + QUOTE_WORKBENCH 新建 |
| 2.1b | 下拉驗證（4 組） | ✅ | SALES_INTAKE status+event_type、REVISION_LOG change_type+reason_tag |
| 2.2 | 測試資料（3-5 筆） | 🔲 | **Owner/業務** 在 SALES_INTAKE 手動填真實案件 |
| 2.3 | A6 報價測試 | 🔲 | A6 讀 SALES_INTAKE → 調用 A5 → 輸出到 QUOTE_WORKBENCH |
| 2.4 | 修改追蹤 | 🔲 | 業務修改後填 REVISION_LOG change_type + reason_tag |
| 2.5 | LINE 對話手動存入 | 🔲 | 業務/Owner 把 LINE 對話重點貼到 CONVERSATION_LOG |

**驗證標準**：3 筆完整流程跑通（SALES_INTAKE -> QUOTE_WORKBENCH -> REVISION_LOG 各有 3+ 筆）

### Phase 3：自動化 + 策略循環 🔲 待開始

| Step | 內容 | 狀態 | 備註 |
|------|------|------|------|
| 3.1 | LINE webhook | 🔲 | Apps Script 接 LINE Messaging API → 自動寫 CONVERSATION_LOG |
| 3.2 | A1 週報 | 🔲 | 每週讀 REVISION_LOG → 產出高頻修改報告 → 回饋 A5 模板 |
| 3.3 | Strategy Cycle guide | 🔲 | 新建 skills/strategy-cycle-guide.md |
| 3.4 | AGENT_RULES 更新 | 🔲 | 加任務路由建議 + agent idle 規則 |
| 3.5 | Telegram A6 獨立 Bot | 🔲 | **還沒做**。用 BotFather 建 @maplab_quote_bot，獨立 a6_bot.py + launchd，完全不動現有系統 bot |

---

## 六、GPT vs A1 分析對比

**GPT 做對的（採納）**：Shadow System 概念、Chrome 是 workaround 的洞察、Strategy Cycle 流程、任務看板欄位設計

**GPT 的問題（修正）**：
- 花 7 輪才到正確答案 → A1 直接整合最終版
- 產出「需求文件」非「執行計畫」→ A1 補具體檔案改動 + 步驟
- 不知道 line-quote-assistant.md 已存在（80% 設計已寫好）→ A1 避免重複建設
- 建議 6 個新 skill → A1 判斷只需 1 個（Strategy Cycle），其餘併入現有文件

---

## 七、Sheets 位置速查

| 分頁 | Sheets ID | Sheet Name |
|------|-----------|------------|
| Task Board | 1fn_woqYI_RY9ggGHVidB5SMygAzwe4CL_SOPLhe91Jg | Task Board |
| Owner Actions | 同上 | Owner Actions |
| SALES_INTAKE | 同上 | SALES_INTAKE（15 欄） |
| REVISION_LOG | 同上 | REVISION_LOG（10 欄） |
| CONVERSATION_LOG | 同上 | CONVERSATION_LOG（8 欄） |
| QUOTE_WORKBENCH | 同上 | QUOTE_WORKBENCH（14 欄） |

欄位定義：`projects/line-quote-assistant.md` SECTION 3

---

## 八、關聯文件

| 文件 | 用途 |
|------|------|
| `projects/line-quote-assistant.md` | LINE 業務報價助手完整設計（三層資料模型 + Sheet 欄位 + 9 SECTION） |
| `skills/a6-rapid-quote-sop.md` | A6 報價 SOP（7 步流程 + 品項組合邏輯） |
| `skills/a7-customer-service-skills.md` | A7 客服技能（8 種對話模式 + Q1-Q10 模板） |
| `data/a7-reply-templates.md` | Mina 操作版回覆模板庫 |
| `AGENT_RECALL_PROMPTS.md` | A0 Artifacts 渲染指引 + A1 Sheets 巡查同步 |
| `docs/openclaw/telegram-multi-agent-router.md` | Telegram 介接多 Agent 路由架構（A6 -> A2/A5/A1） |
