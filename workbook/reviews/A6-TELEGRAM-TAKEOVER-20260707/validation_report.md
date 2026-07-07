# A6 Telegram Takeover / Route Guard Validation — 2026-07-07

## Scope

- Runtime target: Chrome Telegram Web chat `maplab_a6_bot`
- Repo: `/Users/pagemacmini/maplab-ai-handbook`
- Runtime label: `com.maplab.a6bot`
- Change scope: A6 Telegram route guard, takeover handoff command, non-quote photo fallback text, local quote mobile summary
- Out of scope: LINE webhook, GAS formula logic, Google Sheet structure, secrets

## Chrome Telegram Observations

Recent visible conversation before the fix showed four actionable issues:

1. `22:16` / `22:17` Owner asked: `我在這裡請你報價 有訓練到ollama 嗎 有一天出地端專用迷你模型的做法的時候可以把工作流拿給他用嗎？`
   - A6 replied with `A6 runtime 狀態`, because the status detector matched `ollama` / `模型` inside a broad workflow question.
2. `21:16` a photo-related path reached the old Claude CLI path and surfaced `找不到 claude 命令`.
   - This is not a useful Telegram-facing recovery path for A6 users.
3. The chat window had no first-class handoff command.
   - A next Codex session had to infer state from chat plus repo files instead of receiving a copyable takeover packet.
4. A prior `15人有主食高毛利 要英文菜單` local quote result in A6 memory showed only the local fallback footer.
   - Telegram did not get a usable quote summary.

## Fixes

- Narrowed `_looks_like_runtime_status_request()` so explicit `/status`, `/model`, short model-status questions, and short runtime-status phrases still work, but long workflow questions mentioning `ollama` no longer become status.
- Added `/takeover`, `/handoff`, text triggers like `接手`, and a `🧭 接手包` keyboard button.
- Added `_render_takeover_packet()` with repo, launchd runtime, cold-start files, routing rule, and recent local memory.
- Changed non-quote photo handling to return a safe image handoff message with the saved local path and `/takeover` path instead of calling the old Claude CLI path.
- Added `_prepare_local_quote_answer()` so `/localquote` and local fallback can present a deterministic Sheet-first summary when the local model output is empty, footer-only, or JSON-heavy.
- Added `bot_a6/test_a6_telegram_routes.py` to lock the route guard, takeover packet, photo fallback, and localquote summary behavior.

## Verification

Local checks:

```text
bot/venv/bin/python -m py_compile bot_a6/bot_a6.py bot_a6/a5_quote_engine.py bot_a6/test_a6_telegram_routes.py
bot/venv/bin/python bot_a6/test_a6_telegram_routes.py
✅ A6 Telegram route tests passed.
```

Runtime restart:

```text
launchctl kickstart -k gui/501/com.maplab.a6bot
launchctl list: PID 29067, status 0, label com.maplab.a6bot
stdout: 2026-07-07 23:28:06 A6 Bot running
```

Chrome Telegram readback:

```text
23:38 /takeover
23:38 A6 接手包 repo：/Users/pagemacmini/maplab-ai-handbook
     runtime：launchd `com.maplab.a6bot` / `bot_a6/bot_a6.py`
     contains copyable Codex startup and recent local memory

23:39 我在這裡請你報價 有訓練到ollama 嗎 有一天出地端專用迷你模型的做法的時候可以把工作流拿給他用嗎？
23:39 A6 Codex 處理中…
23:39 A6 answered the workflow/model-training question directly and did not return `A6 runtime 狀態`.

23:46 /localquote 15人有主食高毛利 要英文菜單
23:46 A5 本地備援測試：不寫 Google Sheet。
23:47 A5 Sheet-first 報價試算 ... 總金額 NT$15,700｜訂單成本 NT$3,140｜毛利率 80.00%
     includes `/localquote` is test mode and no Google Sheet write
```

## Remaining Notes

- I did not upload a new photo into Telegram during this validation. The code path and unit test now prove non-quote photos no longer surface the old `找不到 claude` error; next real photo message should return the new handoff text.
- `CURRENT_STATUS.md` already had unrelated dirty changes before this fix, so this receipt and `handoff/tasks/T-A6-001.md` carry the durable record for this scoped commit.

## Resume Prompt

```text
我是 MAPLAB A6 Telegram/runtime 接手代理，環境 Mac mini Codex + Chrome Telegram Web，任務是延續 A6 bot 修復。
repo: /Users/pagemacmini/maplab-ai-handbook

先讀：
1. CURRENT_STATUS.md
2. handoff/tasks/T-A6-001.md
3. pitfalls.md
4. workbook/reviews/A6-TELEGRAM-TAKEOVER-20260707/validation_report.md
5. bot_a6/bot_a6.py

最新已完成：
- A6 runtime/status 意圖收斂，長句提到 ollama/模型不再自動回 /status。
- 新增 /takeover / /handoff / 接手包 keyboard，Telegram 可直接產 Codex 接手包。
- 非報價圖片不再走舊 Claude CLI 裸錯，改回可接手圖片路徑與下一步。
- /localquote 15人高毛利英文菜單 Chrome readback 已回手機可讀摘要，不寫 Google Sheet。

驗證：
- py_compile passed
- bot_a6/test_a6_telegram_routes.py passed
- launchctl com.maplab.a6bot PID 29067 running
- Chrome Telegram /takeover, 誤判長句, /localquote 三項 readback passed

下一步：
- 若 Owner 再傳圖片，驗證實際 photo handoff 文案。
- 若要把接手包升級成真正 dispatch queue，再開新 task card，不要塞進這次 bot hotfix。
```
