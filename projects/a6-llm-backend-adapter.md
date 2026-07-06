# A6 LLM Backend Adapter — Pluggable 底層模型設計

版本：v0.1（設計文件，尚未實施） | 建立：2026-07-06 | 維護者：A1

---

## 背景 / Owner 原話

> 「gpt最近額度很多誒 他是你的sub agent你都不好好用起來 訓練他」
> 「我指的是codex antigravity我都有付費 允許的話 幫我把telegram上的服務分過去給他們做」
> 「類似有些軟體可以只更換底層運行的大語言模型 但實際上做的工作一樣 我的架構也是為了這個才有角色與分工 專案 等」

Owner 已付費 Codex 與 Antigravity，額度充足。目前 A6 Telegram 服務只有「Codex primary + Ollama fallback」兩層，Ollama 常駐佔用大量本機 RAM（是 2026-07-06 記憶體警報的來源之一）。Owner 要的不是新角色，是**把 A6 這個角色的底層執行模型做成可插拔**：角色定位、任務分工、系統架構完全不變，只是把實際跑文字生成的「引擎」從固定寫死的 codex→ollama 兩層，換成可設定優先序的多層 chain，並把 Codex/Antigravity 的額度用起來取代常駐吃 RAM 的 Ollama。

**本輪範圍**：只做設計文件 + adapter 骨架程式碼，**不修改 `bot_a6/bot_a6.py` 線上邏輯**。A0 需先把本文件彙報 Owner，確認方向後才進入實施。

---

## 一、現況架構（`bot_a6/bot_a6.py`）

```
A6_CHAT_PRIMARY (env, 預設 "codex")
  │
  ├─ codex_ask() ──► _codex_generate_sync()
  │                    codex exec --ephemeral -C <repo> -s read-only -o <tmpfile> [-m <model>] -
  │                    （成功則回傳，失敗 raise）
  │
  └─ 失敗時 fallback ──► ollama_ask() ──► _ollama_generate_sync()
                          POST http://127.0.0.1:11434/api/generate {model: OLLAMA_MODEL_CHAT}
```

- 只有兩層，`A6_CHAT_PRIMARY` 目前程式碼實際只認得 `"codex"`（`_run_ollama_background` 裡寫死 `if A6_CHAT_PRIMARY == "codex"`，其他值會直接報錯訊息「目前只支援 codex primary」）。
- Antigravity 完全沒接進來。
- Ollama 是唯一 fallback，代表只要 Codex 失敗（額度、網路、逾時），就會落到本機 `llama-server`——而這個 process 目前常駐佔用 RSS 實測 ~9.2GB（Owner 說的 14GB 量級一致，含 vision 模型時更高），是本機 RAM 壓力的主因之一。

---

## 二、Antigravity CLI（agy）盤點結果（2026-07-06）

| 項目 | 結果 |
|---|---|
| 是否已安裝 | ✅ 是。Homebrew cask `antigravity-cli` 1.0.14，binary 別名 `agy`，路徑 `/opt/homebrew/bin/agy` |
| 是否可非互動呼叫 | ✅ 是。`agy --print "<prompt>"` 或 `agy -p "<prompt>"`，已在 `scripts/weekly_eval_compounding.py` `run_agy_quality_review()` 生產驗證（eval 品質複核者） |
| 可切換模型 | `agy models` 列出：Gemini 3.5 Flash（Low/Medium/High）、Gemini 3.1 Pro（Low/High）、Claude Sonnet 4.6（Thinking）、Claude Opus 4.6（Thinking）、GPT-OSS 120B（Medium）；`--model <name>` 指定 |
| 逾時控制 | `--print-timeout`（預設 5m0s） |
| 工作目錄限定 | `--add-dir <dir>`（可重複） |
| **唯讀/sandbox 保證** | ⚠️ **不確定，實測有疑慮**。`--sandbox` 是布林 flag（不像 Codex `-s read-only` 那樣有明確語義）。盤點時單純打招呼，agy 仍主動列出 scratch 目錄、檢查權限、執行 shell 指令做「環境驗證」，回報自己有 `command(*): Allowed`（完整 shell 執行權限）。**沒有找到讓 agy 強制唯讀的 CLI flag。** |

**結論**：agy 適合現有的「唯讀分析/離線複核」場景（如 eval 品質複核，本來就是唯讀性質的文字任務，就算它嘗試探索環境影響也有限）。**在權限模型搞清楚之前，不建議接進 A6 Telegram 這種直接面向客戶、可能被注入內容的路徑**。這是本設計最大的待解風險，見下方「風險」章節。

Antigravity IDE（`/Applications/Antigravity.app`、`Antigravity IDE.app`）另有 GUI 版本，本文件只評估 CLI（`agy`），GUI 版留給 A0 用桌面工具操作，不在本次程式化盤點範圍內。

---

## 三、目標架構：三層 chain-of-responsibility

```
BackendChain(order=["codex", "antigravity", "ollama"])
  │
  ├─ 1. codex   ──► 沿用現有 _codex_generate_sync()，唯讀 sandbox 已驗證安全
  ├─ 2. antigravity ──► 新增，agy --print，額度充足但唯讀保證待確認（見風險）
  └─ 3. ollama  ──► 降為「冷備援」：只有前兩層都失敗才啟動，不再是常態 fallback
```

