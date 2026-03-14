# Superpowers Skills 導覽手冊 — MAPLAB AI Agent 版

版本：v1.0 | 建立：2026-03-14 | 來源：Notion「Superpowers Skills 導覽手冊」同步

> 本文件是 Notion Superpowers Skills 導覽手冊的 GitHub 版本，供 AI Agent 接手時快速查閱。
> 完整互動版請見：https://www.notion.so/Superpowers-Skills-320ab0806d5c807c95c7d8d633a7e5c5
> 原始 Skills Repo：https://github.com/obra/superpowers

---

## 快速大綱（開工前翻一下）

| 需求 | 用哪個 Skill | 核心原則 |
|---|---|---|
| 需求模糊 | `brainstorming` | 蘇格拉底式提問，一次一問，列 2-3 方案 |
| 要寫計畫 | `writing-plans` | 每步驟 2-5 分鐘，路徑/指令/預期輸出全寫死 |
| 要寫程式 | `test-driven-development` | 先寫失敗測試，紅→綠→重構，不跳步 |
| 遇到 Bug | `systematic-debugging` | 四階段根因調查，3次修不好就質疑架構 |
| 說完成前 | `verification-before-completion` | 先跑驗證指令，有證據才能說完成 |
| 要 Code Review | `requesting-code-review` / `receiving-code-review` | 審前清單、技術回應 |
| 多人分工 | `subagent-driven-development` | Subagent + 雙階段審查（規格→品質）|
| 平行作業 | `dispatching-parallel-agents` | 並發多個 Subagent |
| 隔離環境 | `using-git-worktrees` | 新 branch + worktree，不污染主線 |
| 任務收尾 | `finishing-a-development-branch` | 跑測試，決定合併/PR/保留/丟棄 |
| 批次執行 | `executing-plans` | 分批執行，保留人工確認點 |
| 寫新 Skill | `writing-skills` | TDD 方式寫文件，先跑失敗場景 |
| 第一次用 | `using-superpowers` | 系統入門介紹 |

---

## Skills 詳細參考

### brainstorming — 需求釐清
- **何時用：** 開始新功能前，需求還不清楚時
- **核心原則：** 一次只問一個問題、YAGNI、提出 2-3 方案讓人選
- **流程：** 問問題釐清需求 → 分段確認設計（200-300字）→ 選定方案
- GitHub: https://github.com/obra/superpowers/blob/main/skills/brainstorming/SKILL.md

### writing-plans — 計畫撰寫
- **何時用：** 設計確認後，開始實作前
- **核心原則：** 假設執行者零背景、每步驟 2-5 分鐘、路徑/指令/預期輸出全部寫死
- **重點：** 不允許「加上適當的測試」等模糊描述
- GitHub: https://github.com/obra/superpowers/blob/main/skills/writing-plans/SKILL.md

### test-driven-development — TDD
- **何時用：** 實作任何功能時，始終適用
- **鐵則：** 沒有先寫失敗測試，不能寫 Production Code
- **流程：** 寫失敗測試 → 跑測試確認失敗 → 寫最小 Code → 跑測試確認通過 → 重構
- GitHub: https://github.com/obra/superpowers/blob/main/skills/test-driven-development/SKILL.md

### systematic-debugging — 系統性除錯
- **何時用：** 遇到 Bug，在亂猜之前
- **四階段（必須依序）：** 根因調查 → 假說建立 → 最小復現 → 修復驗證
- **原則：** 3次修不好就質疑架構，不繼續猜
- GitHub: https://github.com/obra/superpowers/blob/main/skills/systematic-debugging/SKILL.md

### verification-before-completion — 完成驗證
- **何時用：** 說任何「完成」「修好了」「通過」之前
- **5 步驟：** 找到能證明的指令 → 執行完整指令 → 讀完整輸出 → 確認結果 → 才能說完成
- **禁用語：** 「應該」「大概」「似乎」「我有信心」= 停下來先驗證
- GitHub: https://github.com/obra/superpowers/blob/main/skills/verification-before-completion/SKILL.md

### subagent-driven-development — 雙階段審查開發
- **何時用：** 計畫就緒，準備開始實作
- **流程：** 每個任務派獨立 Subagent → 第一審：規格符合性 → 第二審：程式碼品質
- **重點：** 兩種審查順序不能對調
- GitHub: https://github.com/obra/superpowers/blob/main/skills/subagent-driven-development/SKILL.md

### requesting-code-review / receiving-code-review — 程式碼審查
- **requesting：** 對照計畫檢查，按嚴重性分級回報，Critical 問題阻斷進度
- **receiving：** 先理解 → 驗證 → 評估 → 技術理由推回或接受（禁止表演性回應）
- **暗號：** 「Strange things are afoot at the Circle K」= 有話想說
- GitHub: https://github.com/obra/superpowers/blob/main/skills/requesting-code-review/SKILL.md

### dispatching-parallel-agents — 平行 Subagent
- **何時用：** 有多個獨立任務可以同時進行
- **注意：** 任務之間若有依賴關係，不適合平行
- GitHub: https://github.com/obra/superpowers/blob/main/skills/dispatching-parallel-agents/SKILL.md

### using-git-worktrees — 隔離工作環境
- **何時用：** 設計通過後，開始實作前
- **做法：** 在新 worktree 建立獨立 branch，確認測試基線乾淨
- GitHub: https://github.com/obra/superpowers/blob/main/skills/using-git-worktrees/SKILL.md

### finishing-a-development-branch — 分支收尾
- **何時用：** 所有任務完成後
- **流程：** 跑完整測試 → 提供 4 個選項：合併/PR/保留分支/丟棄變更
- GitHub: https://github.com/obra/superpowers/blob/main/skills/finishing-a-development-branch/SKILL.md

### executing-plans — 批次執行計畫
- **何時用：** 計畫就緒，要開始逐步執行但不想全自動
- **特色：** 分批執行，每批完成後保留人工確認點
- GitHub: https://github.com/obra/superpowers/blob/main/skills/executing-plans/SKILL.md

### writing-skills — 自訂新 Skill
- **何時用：** 要建立團隊自己的 Skill 時
- **核心：** 先設計壓力測試場景 → 跑失敗 → 寫 Skill → 跑通過
- GitHub: https://github.com/obra/superpowers/blob/main/skills/writing-skills/SKILL.md

---

## 安裝快速指令

```bash
# Claude Code（官方 Marketplace）
/plugin install superpowers@claude-plugins-official

# Claude Code（obra Marketplace）
/plugin marketplace add obra/superpowers-marketplace
/plugin install superpowers@superpowers-marketplace

# Gemini CLI
gemini extensions install https://github.com/obra/superpowers
```

---

## 相關資源

| 資源 | 連結 |
|---|---|
| 主要 Repo | https://github.com/obra/superpowers |
| Marketplace | https://github.com/obra/superpowers-marketplace |
| 實驗性工具 | https://github.com/obra/superpowers-lab |
| Notion 導覽（互動版）| https://www.notion.so/Superpowers-Skills-320ab0806d5c807c95c7d8d633a7e5c5 |
| Multi-agent 架構參考 | https://github.com/Ibrahim-3d/conductor-orchestrator-superpowers |

---

## 版本紀錄

| 版本 | 日期 | 說明 | 更新者 |
|---|---|---|---|
| v1.0 | 2026-03-14 | 從 Notion Superpowers Skills 導覽手冊同步建立 GitHub 版本 | A1 Handbook Agent |
