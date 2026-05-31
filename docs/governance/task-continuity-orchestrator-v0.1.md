# Task Continuity Orchestrator v0.1 — 地端守夜人 / 額度中斷續航

**建立：2026-05-31 | 作者：B1 | 狀態：草案待 A1/Owner 審**
**配套：`multi-model-orchestration-v0.1.md`**

---

## 0. 要解決的真問題

Owner 真正期待的不是「半夜整理紀錄」，而是：

> 當 Codex / GPT / Gemini 額度斷、session 斷、任務卡沒寫完、OpenClaw 沒收尾時，
> 地端模型像守夜人把系統盤起來、找斷點、產出下一輪可直接餵 Codex 的 prompt，
> 等額度恢復後任務能接著跑。

**邊界硬規則：地端可以「啟動接續流程」，不可以「自作主張完成判斷」。**

---

## 1. 地端模型分級（沿用 ChatGPT 評估）

- **A 級（放心給）**：整理 log、摘要 git diff、找 TODO、整任務卡格式、檢查版本號/CTA/內連/Alt、把 Codex 結果整理成「做了什麼/改了什麼/測了什麼/還缺什麼」。
- **B 級（要審查）**：SEO 初稿、貼文草稿、投資研究格式檢查、候選股初分類、測試建議。輸出不得直接上線。
- **C 級（只反問）**：股票故事是否成立、加減碼、策略優先級。可提問，不可決策。
- **D 級（禁止）**：真實下單、自動 commit/push 核心 repo、改生產 Sheet/webhook/憑證、最終投資建議、判斷新聞真偽。

---

## 2. 缺口一：AGENT_RUN_LOG 紀律

patrol.sh 目前偵測「缺 commit」，但不偵測「缺 run-log / 把推論寫成事實」。
每個 agent（含 Codex/Antigravity/地端）每次跑完寫一份（建議放 `workbook/run-logs/`）：

```
agent / model / task_id / input_source
files_read / files_changed / commands_run / tests_run
external_sources_used
claims_verified / claims_inferred / claims_missing   ← 三分法，禁止混為事實
errors / rollback_plan / next_step
```

地端守夜人每日檢查：有沒有寫？完整嗎？有沒有宣稱查核卻無 URL？改檔卻沒測試？

---

## 3. 缺口二：額度中斷續航機制

### 3.1 佇列狀態

任務狀態新增一個值：`waiting_for_quota`。意義：任務沒失敗，只是主力模型額度暫停。
地端在這段時間做盤點、補紀錄、準備下一輪 prompt。

建議佇列檔（地端每日自動生成於 `workbook/queue/`）：
- `QUEUE_NEXT_FOR_CODEX.md`
- `QUEUE_NEXT_FOR_GPT_RESEARCH.md`
- `QUEUE_NEXT_FOR_GEMINI_VERIFY.md`

### 3.2 NEXT_CODEX_PROMPT 自動生成

地端守夜人每輪盤查後，對每個中斷任務產出可直接貼給 Codex 的接續 prompt：

```
# Next Codex Resume Prompt
你現在接手 <task_id> 任務續航。先讀：CURRENT_STATUS.md / 對應 T-*.md / 本 prompt。
上次目標：... / 已完成：... / 已確認檔案：... / 中斷位置：... / 不可碰：...
下一步請先做：1... 2... 3...
完成後必須輸出：actions_taken / files_changed / tests_run / unresolved_risks / next_checkpoint
```

目標驗收：**未來 Codex session 不用讀完整對話，只讀這份 prompt 就能接續。**

### 3.3 與既有腳本接線（不重造）

- 盤查入口：擴充 `scripts/patrol.sh` 增加 `--continuity` 模式（A1 落地，B1 不改腳本）。
- 斷點來源：`handoff/tasks/T-*.md` 接續狀態區塊 + `checkpoint.sh` 已寫的最後活動。
- 額度恢復後：Codex 讀 `workbook/queue/QUEUE_NEXT_FOR_CODEX.md` 即接續。

---

## 4. MVP（不要一次做太大）

第一版只做半自動，每天 Owner 打開能看到一份乾淨巡查 + 一份可貼 Codex 的 resume prompt 就有複利：

1. 地端讀 CURRENT_STATUS + T-*.md + 最近 git diff，標斷點。
2. 產 `workbook/queue/QUEUE_NEXT_FOR_CODEX.md`（含 resume prompt）。
3. 標記每個任務狀態（active / blocked / waiting_for_quota / waiting_for_user / ready_for_codex）。
4. 不改生產流程、不自動 commit/push、缺資料標「缺」不杜撰。

---

## 5. 落地責任分工（B1 只規劃，不越權）

| 項目 | 負責 | B1 角色 |
|------|------|---------|
| patrol.sh 加 --continuity | A1 | 已提供規格 |
| checkpoint.sh 收尾自動 verify | A1 | 已提供建議 |
| run-log 模板進 AGENT_RULES | A1 | 已提供 schema |
| Chrome Extension 召喚模組 | A1 | 已提供 prompt（見 review bundle b1_prompt.md）|
| A6 bot 客戶流程 | A6 | **不碰** |
| 地端模型實際接 Ollama | A1/Owner | 規劃 only |
