# AI_WORKFLOW_MAP.md — MAPLAB AI 協作流程圖

**閱讀順序：README.md → PROJECT_CONTEXT.md → 你在這裡 → AGENT_RULES.md**

本文件說明 Claude / GPT / Gemini 的分工方式，以及各 Agent 在任務流程中的位置。

---

## Model-Level Division（模型分工原則）

| 模型 | 最適合的任務類型 |
|------|---------------|
| Claude | 長文整理、系統文件、架構收斂、handoff 撰寫、規格梳理、代碼閱讀 |
| GPT | 策略整合、商業邏輯、跨專案框架、決策輔助、文字優化、行銷文案 |
| Gemini | 表格與資料結構規劃、Google 生態整合（Sheets/Drive/Gmail）、執行型任務草稿 |

**原則：** 依任務性質選擇最適合的模型，不強制綁定。同一任務可由多個模型協作完成。

---

## Agent-Level Flow（Agent 任務流程）

**A1 Handbook Agent（Claude）**
負責：建立規則、更新上下文、維護交接格式、文件版本管理
觸發時機：系統初始化、文件更新、新 Agent 接手前

**A2 SEO Content Agent（GPT）**
負責：SEO 文章生成、關鍵字優化、WordPress 發文
觸發時機：內容排程、SEO 策略更新

**A3 Ads Monitor Agent（GPT / Claude）**
負責：廣告成效分析、異常偵測、報表生成
觸發時機：每日廣告數據更新、成效異常警示

**A4 Pipeline Agent（Claude）**
負責：相簿整理自動化、資料流程規劃、Google Photos to Drive
觸發時機：活動結束後相簿整理、pipeline 版本更新

**A5 Master Data Agent（Gemini / Claude）**
負責：廚房 ERP 資料結構定義、Sheets 主資料維護
觸發時機：新品項上架、活動資料建立、欄位結構更新

**A6 Ads Tech Agent（Claude）**
負責：廣告技術文件、Python 腳本維護、OAuth 修復
觸發時機：腳本版本更新、API 授權問題

**A7 AI Reply System Agent（GPT）**
負責：對話紀錄整理、回覆規則建立、Line OA 回覆模組
觸發時機：定期對話整理、新回覆模板需求

---

## System Data Flow（系統資料流向）

Google Photos（活動照片）、Line OA（客戶對話）、Meta Ads（廣告數據）、Google Search Console（SEO 數據）→ A4 Pipeline Agent（相簿整理、WebP 轉檔、Drive 歸檔）→ A5 Master Data Agent（廚房 ERP 主資料、活動訂單）→ A2/A3/A6 Detasys Agents（SEO 文章生成、廣告監控分析）→ A7 AI Reply System（回覆知識庫、Line OA 自動回覆）。A1 Handbook Agent 橫跨所有層，負責協調與文件維護。

---

## Handoff Protocol（交接原則）

任何 Agent 完成任務後，必須依序：

**Step 1.** 更新對應 projects/ 文件的狀態欄位

**Step 2.** 填寫 handoff/HANDOFF_TEMPLATE.md（記錄完成了什麼、下一步是什麼、阻塞點）

**Step 3.** 更新 CHANGELOG.md（版本號 + 變更摘要）

**Step 4.** 若新增 projects/*.md，必須同步更新 AGENT_RULES.md SECTION 1 角色表

---

## Collaboration Rules（多 Agent 協作規則）

**規則 1：不覆蓋** — 任何 Agent 在接手前必須先閱讀現有文件，確認不重複執行已完成的工作

**規則 2：不越界** — 每個 Agent 只修改自己負責的文件和 repo，不修改其他 Agent 的核心文件

**規則 3：先確認再執行** — 不確定任務範圍時，回報給 owner 確認，不自行推斷

**規則 4：版本優先** — GitHub commit 是唯一狀態真相，Notion 是人工快照，有衝突以 GitHub 為準

---

*版本：v1.0 | 建立：2026-03-14 | 維護者：A1 Handbook Agent*
