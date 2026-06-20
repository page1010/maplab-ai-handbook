# Phase 1 — @maplab_claude_bot Claude/Hermes 切換現況調查（只讀）

## Startup Check

- Role: B1 Builder（依 B1 契約）。
- Read first: `CURRENT_STATUS.md`、`pitfalls.md`、`skills/experience-log.md`（EXP-F012）、`bot/DEPRECATED.md`。
- Repo: `/Users/pagemacmini/maplab-ai-handbook`（canonical）。
- Scope this pass: 純調查 + 評估，未改任何程式碼，未 push，未讀 secrets/.env 內容，未把 Hermes 輸出當事實使用（僅引用既有 review bundle 與本機 log 證據）。

## 0. 重要先決事實：這件事 2026-06-15 已經做過一輪，而且大部分已經實作完成

`skills/experience-log.md` EXP-F012（2026-06-15）與 `pitfalls.md`「2026-06-15 — Hermes fallback means the Telegram Claude bot fallback path」記錄了同一個需求：Owner 要 `maplab_claude_bot` 在 Claude 沒額度/失敗時切到 Hermes，且要保留貼圖、控制電腦的能力，Hermes 要善用長期記憶。

Git log 顯示 2026-06-17 已經實作並上線：

```
9f84998 fix(bot): dispatch telegram summons to codex packets
877af04 fix(bot): add deterministic role dispatch
07a5261 fix(bot): harden telegram hermes runtime fallback
cffcab6 feat(bot): add hermes fallback for claude quota
```

`com.maplab.telegrambot` launchd job 目前是這版 `bot/bot.py`（PID 1344，啟動於 2026-06-17 19:51，至今 ~3 天無重啟）。**也就是說：自動 Claude→Hermes 切換已經存在且正在跑，不是從零開始的功能。** 今天的調查重點因此改成：(a) 現有實作做到什麼程度、(b) 它今天實際上有沒有正常工作、(c) 跟 Owner 這次說的「想要的東西」之間還缺什麼。

## 1. Bot 程式碼位置與身份

- 入口：[bot/bot.py](../../bot/bot.py)（2117 行），launchd label `com.maplab.telegrambot`，plist `~/Library/LaunchAgents/com.maplab.telegrambot.plist`。
- `@maplab_claude_bot` 與 `bot/bot.py` 的對應關係，交叉確認於三份獨立文件：`docs/security/SECURITY_INCIDENT_2026-05-05.md`（列出 `@maplab_claude_bot` 為受影響系統之一）、`pitfalls.md` 2026-06-17/2026-06-15 條目、`skills/experience-log.md` EXP-F012（皆指向 `bot/bot.py` 是這隻 bot 的 entrypoint）。沒有讀取 `.env` 內容驗證 token 對應的 bot username，但三份獨立文件交叉一致，可信度足夠用於規劃；若要 100% 鐵證，需 Owner 自己對 Telegram 確認 bot username。
- 注意：`bot/bot.py` 檔頭 docstring 寫「直接讀取 repo markdown 文件回傳，無 Claude API 呼叫」——這是舊版殘留說明，**與目前程式碼不符**（目前會呼叫 `claude -p` CLI 與 Hermes/Ollama），純文件性問題，不影響功能，但容易誤導下一個 agent。
- `bot/DEPRECATED.md` 本身內容也是舊的（2026-03-27 寫的「bot.py 已棄用」），但檔案開頭被人手動加了一行更正：「本文件描述過期 — bot/bot.py 實際為 A1 遠端讀檔終端，PID active via launchd」。結論：**bot.py 沒有被棄用，是目前唯一在跑的版本**，但這份文件本身具有誤導性，建議之後清理。
- 另有 `bot_a6/bot_a6.py`（`@maplab_a6_bot`，A6 報價機器人）—— 這是**不同的 bot**，已經有自己獨立的 Ollama/gemma4 local fallback（`bot_a6/a5_quote_engine.py`，2026-05-18 上線）。本次調查不涉及它，列出只是避免兩隻 bot 搞混。
- `/Users/pagemacmini/Documents/New project` 底下也有大量 Hermes 相關檔案（`tests/test_hermes_commander.py`、`tests/test_hermes_chat_gateway.py` 等），但那是 **Investment OS 的 Hermes 生態（commander panel、chat gateway、roundtable）**，跟 `@maplab_claude_bot` 的 fallback 是兩個完全獨立的系統，沒有共用程式碼。不要混在一起改。

## 2. (a) 這 bot 現在能不能用 Claude？接的是什麼？