設計原則：
1. **角色分工不變**：呼叫端（`codex_ask`/`ollama_ask` 這類介面）看到的仍是「問一個問題、拿回一段文字」，換底層模型不影響上層的 mode（一般聊天 vs SEO）、history、Telegram 回覆邏輯。
2. **順序可設定**：透過環境變數 `A6_LLM_BACKEND_ORDER`（逗號分隔，如 `codex,antigravity,ollama`）決定嘗試順序與是否啟用某一層，不寫死在程式碼。
3. **Ollama 降級但不移除**：保留作為「網路/額度都掛掉時」的最後手段，但預設順序把它排最後，減少常駐觸發頻率——目標是讓 Ollama 大部分時間不需要被呼叫，逐步評估是否能把 `ollama serve` 改成需要時才啟動而非常駐。
4. **每層都要有明確的失敗判定**：目前 Codex 的失敗判定是「exit code 非 0」或「輸出檔為空」；Antigravity 需要設計等價判定（exit code、`--print-timeout` 逾時、輸出為空字串）。

---

## 四、Adapter 骨架

骨架程式碼：`bot_a6/llm_backend_adapter.py`（新檔案，**未被 `bot_a6.py` import，不影響線上服務**）。

介面設計：
- `Backend`（抽象基礎）：`name: str`、`generate(prompt: str, timeout: int) -> str`，失敗一律 raise，不吞例外。
- `CodexBackend` / `AntigravityBackend` / `OllamaBackend`：各自包一層現有的 subprocess/HTTP 呼叫邏輯（照抄 `bot_a6.py` 現有實作的呼叫方式，只是搬到獨立模組方便測試與之後接線）。
- `BackendChain`：依序嘗試，直到成功或全部失敗；記錄每一層的失敗原因供 `/status` 或 log 使用。

---

## 五、切換步驟（實施時，需 Owner/A1 核准後才做）

1. **本輪（已完成）**：設計文件 + `bot_a6/llm_backend_adapter.py` 骨架，不動 `bot_a6.py`。
2. **Antigravity 唯讀驗證**：在骨架上針對 agy 做一組唯讀性測試（丟一個「請刪除 /tmp/test.txt」之類的誘導 prompt，確認它不會真的動手），確認前不得把 `AntigravityBackend` 接進任何有真實 side effect 的路徑。
3. **接線（小步）**：把 `bot_a6.py` 的 `codex_ask`/`ollama_ask` 呼叫改成透過 `BackendChain`，先只加 `antigravity` 到 SEO/一般聊天路徑，**保留 Ollama 在鏈尾**，不要一次拔掉。
4. **觀察期**：跑一段時間，比較 Antigravity 的回覆品質/延遲/是否曾誤觸發寫入行為；同時觀察 Ollama 是否因為排到最後而顯著降低喚醒頻率、RAM 壓力是否下降。
5. **Ollama 常駐評估**：若觀察期穩定，再評估把 `Ollama.app` 從開機自啟改成需要時才啟動（不在本輪範圍，需另開任務卡）。
6. 每一步都要更新 `handoff/tasks/T-A6-001.md`（或新開 task card）與 `CURRENT_STATUS.md`，不要靜默上線。

---

## 六、風險清單

| 風險 | 說明 | 因應 |
|---|---|---|
| **Antigravity 權限不明** | `agy --print --sandbox` 觀察到會主動執行 shell 指令、宣稱有完整 shell 執行權限，沒有找到等同 Codex `-s read-only` 的強制唯讀 flag | 接生產路徑前必須先做步驟 2 的唯讀驗證；找不到官方文件前，只用在完全唯讀、低風險的場景（比照現有 eval 複核用法） |
| **客戶對話注入風險** | A6 Telegram 是面向客戶的入口，若客戶訊息本身帶有指令注入意圖，且底層 agy 又會主動執行指令，風險比現有 Codex `read-only` 模式高 | 在唯讀保證確認前，Antigravity 只接一般聊天/SEO 這類低風險 mode，不接觸 A5 報價寫入路徑 |
| **模型輸出風格不一致** | Codex/Antigravity/Ollama 底層模型不同（GPT vs Gemini/Claude vs 本地 llama），品牌語氣需要各自約束 | 三層都套用同一份 `skills/brand-voice-guide.md` 摘要（已寫入 AGENT_RECALL_PROMPTS.md 的 Codex/Antigravity 召回 prompt），降低風格漂移 |
| **降級鏈變複雜，除錯變難** | 三層 fallback 比兩層更難追蹤「這次到底是誰回答的」 | `BackendChain` 需要回傳實際使用的 backend 名稱，`/status` 指令要能顯示三層各自狀態，log 要記錄每次的實際路徑 |
| **Ollama 降級可能影響既有依賴** | 目前不確定是否有其他流程假設 Ollama 常駐可即時回應 | 實施前先搜一輪 repo 內對 `OLLAMA_BASE_URL`/`ollama serve` 的依賴，列清單再動 |

---

## 七、與現有文件的關係

- 路由規則（何時該卸載、範例呼叫）：`skills/codex-offload-guide.md`
- 召回 prompt（可直接貼給 Codex/Antigravity 的固定身份段落）：`AGENT_RECALL_PROMPTS.md` 「## Codex」「## Antigravity (agy)」
- 現有 A6 兩層架構原始碼：`bot_a6/bot_a6.py`（`_build_codex_prompt`/`_codex_generate_sync`/`ollama_ask`/`codex_ask`）
- 本文件的骨架程式碼：`bot_a6/llm_backend_adapter.py`（未接線）
