# Reactivation Status — JOB-B4-RADAR-RECOVERY-20260606

## Status

PARTIAL REACTIVATED.

## What Is Working

- Runtime convergence radar is active: launchd state `running`, `runs=254`, `last exit code=0`.
- Runtime `convergence_all.md` is fresh at `2026-06-06 21:31 Asia/Taipei`.
- `evaluate_risk.py` now reads radar BSI from the runtime report before the stale repo mirror.
- Public market signal fetch works locally with network permission.
- 2026-06-05 dry-run correctly produces `BLACK_SWAN`, `score=13`, `crisis_type=EPISODIC`.
- `evaluate_reentry.py` returns staged re-entry gates and blocks add-back on event day +1.

## What Is Not Yet Live

- `openclaw_tasks/cron.yml` is explicitly marked orphan/superseded in the repo and is not the live schedule source.
- The new black-swan risk engine is implemented and tested in repo, but it has not yet been registered in `scripts/run_invest_os_background_job.py` or a launchd plist.
- The smoke used `/private/tmp/investos_black_swan_smoke.sqlite3`, not the production runtime DB.
- No Telegram live alert was sent in this task.

## Next Safe Activation Step

Register a new dispatcher job for the risk engine after review:

1. Add `fetch-market-signals`, `evaluate-risk-postmarket`, `evaluate-risk-preopen`, and `evaluate-risk-intraday` or one combined `black-swan-risk-engine` command to `scripts/run_invest_os_background_job.py`.
2. Add launchd plist schedule or extend an existing supervised job; do not rely on `openclaw_tasks/cron.yml`.
3. Run acceptance chain: `py_compile -> focused pytest -> runtime scoped sync -> wrapper no-send dry-run -> job state proof -> Telegram readback only after approval`.

## Resume Prompt

我是 B1 Builder 或 B4 System Patrol。先讀 Investment OS `AGENT_CORE.md`、`CURRENT_STATUS.md`、`pitfalls.md`、`docs/TASK_CARD_PROTOCOL.md`，再讀 MAPLAB `CURRENT_STATUS.md` / `pitfalls.md`。本輪已完成 repo 實作：`scripts/fetch_market_signals.py`、`scripts/evaluate_risk.py`、`scripts/evaluate_reentry.py`、`schemas/003_risk_engine.sql`、`tests/test_black_swan_engine.py`。下一步是把 risk engine 接進 Investment OS live dispatcher/launchd；不要用 orphan `openclaw_tasks/cron.yml` 當 live proof。先用 `/private/tmp` 或 `--dry-run` 驗證，未經 Owner 批准不要發 Telegram、不寫 production runtime DB、不碰 broker/order。
