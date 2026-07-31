# Quota Value Cycle v1 — Validation Report

> Date: 2026-07-31 Asia/Taipei  
> Role: Mac mini Remote Codex / system compounding and quota governance  
> Scope: deterministic quota telemetry, value-job gate, receipts, pre-reset sprints, post-reset report

## Outcome

PASS — 額度使用策略已從文件骨架變成可運行閉環。

本輪沒有為了證明「會消耗」而提前執行專案修改。真實 Codex snapshot 顯示距下一次
reset 尚有約 118.6 小時，超出 36 小時 activation window，因此 planner 正確輸出
`outside_activation_window`。第一次正式 value sprint 將在進入重置前視窗後執行。

## Implemented

1. `local_model_evolution/bin/quota_value_cycle.py`
   - 只解析 `token_count.rate_limits`，不保存 prompt/response。
   - 每小時 snapshot 不呼叫模型。
   - 36 小時 activation window。
   - 15% safe reserve。
   - Owner value / step change / readiness / risk 排序。
   - completed revision 不重跑；`no_delta` / `blocked` 七天 cooldown。
   - `done` 沒有 output receipt 會被拒絕。
   - current / previous cycle report。
2. `local_model_evolution/config/value_backlog.json`
   - MAPLAB 初始主線：A6 採用／修改／丟棄回覆閉環。
   - Investment OS 初始主線：Telegram direct Bot API fail-closed enforcement。
   - 需要外部 mutation 或 Owner 決策的廣告修改不會自動進場。
3. Runtime watcher
   - LaunchAgent: `com.maplab.quota-value-snapshot`
   - Interval: 3600 seconds
   - Runtime state: `/Users/pagemacmini/.codex/quota-value-cycle/`
4. Codex automations
   - `quota-value-sprint-maplab`：重置前 MAPLAB 高價值衝刺。
   - `quota-value-sprint-investment-os`：重置前 Investment OS 高價值衝刺。
   - `quota-value-cycle-post-reset-report`：重置後跨專案 Owner report。

## Runtime readback

- LaunchAgent state after RunAtLoad: `not running`（interval job 正常退出）
- LaunchAgent runs: `2`
- LaunchAgent last exit code: `0`
- Latest trusted lane: `limit_id=codex`
- Observed used: `6.0%`
- Observed remaining: `94.0%`
- Next reset: `2026-08-05T12:49:31+08:00`
- Evidence:
  `/Users/pagemacmini/.codex/sessions/2026/07/31/rollout-2026-07-31T13-07-28-019fb691-fbae-78e1-a1cc-f16eb9bad161.jsonl:63`
- Latest snapshot:
  `/Users/pagemacmini/.codex/quota-value-cycle/latest_snapshot.json`
- Current-cycle dry report:
  `/Users/pagemacmini/.codex/quota-value-cycle/reports/20260731-141517-current-cycle-report.md`

## Tests

- `python3 -m py_compile local_model_evolution/bin/quota_value_cycle.py` — PASS
- `python3 -m unittest local_model_evolution/tests/test_quota_value_cycle.py`
  — `7 tests`, PASS
- `quota_value_cycle.py doctor`
  — PASS, 4 candidates, 0 missing evidence paths
- `quota_value_cycle.py snapshot`
  — PASS, trusted source path + line recorded
- `quota_value_cycle.py plan --project all`
  — PASS, correctly gated `outside_activation_window`
- `plutil -lint com.maplab.quota-value-snapshot.plist`
  — PASS
- `launchctl print gui/501/com.maplab.quota-value-snapshot`
  — 2 runs, last exit code 0
- Three Codex automation config readbacks
  — ACTIVE + worktree execution

## Scheduled owner-visible cycle

- 2026-08-04 09:00 Asia/Taipei：MAPLAB value sprint。
- 2026-08-05 09:00 Asia/Taipei：Investment OS value sprint。
- 2026-08-05 13:30 Asia/Taipei：post-reset report。

每個 sprint 仍會先讀當下 quota snapshot；只有 gate=`ready` 才執行。時間表不是
繞過額度 gate 的授權。

## Safety

- Production mutation: false
- Telegram sent: false
- WordPress / Ads changed: false
- Broker / order touched: false
- Secrets read: false
- Push / merge performed: false
- Existing unrelated dirty files changed: false

## Resume Prompt

我是接手 Quota Value Cycle v1 的 Codex。先讀
`handoff/tasks/T-A1-QUOTA-VALUE-CYCLE-001.md`、本 validation report、
`local_model_evolution/config/value_backlog.json` 與 runtime
`/Users/pagemacmini/.codex/quota-value-cycle/latest_snapshot.json`。

先確認 LaunchAgent last exit code 0、三條 automations ACTIVE，再等 activation window。
任何 sprint 必須交 output/tests/commit receipt；沒有 material delta 就 record
`no_delta` 並停止，不得再用 checkpoint 數量代替 Owner utility。
