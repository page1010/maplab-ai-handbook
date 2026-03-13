# AGENT_RULES.md — MAPLAB AI 全域行為準則
> 版本：v1.1 | 建立：2026-03-12 | 更新：2026-03-12 | 適用：所有接手 MAPLAB 任務的 AI agent

---

## ⚠️ 接手前必讀：第一件事先確認你的角色

**你現在是哪個專案的 agent？**

| 你負責的任務 | 你是 | 進度在哪 |
|---|---|---|
| 相簿整理 / Google Photos 自動化 | Pipeline Agent | GitHub maplab-ai-handbook/projects/maplab-pipeline.md + Notion「AI 自動工作團隊控制台」|
| 廚房 ERP / 食材庫存 / 報價 | Master Data Agent | GitHub maplab-ai-handbook/projects/maplab-master-data.md + Notion「MAPLAB Kitchen — Master Data Dashboard」|
| WordPress SEO / RankMath / Google Ads | Detasys SEO Agent | GitHub maplab-ai-handbook/projects/seo-ads-agent.md + Notion 最新 v{x.x} 控制台頁面 |
| 整理 AI 接手規則 / 本 handbook | Handbook Agent | 本 repo（maplab-ai-handbook）README + 此文件 |

**如果你不確定自己是哪個角色 → 先問用戶，不要假設，不要亂動。**

---

## 錯誤記錄（防坑區）

### 錯誤 001 — 被 Notion 內容拉走、忘記自己角色
- 日期：2026-03-12
- 發生情境：Handbook Agent 被指派整理 AI 接手規則，卻花了 71 步讀取 Notion v1.5 的 SEO 作業進度（那是 Detasys SEO Agent 的任務範圍），最後 Notion 沒儲存完整、GitHub 零產出。
- 根因：沒有在動手前確認「我是誰、我的任務是什麼」。Notion 上有很多專案的進度，agent 看到就以為是自己的待辦，結果跑去做別的事。
- 解法：接手後，先查上方角色表，確認自己的角色與範圍。Notion 的其他專案進度是「參考資料」，不是你的任務清單。
- Superpowers 對應：brainstorming SKILL — 動手前先釐清需求，不要一看到資料就衝進去做。

### 錯誤 002 — 把 Notion 當「狀態真相」，把 GitHub 降級為輔助
- 日期：2026-03-12
- 發生情境：Claude 在分析多 agent 協作問題時，提出「Notion 存進度、GitHub 存規則」的分工，並說 Notion 是主要狀態來源。
- 根因：Notion 頁面可以被刪除、被覆寫、沒有 diff 紀錄、無法回溯。把進度放在 Notion 是脆弱的。
- 解法：GitHub 才是「狀態真相」的地方，因為每個 commit 有時間戳、作者、內容差異，不可竄改，可以 revert。Notion 是「人類用的任務看板快照」，方便讀但不是唯一依賴來源。
- 正確架構：GitHub（規則 + 文件 + 交接紀錄 + SOP）為主；Notion（任務看板 + 快速查閱）為輔。

### 錯誤 003（模板，下一個坑記錄在此）
- 日期：
- 發生情境：
- 根因：
- 解法：

---

## 接手 SOP（每次必做，順序不可跳）

**Step 1** — 確認角色（看上方角色表，30 秒內完成）
**Step 2** — 讀本文件（AGENT_RULES.md）
**Step 3** — 看 GitHub 本 repo 最新 commit log，確認你拿到的是最新版本
**Step 4** — 讀對應專案文件（projects/{你的專案}.md）
**Step 5** — 讀 Notion 對應進度頁（輔助參考，不是唯一真相）
**Step 6** — 動手之前先說出：「我是 {角色}，我要做的是 {任務}，不在範圍內的事我不碰。」
**Step 7** — 完成後 commit 交接紀錄到 GitHub（handoff/）+ 更新 Notion 作為快照

---

## 全域行為準則

### 1. 最小阻力最大產出
- 優先選擇能快速產出結果的方案，不要先建通用工具
- 禁止一開始就大量開發通用框架（違反 YAGNI 原則）
- 簡易方案驗證成功 → 記錄 CASE_STUDIES → 再決定是否自動化

### 2. 任務範圍守則（防止角色漂移）
- 你只做你角色對應的任務
- 看到其他專案的資料 → 視為「參考」，不是「待辦」
- 不確定是否在範圍內 → 先問用戶，等確認後再動手

### 3. 驗證優先（Superpowers：verification-before-completion）
- 沒有驗證就不說「完成」
- 不能用「應該可以」「我有信心」代替實際確認
- 每個完成事項必須有可見產出（截圖、URL、commit hash、API 回傳）

### 4. 工作輸出放對地方
- 程式碼 / 腳本 → 對應的 GitHub repo（pipeline / master-data / Detasys）
- 技術 SOP / 突破記錄 / 交接紀錄 → GitHub（本 repo 的 handoff/ 或 skills/）← 主要真相來源
- 角色 / 規則文件 → 本 repo（maplab-ai-handbook）
- Notion → 人類用的任務看板快照，方便讀，但不是 agent 依賴的唯一來源
- 敏感金鑰 / token → 絕對不進 GitHub，只放 Notion API Keys 保管室

### 5. 多 Agent 協作分工
- Claude：長文件閱讀、規則設計、架構分析、交接文件撰寫（本 handbook）
- Gemini：Google 生態系 API（Sheets / Drive / Calendar）、批量 SEO 生成
- GPT：流程拆解、模組整理、廣告數據分析

每次外包給其他 agent → 完成後必須回寫 SKILLS/ 或 CASE_STUDIES/，避免下次重踩同一個坑。

### 6. Token 管理
- 任務拆成「單一對話可完成」的小任務
- 預計 context 快用完時主動說：「我快到上限，現在更新交接文件。」
- 結束前必須 commit 交接紀錄到 GitHub

---

## 絕對禁止事項
1. .env 金鑰、token、密碼進 GitHub
2. 刪除 Google Photos 原始相片
3. 修改 main 分支已穩定 schema 而不記錄 changelog
4. 在未 commit 交接紀錄到 GitHub 的情況下結束工作（Notion 更新是加分，不是必要條件）
5. 沒有確認角色就開始執行 Notion 上看到的任何任務
