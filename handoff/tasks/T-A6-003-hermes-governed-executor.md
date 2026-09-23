+# T-A6-003 — Hermes Telegram 治理式執行器

- **狀態**：🟡 V2 PRIVATE＋PHOTO LIVE VERIFIED；群組 mention/reply 程式與測試 PASS，現有 Owner 群 live eye proof 待補
- Owner 需求：Hermes 在 Telegram 收到自然語句後能自己動手，不只答疑；能收照片；Owner 在群組提及後要看得到、會回覆、會開工。
- 版本邊界：sender 為 Owner 才授權；群組需 @bot 或回覆 bot；固定 argv 白名單；每次建立 task/receipt；禁止任意 shell。

## V2 改了什麼

1. 能力問題改走 deterministic runtime readback，不再由免費模型猜：
   - A6 gateway 不是零存取。
   - provider chain、最近成功 provider、持久對話路徑都可查。
   - 明確區分 gateway 能力、模型能力、Hermes Agent 原生 runtime。
2. 自然語句可直接執行安全動作，不再強迫 Owner 記 `/do`：
   - `runtime-status`
   - `signal-status`
   - `repo-status`
   - `recent-commits`
   - `a6-self-test`
3. `signal-status` 真讀 `launchctl` 與最新報告 mtime；手冊舊快照不能冒充 current。
4. 授權由 `message.from.id` 判斷，不再拿 group chat id 跟 Owner user id 比；Owner 在群組 @bot 或回覆 bot 可用。
5. Telegram 照片會下載到 owner-only inbox，建立 bytes／sha256／路徑 receipt；v2 不假裝有視覺理解。
6. 舊 `bot_a6/hermes_conv.json` 隔離到 private runtime quarantine，新對話從乾淨 v2 history 開始。
7. 對話、照片、state、log 一律 0600，runtime/task 目錄 0700；log 只記字數與 message hash，不再寫 Owner 明文。
8. repo 與 `~/.hermes` runbook／SOUL 已教育為 capability truth；刪除「等 Fable5/Codex 額度」這種假阻塞。

## 治理邊界

- Telegram 文字永遠不送進 shell。
- action 只映射到程式內固定 argv。
- 下單、買賣、轉帳、發布、WordPress、密鑰/token、刪除、券商與排程修改一律 fail closed。
- 允許唯讀查 launchd 狀態；禁止修改、重啟、載入或卸載排程。
- 未知任務拒絕並列出支援動作；不得由 LLM 自行發明工具。
- A6 gateway 無 Sheets／Drive／GitHub API 直連；不得因此誤稱本機零存取。
- 投資狀態必須來自 runtime readback 或新 receipt，不得靠舊手冊推測。

## 驗證

- `python -m unittest tests.test_hermes_task_executor tests.test_hermes_capability_runtime tests.test_hermes_telegram_gateway -v`：14/14 PASS。
- `py_compile`：PASS。
- 兩份 launchd plist `plutil -lint`：PASS；installed service readback 顯示 `state=running`、`pid=3376`、`umask=77`。
- 舊對話已隔離：`~/.local/share/maplab-a6-hermes/quarantine/legacy-conversation-20260826-181225.json`；conversation/quarantine 檔案均 0600。
- Telegram Web 2026-08-26 18:14 實送能力問題，回覆 `【hermes】能力真相 v2（runtime readback）`，明確含「不是零存取」、provider chain、跨重啟 12 則記憶與固定動作。
- Telegram Web 2026-08-26 18:14 實送自然語句「現在動能名單狀態如何？請直接查，不要叫我跑終端機。」；回覆 `completed`，task id `A6H-20260826-181433-26d05c`。
- 同 id 本機 receipt 存在，`status=completed`、`action=signal-status`、`returncode=0`；真相為 launchd `not running`、`runs=18`、`last_exit=1`，最新報告日期 2026-05-22，不能當今日名單。
- Telegram Web 2026-08-26 18:24 實傳 5,354-byte 非敏感測試 PNG；同一視窗回覆「照片已收到並私密留檔」，receipt `~/.local/share/maplab-a6-hermes/inbox/tg-493-AQADrhBrG1TacVR-.receipt.json`。本機 image/receipt 均為 0600，bytes=5354，SHA-256 `8f96cb8c1a6c6e856e5eed1543657010a9e11f0d0cd78ef350f30c8c7eb5e386` 與 Telegram readback 一致。

## Receipt

`workbook/reviews/JOB-A6-HERMES-V2-20260826/validation_receipt.md`

Implementation commit: `9639178` (`fix(A6): make Hermes execute and receive photos`).

## Resume Prompt

我是 A6 Hermes v2 接手者，環境是 `/Users/pagemacmini/maplab-ai-handbook`，任務只剩群組 live eye proof。先讀 `AGENT_CORE.md`（若存在）、`CURRENT_STATUS.md`、`pitfalls.md`、本卡與 `handoff/HERMES_TAKEOVER_RUNBOOK_20260825.md`。先確認 `com.maplab.a6bot` 仍在跑 `bot_a6/hermes_telegram_gateway.py`，不要重寫已通過的 private/photo 路徑。群組驗證只能使用 Owner 指定的測試群；確認 bot 已在群內，再由 Owner 帳號 @bot 說「幫我查 Hermes runtime 狀態」，必須得到同群回覆與 matching `A6H-*` receipt。不要讓 bot 回覆非 Owner，不要另建群或打擾生產群，不要測下單／發布／密鑰／排程修改。
