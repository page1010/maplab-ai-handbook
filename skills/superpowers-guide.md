# Superpowers Skills 導覽手冊 — MAPLAB AI Agent 版
版本：v1.4 | 建立：2026-03-14 | 更新：2026-03-18

> 完整互動版：https://www.notion.so/Superpowers-Skills-320ab0806d5c807c95c7d8d633a7e5c5
> 原始 Repo：https://github.com/obra/superpowers

---

## 🗺️ 任務類型 → 建議預讀技能書（開工前路由表）

> 不是卡住才查，是開工前就知道該讀什麼。啟動任務時，先對照此表預讀相關技能書。

| 任務類型 | 建議預讀技能書 | 原因 |
|---------|-------------|------|
| 碰 GitHub API / 建 branch / PR | github-api-workflow-guide + systematic-debugging-cloud-guide | API 流程 + 雲端除錯 |
| 寫長文件 / 大量修改 | context-compression-guide + verification-checklist-guide | 防 prompt 過長 + 完成驗證 |
| 廣告相關任務 | ai-model-guide | 選 Claude 或 Gemini 執行 |
| Colab 長時間任務（>30 min） | colab-resilience-guide + systematic-debugging-cloud-guide | 防死機 + 雲端除錯 |
| Google Sheets 資料操作 | sheets-tracking-guide + ai-model-guide | Sheets 追蹤 + Gemini 整合 |
| 遇到 Bug / 執行卡住 | troubleshooting-hub → 對應技能書 | 先查急救表再行動 |
| 新 Agent 首次接手 | 全部讀 AGENT_STARTUP_PROTOCOL.md 9 步驟 | 建立大局觀 |
| 系統文件維護 / 治理 | context-compression-guide + verification-checklist-guide + strategic-review-guide | 長文 + 驗證 + 大局觀 |
| Pipeline 相簿整理 | colab-resilience-guide + media-limit-workaround | 防死機 + 媒體限制 |
| 跨專案策略規劃 | strategic-review-guide + ai-model-guide | 大局觀 + AI 分工 |

---

## 快速大綱

### 原版 Superpowers（from obra/superpowers）

| 需求 | Skill | 核心原則 |
|------|-------|---------|
| 需求模糊 | brainstorming | 一次一問，列 2-3 方案 |
| 要寫計畫 | writing-plans | 每步 2-5 分鐘，路徑/指令全寫死 |
| 要寫程式 | test-driven-development | 先寫失敗測試，紅→綠→重構 |
| 遇到 Bug | systematic-debugging | 四階段根因調查，3次修不好質疑架構 |
| 說完成前 | verification-before-completion | 有證據才能說完成 |
| Code Review | requesting/receiving-code-review | 審前清單、技術回應 |
| 多人分工 | subagent-driven-development | 雙階段審查 |
| 平行作業 | dispatching-parallel-agents | 並發 Subagent |
| 隔離環境 | using-git-worktrees | 新 branch + worktree |
| 任務收尾 | finishing-a-development-branch | 合併/PR/保留/丟棄 |
| 批次執行 | executing-plans | 分批，保留人工確認點 |
| 寫新 Skill | writing-skills | TDD 方式寫文件 |
| 第一次用 | using-superpowers | 入門 |

### MAPLAB 自建技能包

| 需求 | Skill | 核心原則 |
|------|-------|---------|
| Colab 防死機 | colab-resilience-guide | checkpoint + timeout + retry |
| Prompt 太長 | context-compression-guide | 三層防線：預防→監測→應急 |
| GitHub 雲端開發 | github-api-workflow-guide | 7步 API 工作流 + fetch 範本 |
| 完成驗證 | verification-checklist-guide | 5步驗證關卡 + MAPLAB 場景表 |
| 雲端除錯 | systematic-debugging-cloud-guide | 四階段 + Colab/API/Drive 場景 |
| 選 AI | ai-model-guide | Claude/Gemini/GPT 分工 |
| 卡住急救 | troubleshooting-hub | 症狀→解法→技能書路由表 |

---

## MAPLAB 自建 Skill 詳細

### colab-resilience-guide — Colab 防死機
- 何時用：Colab 長時間任務（>30 分鐘）
- 6 條規則：checkpoint | timeout | 進度輸出 | unzip -n | session SOP | 斷線 SOP
- 路徑：skills/colab-resilience-guide.md

### context-compression-guide — 防 Prompt Too Long
- 何時用：session 做了很多事、讀了很多文件
- 三層防線：預防（6規則）→ 監測（水位表）→ 應急（存檔SOP）
- 路徑：skills/context-compression-guide.md

### github-api-workflow-guide — GitHub API 開發流程
- 何時用：要在 GitHub 上建 branch / 寫程式 / PR / merge
- 7 步標準流程 + JS fetch 範本 + 踩坑紀錄
- 路徑：skills/github-api-workflow-guide.md

### verification-checklist-guide — 完成驗證
- 何時用：說「完成」「修好了」之前
- 5 步驗證關卡 + MAPLAB 8 大場景對照表
- 路徑：skills/verification-checklist-guide.md

### systematic-debugging-cloud-guide — 雲端除錯
- 何時用：遇到任何 bug，在亂猜之前
- 四階段 + Colab/GitHub API/Drive 15 個常見場景表
- 路徑：skills/systematic-debugging-cloud-guide.md

### ai-model-guide — AI 選用指南
- 何時用：不確定該用 Claude / Gemini / GPT
- 對照表 + 跨 AI 協作範例 + GPT 幻覺校正 SOP
- 路徑：skills/ai-model-guide.md

### troubleshooting-hub — 卡住急救手冊
- 何時用：執行中卡住，嘗試 1-2 次修不好
- 13 個常見症狀 → 解法 → 技能書路由表
- 找不到解法 → 回報格式 → A1 補充 → 全員受益
- 路徑：skills/troubleshooting-hub.md

---

## 版本紀錄

| 版本 | 日期 | 說明 | 更新者 |
|------|------|------|--------|
| v1.0 | 2026-03-14 | 從 Notion 同步 | A1 |
| v1.1 | 2026-03-17 | 加入 colab-resilience-guide | A4 |
| v1.2 | 2026-03-17 | 加入 github-api-workflow / verification-checklist / systematic-debugging-cloud | A4 |
| v1.3 | 2026-03-17 | 加入 troubleshooting-hub | A1 |
| v1.4 | 2026-03-18 | 新增「任務類型 → 建議預讀技能書」路由表；修正 troubleshooting-hub 格式 | A1 |
