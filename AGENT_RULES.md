# AGENT_RULES.md — MAPLAB AI 全域行為準則
> 版本：v1.0 | 建立：2026-03-12 | 適用：所有接手 MAPLAB 任務的 AI agent

---

## ⚠️ 接手前必讀：第一件事先確認你的角色

**你現在是哪個專案的 agent？**

| 你負責的任務 | 你是 | 進度在哪 |
|---|---|---|
| 相簿整理 / Google Photos 自動化 | Pipeline Agent | Notion「AI 自動工作團隊控制台」> maplab-pipeline 專案頁 |
| 廚房 ERP / 食材庫存 / 報價 | Master Data Agent | Notion「MAPLAB Kitchen — Master Data 資料架構 Dashboard」|
| WordPress SEO / RankMath / Google Ads | Detasys SEO Agent | Notion 最新 v{x.x} 控制台頁面（搜尋「v1.5」或最新版） |
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

### 錯誤 002（模板，下一個坑記錄在此）
- 日期：
- 發生情境：
- 根因：
- 解法：

---

## 接手 SOP（每次必做，順序不可跳）

Step 1 — 確認角色（看上方角色表，30 秒內完成）
Step 2 — 讀本文件（AGENT_RULES.md）
Step 3 — 讀對應專案文件（projects/{你的專案}.md）
Step 4 — 讀 Notion 對應進度頁，找「下一棒任務」
Step 5 — 動手之前先說出：「我是 {角色}，我要做的是 {任務}，不在範圍內的事我不碰。」
Step 6 — 完成後更新 Notion checkpoint + 填寫 handoff/HANDOFF_TEMPLATE.md

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
- 技術 SOP / 突破記錄 → skills/ 或 CASE_STUDIES/（本 repo 或對應 repo 的 docs/）
- 當日交接紀錄 → Notion 對應控制台頁面 + handoff/HANDOFF_TEMPLATE.md
- 角色 / 規則文件 → 本 repo（maplab-ai-handbook）
- 敏感金鑰 / token → 絕對不進 GitHub，只放 Notion API Keys 保管室

### 5. 多 Agent 協作分工
- Claude：長文件閱讀、規則設計、架構分析、交接文件撰寫（本 handbook）
- Gemini：Google 生態系 API（Sheets / Drive / Calendar）、批量 SEO 生成
- GPT：流程拆解、模組整理、廣告數據分析

每次外包給其他 agent → 完成後必須回寫 SKILLS/ 或 CASE_STUDIES/，避免下次重踩同一個坑。

### 6. Token 管理
- 任務拆成「單一對話可完成」的小任務
- 預計 context 快用完時主動說：「我快到上限，現在更新交接文件。」
- 結束前必須更新：Notion checkpoint + handoff/HANDOFF_TEMPLATE.md

---

## 絕對禁止事項
1. .env 金鑰、token、密碼進 GitHub
2. 刪除 Google Photos 原始相片
3. 修改 main 分支已穩定 schema 而不記錄 changelog
4. 在未更新 Notion 狀態的情況下結束工作
5. 沒有確認角色就開始執行 Notion 上看到的任何任務
