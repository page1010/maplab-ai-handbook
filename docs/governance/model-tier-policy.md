# 模型分層與額度切換政策(Model Tier & Quota Policy)

> 生效:2026-07-06。背景:Fable 5 於 2026-07-07 起按量計費(input $10 / output $50 per M tokens,
> 約 Opus 4.8 兩倍;批次價半價;週用量上限 50%;coding 任務可能被自動降回 Opus 4.8)。
> 對齊:`docs/company-values.md` §8「先用 Claude 開發,重複維護任務交地端模型」。
> 本檔是 A0/A1 派工前的強制查表。所有 agent 與 bot 的模型選擇以本檔為準。

---

## 1. 模型分層(由貴到便宜)

| 層 | 模型 | 計費 | 只用於 |
|---|---|---|---|
| T0 | **Fable 5** | 按量($10/$50 per M)| 架構級診斷、跨系統事故、長時序多步 agent 任務、發案包/治理文件產出。**用前 Owner 核准**。 |
| T1 | **Opus 4.8** | 訂閱內 | 日常開發、debug、review、A1 巡查以外的 Claude 工作。**預設層**。 |
| T2 | **Codex CLI** | 訂閱內 | A6 一般聊天/SEO、A5 報價管理(T-A5-007)、重複性工程維護。 |
| T3 | **地端 Ollama**(gemma4/qwen2.5/llama3.1)| 免費 | 分類、模板化草稿、報價 fallback、巡查 hot path、高頻低價值任務。 |

**Effort 規則(T0/T1)**:預設 low/medium——官方明確說 Fable 5 low effort 常勝前代 xhigh;
只有長時序(>30 分鐘、token 百萬級)任務才用 high/xhigh,且需在任務卡註明理由。

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

## 3. 額度守門(Quota guard)

- **T0 月預算上限:Owner 設定(建議 NT$3,000/月起議)**。理由:GCP Gemini 事件
  (2026-04-18,~NT$3,000 意外帳單)的根因就是「API 能用就一直用、無預算警戒」。同樣錯誤不犯第二次。
- T0 每次任務開跑前,派工者在任務卡寫預估 token 量級;跑完寫實際用量,存入任務卡。
- 週用量到 50% 上限或月預算用罄 → 全部工作自動降 T1,不例外。
- 批次型 T0 工作(大量文件蒸餾、批量分析)一律走批次價(半價)。

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