**現況：primary 是 Claude Code CLI（`claude -p --dangerously-skip-permissions`），不是 Claude API，也不是純對話腳本。**

- `_claude_ask_raw()`（[bot/bot.py:1371](../../bot/bot.py)）用 `asyncio.create_subprocess_exec("claude", "-p", "--dangerously-skip-permissions", full_prompt, ...)` 呼叫本機 Claude Code CLI，帶 `CLAUDE_CODE_OAUTH_TOKEN`。
- 失敗會被分類成 `failure_kind`：`quota` / `rate_limit` / `auth` / `cli_missing` / `timeout` / `primary_unavailable`（`_classify_claude_failure()`，[bot/bot.py:387](../../bot/bot.py)）。
- 這些失敗類型（不只是「沒額度」，也包含認證錯誤、CLI 不存在、逾時）都會觸發 fallback（`_should_fallback_to_hermes()`，[bot/bot.py:442](../../bot/bot.py)）。
- 對話記憶：每個 chat_id 保留最近 20 則訊息的 deque，存在 `bot/conv_history.json`，Claude prompt 會帶入歷史。
- 貼圖：`handle_photo()`（[bot/bot.py:1926](../../bot/bot.py)）存到 `data/telegram-photos/`，本機路徑交給 Claude/Hermes 讀，圖片走 Hermes 時固定用 `vision` toolset。
- 電腦控制：primary（Claude CLI）跑在 `--dangerously-skip-permissions`，理論上有完整工具權限；fallback（Hermes）依 `_format_hermes_receipt()` 明文限制成「read/draft/smoke/image-analysis only；live send/delete/publish/secrets/computer-control 需最後確認」，即 **Hermes fallback 故意比 Claude 弱，不能直接控制電腦**，這是刻意設計（EXP-F012 第6點要求的能力對等清單已經做了，但是做成「明確降級＋告知」而非「完全對等」）。

**Fallback 接的是什麼模型：**

- 程式裡叫 `HERMES_FALLBACK_MODEL`，預設值 `gemma4:latest`（`.env` 沒有覆寫這個變數，所以實際生效值就是 `gemma4:latest`，已用 `grep -o "^[A-Z_]*="` 確認 `.env` 只設了 `TELEGRAM_BOT_TOKEN` / `OWNER_CHAT_ID` / `CLAUDE_CODE_AUTO_COMPACT_WINDOW` / `CLOUDFLARE_API_TOKEN`，沒有任何 `HERMES_*` 變數，沒有讀值，只列 key）。
- 「Hermes」不是一個品牌模型，是本機 `hermes` CLI（`~/.local/bin/hermes`，背後是 `ai.hermes.gateway` launchd 服務，目前 PID 951 在跑，已存活 11Jun26 至今）。Hermes CLI 失敗（no final response / 逾時 / 找不到指令）時會再降一級，直接打 Ollama HTTP API（`http://127.0.0.1:11434/api/generate`，`ollama_direct_ask()`）。
- 所以實際是三層：**Claude CLI → Hermes CLI（gemma4:latest，搭配記憶 anchor prompt）→ Ollama 直連（同一顆 gemma4:latest，無 toolset、無記憶包裝）**。
- 本機 `ollama list` 確認可用模型：`gemma4:latest`、`qwen2.5:14b`、`qwen2.5-coder:7b`，沒有名為「Hermes」的模型檔——Owner 認知的「Hermes」是這條 fallback 角色的名字，底層模型其實是 gemma4。

## 3. (b) 目前有哪些功能/指令

`/start /help /ping /status /owner /task /patrol /queue /agent /commit /blocker /refresh /ask /codex_dispatch /runtime /reset /clip`，加上一般文字訊息（`handle_message`）與貼圖（`handle_photo`）走 Claude→Hermes fallback。

值得注意的兩個：

- **`/runtime`**（[bot/bot.py:1740](../../bot/bot.py)）：回報 primary/fallback 是否可用、fallback engine 路徑、fallback model、toolsets、是否強制 fallback 測試模式。這已經是一個「模型/額度健康檢查」指令，但**只在被問時才回報**，不會自動出現在一般對話。
- **`/codex_dispatch`** 與自然語句派工：會建立 `workbook/telegram-dispatch/TG-DISPATCH-*` 任務包，回 dispatch_id/角色/worker/status（2026-06-17 修的，回應 Owner「所以誰做你召喚了嗎」那次抱怨）。

