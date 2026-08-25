# T-A6-003 — Hermes Telegram 治理式執行器

- 狀態：✅ IMPLEMENTED / 待 Telegram Web 真實 roundtrip
- Owner 需求：A6 Hermes 收到指令後能動手，不只答疑。
- 版本邊界：Owner-only、固定 argv 白名單、每次建立 task/receipt；禁止任意 shell。

## 這版改什麼

1. `/do repo-status`：唯讀 repo dirty-state 摘要。
2. `/do recent-commits`：唯讀最近八筆 commit。
3. `/do a6-self-test`：執行 executor focused unittest。
4. `執行：...`、`動手：...` 可作中文入口。
5. 每次 accepted/rejected request 都寫入 `workbook/reviews/A6-HERMES-TASKS/<task-id>/`。

## 治理邊界

- Telegram 文字永遠不送進 shell。
- action 只映射到程式內固定 argv。
- 下單、買賣、轉帳、發布、WordPress、launchd/cron、密鑰/token、刪除、券商關鍵字一律 fail closed。
- 未知任務拒絕並列出支援動作；不得由 LLM 自行發明工具。
- 不讀 `.env`、不改排程、不做外部寫入。

## 驗證

- `python -m unittest tests.test_hermes_task_executor -v`：4/4 PASS。
- `py_compile`：PASS。
- `git diff --check`：PASS。
- 本機真實 worker receipt：`workbook/reviews/A6-HERMES-TASKS/A6H-20260825-204904-bcf1c5/receipt.json`。

## Resume Prompt

我是 A6 runtime 接手者。先讀 `CURRENT_STATUS.md`、`AGENT_CORE.md`（若存在）、`pitfalls.md` 與本卡。檢查 `com.maplab.a6bot` 是否運行新版 `bot_a6/hermes_telegram_gateway.py`。使用已登入 Telegram Web 對 `@maplab_a6_bot` 發 `/start`，確認 help 包含 `/do`；再發 `/do recent-commits`。必須同時取得 Telegram 可讀回覆與 `workbook/reviews/A6-HERMES-TASKS/<task-id>/receipt.json`，兩者 task id 相同才可把狀態升為 ROUNDTRIP_VERIFIED。不可測試發布、下單、密鑰或排程操作；高風險只可用 unit test 驗 fail-closed，不要在 Telegram 實送敏感字串。若要新增能力，逐項增加固定 argv Action 與測試，不得加入通用 shell/exec。
