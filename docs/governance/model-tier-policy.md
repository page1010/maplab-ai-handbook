# 模型分層與額度切換政策(Model Tier & Quota Policy)

> 生效:2026-07-06。背景:Fable 5 於 2026-07-07 起按量計費(input $10 / output $50 per M tokens)。
> 對齊:`docs/company-values.md` §8「先用 Claude 開發,重複維護任務交地端模型」。
> 本檔是 A0/A1 派工前的強制查表。所有 agent 與 bot 的模型選擇以本檔為準。

---

## 0. 最高原則:只用已付費的訂閱額度,禁止按量 API

- **所有工作一律走 Owner 已付費的訂閱端**:Claude 訂閱(Cowork / Claude Code / Claude app /
  Chrome 側欄)、Codex CLI 訂閱、地端 Ollama(免費)。
- **禁止開任何按量計費的 API key**(Anthropic API、Gemini API、OpenAI API 皆同)。
  理由:2026-04-18 GCP Gemini 事件——按量 API 無警戒燒掉 ~NT$3,000。同樣錯誤不犯第二次。
  例外需 Owner 逐案書面核准 + 預算上限 + 用量回報。
- 需要旗艦模型(如 Fable 5)時,**用 computer-use / 訂閱端介面操作**(Cowork 會話、Claude app、
  claude.ai 網頁),把訂閱額度用好用滿,而不是切到按量 API。
- 額度切換的意義 = **在「已付費額度」之間切換**:Claude 訂閱額度吃緊 → Codex 訂閱 → 地端模型;
  絕不是「訂閱用完就開 API 付錢」。

## 1. 模型分層(全部是已付費/免費,無按量)

| 層 | 模型/入口 | 額度來源 | 只用於 |
|---|---|---|---|
| T0 | **Fable 5**(經 Cowork / Claude app / claude.ai,必要時 computer-use 操作)| Claude 訂閱 | 架構級診斷、跨系統事故、長時序任務、發案包/治理文件。訂閱內有多少用多少,用完即降層。 |
| T1 | **Opus 4.8**(Claude Code CLI / Cowork)| Claude 訂閱 | 日常開發、debug、review。**預設層**。 |
| T2 | **Codex CLI** | Codex/GPT 訂閱 | A6 一般聊天/SEO、A5 報價管理(T-A5-007)、重複性工程維護。 |
| T3 | **地端 Ollama**(gemma4/qwen2.5/llama3.1)| 免費 | 分類、模板化草稿、報價 fallback、巡查 hot path、高頻低價值任務。 |

**Effort 規則(T0/T1)**:預設 low/medium——官方明確說 Fable 5 low effort 常勝前代 xhigh;
只有長時序(>30 分鐘)任務才用 high/xhigh,且需在任務卡註明理由。

## 2. 切換規則(什麼時候升層/降層)

**進場分級(A0/A1 派工時做,一次)**:
1. 事故/架構/跨系統 → T0(需 Owner 一句核准,例:「用 Fable 修 dispatch」)
2. 一般開發/修 bug/review → T1
3. 有既定 SOP 或 skill 檔可照抄的重複任務 → T2/T3
4. 判斷不了 → 先 T1 跑一次;失敗兩次再升 T0,並把失敗原因寫進任務卡

**運行中自動降層(既有機制,明文化)**:
- Claude quota/rate-limit/auth 錯誤 → sticky fallback 到 Hermes/Ollama 300 秒(`bot/model_switch.py`),
  手動 `/claude` `/hermes` 覆蓋。
- A6 報價:Sheet-first(deterministic)→ 雲端 A5 → 地端 A5(`bot_a6/bot_a6.py`)。

**降層的品質補償**:T2/T3 執行時必須掛 `skills/fable5-work-discipline.md`
(驗證優先/根因優先/最小變更/發案包/回報格式)——移植行為紀律,補能力差距。

## 3. 額度守門(Quota guard,訂閱額度版)

- **金錢守門已由 §0 解決**(禁按量 API,支出恆等於既有訂閱費)。這裡守的是**訂閱額度不被浪費**。
- Claude 訂閱額度吃緊(rate limit 提示、剩餘量低)時:T0/T1 工作降到 T2/T3,
  把剩餘 Claude 額度保留給「只有 Claude 能做」的任務(架構、事故、長時序)。
- T0 任務開跑前,派工者在任務卡寫「為什麼值得用旗艦額度」;高頻/重複任務出現在 T0/T1 = 派工錯誤。
- 大量重複處理(批量分類、模板產出)禁止吃 Claude 額度,一律 T3 地端跑,T1 只做抽查驗證。

## 4. 治理迴圈(自我改進,3 層架構)

- **原語層**:模型 + 子代理 + worktree + 工具(現況已具備)。
- **編排層**:長任務不靠模型自我批評——**派 context 全新的 verifier 子代理,定期對照原始規格驗證**
  (官方 handbook 建議);巡查/Routines 跑排程(現有 A1 patrol triggers)。
- **記憶層**:模型不跨對話記憶。一切知識必須寫回 repo 才存在:
  CURRENT_STATUS(狀態)、recalls/(斷點)、skills/(紀律)、pitfalls.md(教訓)。
  → 這是 T-A1-LEARNING-LOOP-001 的落地骨架,該任務恢復時以本節為規格。

## 5. 稽核

- A1 巡查新增檢查項:8h 內的 commit 是否有「該用 T2/T3 卻用 T0/T1」的派工(看任務卡模型欄)。
- 每月第一次巡查輸出上月 T0 用量彙總給 Owner。