**沒有的指令：`/model claude`、`/model hermes`，或任何手動切換指令。** 目前唯一能強制走 Hermes 的方法是設定環境變數 `MAPLAB_FORCE_HERMES_FALLBACK=1`（`_truthy_env` 檢查），而這個變數要寫進 `bot/.env` 或 launchd plist 後**重啟服務**才生效——Owner 在 Telegram 對話當下沒有辦法即時切換，這是後面會點出的主要缺口。

## 4. (c) 目前每次回給使用者什麼

- **Primary（Claude）成功時**：只回答案本身，沒有附加任何 model/來源/信心資訊（這是合理的，不需要每次都報來源）。
- **Fallback（Hermes 成功）時**：會自動附 `_format_hermes_receipt()`（[bot/bot.py:1262](../../bot/bot.py)），內容包含：
  - `🟡 Claude primary unavailable，Hermes fallback 接手`
  - `primary_failed_reason`（Claude 的原始錯誤訊息）
  - `fallback=Hermes`、`model: gemma4:latest`、`toolsets`
  - `agent` / `date`
  - `memory_sources`（hermes 讀了哪些記憶錨點）
  - `allowed_actions`（明確列出能做/不能做）
  - `next_check`
  - 這份 receipt 在 `data/telegram-logs/2026-06-17.md` 有兩筆真實線上紀錄（16:43、19:26，都是因為 Claude OAuth `401 authentication_error` 觸發），格式跟設計一致，**這個功能本身是真的有在動、不是只存在於 mock test。**
- **Fallback 整條鏈都失敗時**：只回 Claude 原始錯誤 + `⚠️ Ollama direct fallback 無回應`（或 `⚠️ Ollama direct fallback 錯誤: ...`），**沒有 receipt、沒有「目前無法使用，請稍後再試」這種人話收尾**，這正是今天（2026-06-20 08:18）實際發生的狀況，見下一節。
- **錯誤/額度資訊**：有（`primary_failed_reason` 帶出 Claude 的原始 401/quota/timeout 訊息），但只在 fallback 觸發時才看得到；Claude 成功時 Owner 完全看不到「還剩多少額度」這種前瞻資訊（Claude CLI 本身也不一定會給）。

## 5. 今天的真實證據：fallback 鏈在今天早上整個失敗過一次

`data/telegram-logs/2026-06-20.md`（今天，repo 內既有 log，非本次新建）：

```
## 2026-06-20 08:18:25
Owner：你是什麼模型在回覆我
Bot：⚠️ Claude 錯誤: Failed to authenticate. API Error: 401 ... "authentication_error" ...
⚠️ Ollama direct fallback 無回應
```

對照碼：`claude_ask_with_fallback()` 在 `hermes_answer.startswith("⚠️")` 時會回 `f"{claude_result.answer}\n\n{hermes_answer}"`（[bot/bot.py:1363](../../bot/bot.py)），跟今天看到的格式完全吻合——表示 `hermes_ask()` 內部一路降到 `ollama_direct_ask()`，而 Ollama 回的 `response` 欄位是空字串（`_ollama_generate_sync` 拿到回應但 sanitize 後是空的，[bot/bot.py:1119](../../bot/bot.py)），所以印出「無回應」。

**這代表：Owner 今天早上問「你是什麼模型」時，三層 fallback 全部失敗，Owner 拿到的是一句純錯誤訊息，沒有任何可用回答。** 這也直接呼應 Owner 這次提需求的動機：「Claude 沒額度時切到 Hermes讓他能繼續對話」——現有自動 fallback 理論上該接住，但今天線上至少有一次接不住。

另外，`bot.log` / `launchd_stdout.log` / `launchd_stderr.log` 三個檔案的最後一筆紀錄都停在今天 **08:53:18~08:53:32**（6 筆 DNS 連線錯誤 `httpx.ConnectError: nodename nor servname provided`），之後到現在（20:49）**完全沒有新的 log**，但用 `lsof` 查 PID 1344 目前**確實有一條到 Telegram IP 的 ESTABLISHED 連線**，DNS 現在也正常（`dig api.telegram.org` 有解析、`curl api.telegram.org` 回 302）。這代表 bot process 本身沒死，但結構化 log 已經停寫 ~12 小時——可能是日誌寫入卡住、也可能是 python-telegram-bot 的重試迴圈在某次例外後進入了沒有 log 輸出的狀態。**這是獨立於 Claude/Hermes 切換的另一個風險，建議 Owner 用 `/ping` 實際測一次確認 bot 現在到底有沒有在正常回應**；我沒有主動發測試訊息給 bot（會產生 Owner 看得到的對話紀錄，屬於有外部可見副作用的動作，超出本輪只讀調查的授權範圍）。

