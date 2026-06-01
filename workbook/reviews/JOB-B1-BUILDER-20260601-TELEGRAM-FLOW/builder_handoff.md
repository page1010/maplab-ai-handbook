# Builder Handoff

## What Changed

B1 fixed one concrete Telegram flow: Convergence now has separate outputs for
machine-readable/file-backed evidence and owner-facing phone conversation.

Before:

- `data/convergence_all.md` full report was also sent to Telegram.
- Phone first screen included matrix rows, prompt file paths, and training/debug
  context.

After:

- Full report remains in `data/convergence_all.md` and `reviews/`.
- Telegram sends a short `[Investment OS | 即時共振 | research_only]` card:
  What / So what / Next / Evidence.
- The card explicitly says watch/monitor only and no broker/order action.

## Agent Division

- Codex/B1: repo implementation, tests, runtime sync, status/task-card writeback.
- OpenClaw: read-only Telegram Web readback after next runtime send.
- Hermes/local model: file-only readability review from saved report/card.
- B2 Reviewer: inspect gateway metadata, freshness, allowlist coverage, and
  direct sender bypasses.
- B3 Archivist: archive the next live readback evidence and update resume prompt.
- B4 System Patrol: decide if Convergence frequency/threshold should remain
  Telegram-visible or move to dashboard unless threshold is met.

## Next Resume Prompt

我是 Codex/B1，環境 `/Users/pagemacmini/Documents/New project`，任務是驗證
Convergence Telegram short-card runtime surface。先讀 `AGENT_CORE.md`、
`CURRENT_STATUS.md`、`pitfalls.md`、`tasks/TELEGRAM_SEND_PATH_CONTROL_PLANE_20260529.md`、
`tasks/CONVERGENCE_SHADOW_TRAINING_TELEGRAM_20260528.md`。

已完成：`scripts/run_convergence_engine.py` 將 full report 與 Telegram card 分離，
runtime copy 已同步，targeted tests passed。下一步不要讀 secrets、不要發 spam、
不要碰 broker/order；等下一次自然 runtime all-run 或 Owner 明確授權 trigger 後，
用 Telegram Web read-only 確認 `@page_trading_bot` 收到的是 short card。

## Still Open

- `telegram_notify.py` gateway metadata contract enforcement.
- Direct Bot API allowlist enforcement test.
- File receipts for OpenClaw/Hermes readability branches.
- Live Telegram Web readback after the next token-bearing runtime send.

