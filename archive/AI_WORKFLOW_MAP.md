# AI_WORKFLOW_MAP.md — MAPLAB AI 協作流程圖

**閱讀順序：CURRENT_STATUS.md → AGENT_RULES.md → 你在這裡 → TASK_QUEUE.md**

本文件說明 Claude / GPT / Gemini 的分工方式，以及各 Agent 在任務流程中的位置。

---

## Model-Level Division（模型分工原則）

| 模型 | 最適合的任務類型 |
|------|---------------|
| Claude | 長文整理、系統文件、架構收斂、handoff 撰寫、規格梳理、代碼閱讀 |
| GPT | 策略整合、商業邏輯、跨專案框架、決策輔助、文字優化、行銷文案 |
| Gemini | 表格與資料結構規劃、Google 生態整合（Sheets/Drive/Gmail）、執行型任務草稿 |

**原則：** 依任務性質選擇最適合的模型，不強制綁定。同一任務可由多個模型協作完成。

> 詳細選用指南：skills/ai-model-guide.md

---

## Agent-Level Flow（Agent 任務流程）

**A1 Handbook Agent（Claude）**
負責：建立規則、更新上下文、維護交接格式、文件版本管理、系統巡查、CURRENT_STATUS / TASK_QUEUE 維護
觸發時機：系統初始化、文件更新、新 Agent 接手前、全系統對齊

**A2/A3 SEO & Ads Team（GPT / Claude）**
負責：SEO 文章生成、關鍵字優化、WordPress 發文、廣告成效分析、異常偵測、報表生成、廣告技術文件、Python 腳本維護、OAuth 修復、GTM 設定
觸發時機：內容排程、SEO 策略更新、每日廣告數據更新、成效異常警示、腳本版本更新、API 授權問題

> A2（SEO）+ A3（Ads）於 v3.2 合併為 SEO & Ads Team，共享行銷漏斗（關鍵字→內容→廣告→轉換）。
> A6 於 v2.4 合併入 A3。不再有獨立的 A6。

**A4 Pipeline Agent（Claude）**
負責：相簿整理自動化、資料流程規劃、Google Photos to Drive
觸發時機：活動結束後相簿整理、pipeline 版本更新

**A5 Master Data Agent（Gemini / Claude）**
負責：廚房 ERP 資料結構定義、Sheets 主資料維護
觸發時機：新品項上架、活動資料建立、欄位結構更新

**A7 AI Reply System Agent（GPT）**
負責：對話紀錄整理、回覆規則建立、Line OA 回覆模組
觸發時機：定期對話整理、新回覆模板需求

---

## System Data Flow（系統資料流向）

Google Photos（活動照片）、Line OA（客戶對話）、Meta Ads（廣告數據）、Google Search Console（SEO 數據）→ A4 Pipeline Agent（相簿整理、WebP 轉檔、Drive 歸檔）→ A5 Master Data Agent（廚房 ERP 主資料、活動訂單）→ A2/A3 SEO & Ads Team（SEO 內容 + 廣告監控分析 + GTM 設定）→ A7 AI Reply System（回覆知識庫、Line OA 自動回覆）。A1 Handbook Agent 橫跨所有層，負責協調與文件維護。

---

## Handoff Protocol（交接原則）

任何 Agent 完成任務後，必須依序：

**Step 0.** 清除 CURRENT_EXECUTION_BOARD.md 的 Active Session 簽到（刪除你的簽到行）
**Step 1.** 更新對應 Task Card（handoff/tasks/T-xxx.md）的狀態和 Checkpoint
**Step 2.** 填寫 Handoff Checkpoint 格式（見 AGENT_STARTUP_PROTOCOL.md）
**Step 3.** 更新 TASK_QUEUE.md（你認領的任務狀態）
**Step 4.** 更新 CHANGELOG.md（版本號 + 變更摘要）
**Step 5.** 更新 CURRENT_EXECUTION_BOARD.md（你的 Agent 狀態 + 下一步 + 寫 Session Log）

---

## Stuck Protocol（卡住時怎麼辦）

執行中卡住？按以下順序處理：

**Step 1.** 查 skills/troubleshooting-hub.md — 13 個常見症狀路由表
**Step 2.** 找到對應技能書 → 按指引修復
**Step 3.** 找不到？→ 用回報格式通知 A1，A1 補充到 hub

> 不要浪費 context 亂試。先查表，再行動。
> 詳見 AGENT_STARTUP_PROTOCOL.md「執行中卡住怎麼辦」區段

---

## Collaboration Rules（多 Agent 協作規則）

**規則 1：不覆蓋** — 任何 Agent 在接手前必須先閱讀現有文件，確認不重複執行已完成的工作
**規則 2：不越界** — 每個 Agent 只修改自己負責的文件和 repo，不修改其他 Agent 的核心文件
**規則 3：先確認再執行** — 不確定任務範圍時，回報給 owner 確認，不自行推斷
**規則 4：GitHub 唯一** — GitHub commit 是唯一狀態真相。Agent 不讀 Notion，所有進度以 GitHub 為準
**規則 5：用技能書** — 遇到已知問題先查 skills/，不要重新發明輪子
**規則 6：簽到/簽退** — 開工前在 CURRENT_EXECUTION_BOARD.md 的 Active Session 登記（Agent 編號 / 時間 / 檔案 / 預計完成），收工前清除簽到行並寫 Session Log
**規則 7：檔案衝突檢查** — 開工前查 Active Session，若目標檔案已被其他 Agent 佔用，等待或換任務，不要同時編輯同一檔案
**規則 8：CURRENT_STATUS 優先** — 開工前第一個讀 CURRENT_STATUS.md。若其他文件與 CURRENT_STATUS 衝突，以 CURRENT_STATUS 為準
**規則 9：Task Card 記憶** — 進行中的任務必須建立 Task Card（handoff/tasks/T-xxx.md），分頁當掉時下一個 Agent 靠 Task Card 接手，不靠聊天上下文

---

*版本：v2.2 | 更新：2026-03-19 | 維護者：A1 Handbook Agent*