## 6. 80/20 缺口（站在 Owner 角度，缺什麼）

1. **沒有手動切換指令**——這是 Owner 這次提需求的核心，目前完全不存在。只能靠自動分類（quota/auth/timeout/cli_missing/primary_unavailable）觸發，Owner 自己沒有「我現在要用 Hermes」或「額度應該回來了，切回 Claude」的主動權，要切只能改 `.env` 再重啟 launchd 服務。
2. **Fallback 鏈本身不夠穩**——今天的真實案例顯示三層全敗時只回錯誤訊息，沒有人話收尾、沒有重試建議、沒有「等一下我再試一次」之類的引導。比起「加手動切換指令」，**先讓既有自動 fallback 在全敗情境下也有合理收尾，是更高槓桿、風險更低的修法**。
3. **沒有結構化的「目前用哪個模型」狀態**——`/runtime` 有，但要主動問;一般回答完全不帶 source 標籤（Claude 成功時刻意不帶是合理的，但如果要做「手動切換」，至少要讓 Owner在切換後的下一則回覆知道現在生效的是哪一邊，否則容易搞不清楚現在是誰在回話）。
4. **沒有為「訓練 Hermes」準備過資料**——見下節。
5. **文件性債務**：`bot/bot.py` 檔頭 docstring 過期、`bot/DEPRECATED.md` 內容過期但只在開頭加了一行更正，容易誤導下一個讀者。低成本，建議之後一併清理（不影響功能優先度）。

## 7. Hermes 是什麼、在哪跑、訓練資料現況

- **是什麼**：本機 `hermes` CLI（`~/.local/bin/hermes`），由 `ai.hermes.gateway` launchd 服務（`/Users/pagemacmini/.hermes/hermes-agent/venv/bin/python -m hermes_cli.main gateway run --replace`，PID 951，已存活約 9 天）提供。對 `@maplab_claude_bot` 而言，Hermes 是一個「角色/prompt 包裝層」，底層真正跑推論的是本機 Ollama 的 `gemma4:latest`。
- **切換怎麼接最乾淨**：因為三層 fallback 的程式介面已經存在（`_claude_ask_raw` / `hermes_ask` / `ollama_direct_ask` 都是獨立函式，回傳統一的 `ModelResult`／字串），手動切換**不需要重寫呼叫邏輯**，只需要：
  - 加一個 per-chat 的「強制模式」狀態（記憶體 dict 或寫進現有 `conv_history.json` 旁邊一個小 state 檔即可，不需要新資料庫）。
  - 加 `/model` 指令讀寫這個狀態。
  - `claude_ask_with_fallback()` 開頭多一個判斷：強制模式是 `hermes` 就跳過 Claude 直接走 `hermes_ask`；是 `claude` 就忽略 fallback 規則（即使分類成 quota 也不切，讓 Owner 自己決定要不要等 Claude 恢復）。
  - 這跟現有 `MAPLAB_FORCE_HERMES_FALLBACK` 環境變數是同一條邏輯路徑的延伸，不是新架構。
- **訓練資料現況**：目前**沒有**任何結構化、可直接拿去微調的資料。現有的是：
  - `data/telegram-logs/{date}.md`——人類可讀的 markdown 對話紀錄，每筆只有 `owner_msg` / `bot_reply` 文字，**沒有標記是 Claude 還是 Hermes 回的**（除非回覆文字本身包含 receipt，但那是文字混在內容裡，不是結構化欄位）。
  - `bot/conv_history.json`——只保留每個 chat 最近 20 則，是給 prompt context 用的滾動視窗，不是持久訓練語料（會被截斷覆寫）。
  - 兩者都會在每次對話後自動 `git add/commit/push origin main`（`git_commit_log_sync()`，[bot/bot.py:190](../../bot/bot.py)）——這是**既有行為**，不是我這次做的事，但值得讓 Owner知道：目前每一句 Telegram 對話內容都會自動進 public repo 的 git history。
  - 結論：「訓練 Hermes」要做的最小事情，是新增一個 jsonl 紀錄器（例如 `data/hermes-training/{date}.jsonl`），每筆寫 `{timestamp, chat_id, user_message, model_used: claude|hermes|ollama_direct, answer, failure_kind}`，純粹是在現有 `_record_history` / `log_conversation` 旁邊多寫一行 append，不動既有邏輯、不影響現在的 markdown log。**不建議**現階段做自動微調 pipeline——先把資料存對格式，之後要訓練時再做，避免過度工程。

## 8. 風險與安全檢查

- 沒有讀取或印出 `bot/.env`、任何 token、API key 內容；只確認 key 是否存在。
- 沒有對 Telegram 發送任何測試訊息（會在 Owner 的真實對話紀錄留下痕跡，視為有外部可見副作用，超出本輪只讀授權）。
- 沒有重啟、reload 或修改 `com.maplab.telegrambot` launchd 服務或 `bot/.env`。
- 沒有把 Hermes/Ollama 的任何輸出內容當作事實使用——本報告引用的 Hermes 輸出（第 5 節）只作為「fallback 鏈失敗」的證據，不是引用其回答內容當結論。
- 唯一執行的程式碼是 `python3 -m py_compile bot/bot.py bot/test_hermes_fallback.py` 與既有 mock 測試 `bot/venv/bin/python3 -m unittest test_hermes_fallback`（22 passed），兩者都不連網、不碰真實 Claude/Hermes/Ollama、不寫入 repo 以外的東西。

## 9. 建議的 Phase 2 範圍（等 Owner 確認後才做）

依今天查到的事實排序，建議優先序是：

1. **先補「fallback 全敗時的人話收尾」**——風險最低、影響最直接，修的是已經存在、今天就真實壞過一次的路徑（`ollama_direct_ask` 回空字串時的處理）。
2. **加 `/model claude|hermes|status` 手動切換指令**——這才是 Owner 這次主要要的東西，但實作前需要 Owner 確認：手動切到 Hermes 時，要不要也限制電腦控制能力（目前 fallback receipt 已經有「only read/draft/smoke/image-analysis」這條線，手動模式應該沿用同一條線，而不是讓 Owner 手動切換時意外解鎖更高權限）。
3. **加結構化訓練 jsonl 記錄器**——低風險、純 additive，但需要 Owner 確認要不要存（畢竟現在對話內容已經自動 push 進 public repo 的 git history，多一份 jsonl 只是換格式，不是新的隱私風險，但還是要明確同意）。

不在這次 Phase 2 建議範圍內（風險高/需要更多資訊才能動）：

- 修「log 停寫 12 小時」這個操作面問題——建議 Owner 先用 `/ping` 確認 bot 現在到底活不活，再決定要不要重啟服務；重啟服務本身屬於會中斷現有服務的動作，需要 Owner 明確同意才做。
- 清理 `bot/bot.py` docstring 與 `bot/DEPRECATED.md` 過期內容——純文件債，優先度低，可以晚點一起做。

## 10. Resume Prompt

```text
我是接續 Telegram @maplab_claude_bot Claude/Hermes 切換需求的下一位 agent。
Phase 1（只讀調查）已完成，bundle：workbook/reviews/JOB-B1-BUILDER-20260620/phase1_investigation_report.md

關鍵事實：
1. 自動 Claude→Hermes fallback 已經存在並上線（2026-06-17, commits cffcab6/07a5261/877af04/9f84998），
   不是新功能。三層：Claude CLI -> hermes CLI(gemma4:latest) -> Ollama 直連(同一顆 gemma4:latest)。
2. 沒有手動 /model 切換指令，只有環境變數 MAPLAB_FORCE_HERMES_FALLBACK（需重啟才生效）。
3. 今天 2026-06-20 08:18 真實發生過一次三層全敗（data/telegram-logs/2026-06-20.md），
   Owner 只收到錯誤訊息，沒有人話收尾。
4. bot.log/launchd_stdout/stderr 從今天 08:53 起完全沒有新紀錄，但 PID 1344 目前有 ESTABLISHED
   連線到 Telegram——log 停寫原因未查清，建議先請 Owner /ping 確認 bot 是否還在正常回應。
5. 沒有任何結構化訓練資料（只有 markdown log + 20 則滾動 deque），要訓練 Hermes 需先加 jsonl 記錄器。

下一步（等 Owner 從 Phase 2 建議的 3 項裡選要做哪些、確認手動模式的權限邊界後才動手）：
- 若要做，先修 ollama_direct_ask 全敗時的收尾，再加 /model 指令，最後才加訓練 jsonl。
- 任何實作都要 python_compile + 跑 bot/test_hermes_fallback.py 既有 22 個 mock test 確保不退步，
  並補新行為的 mock test。
- 不要 reload/restart launchd 服務，除非 Owner 明確同意（會中斷正在跑的 bot）。
- 不要把 hermes/ollama 的輸出當事實，只能當「這條路徑有沒有回應」的證據。
```
