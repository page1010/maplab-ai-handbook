# T-A1-QUOTA-VALUE-CYCLE-001 — 訂閱額度價值複利閉環

## 接續狀態

- **狀態**: ✅ COMPLETED
- **最後活動**: 2026-07-31
- **接續點**: 等待 2026-08-04 09:00 第一個 MAPLAB value sprint；重置後核對 Owner report。
- **阻塞**: Claude／Gemini 訂閱剩餘量沒有可信機器端來源，維持 `unknown`；不得因此偽造百分比。
- **assigned_session**: 2026-07-31 / Mac mini Remote Codex
- **last_committed_by**: Codex（2026-07-31，scoped commit 見 validation report）

## 目標

把 Owner 的規則落成可執行閉環：

1. 不用 AI 額度的本機 watcher 持續記錄可信 Codex rate-limit snapshot。
2. 距重置 36 小時內、且保留 15% 安全額度後仍有餘裕，才啟動價值衝刺。
3. MAPLAB 與 Investment OS 每輪優先做一個對 Owner 有直接幫助、能形成大步推進的垂直切片。
4. `inventory/checkpoint/no_delta` 不得偽裝成果；相同 revision 七天內不重複消耗。
5. 每個成功 job 必須有 output path、tests、scoped commit 與 receipt。
6. 重置後自動彙整報告並把可點擊連結交回 Owner。

## 本版變更

- `local_model_evolution/bin/quota_value_cycle.py`
  - `snapshot`：只讀 Codex `token_count.rate_limits`，不保留對話內容。
  - `plan`：安全額度 gate、36 小時 activation window、價值評分、重複熔斷。
  - `record`：`done` 強制至少一個 output receipt。
  - `report`：依額度週期彙整成果、測試、commit 與 quota evidence。
  - `doctor`：驗證 config、session telemetry、candidate evidence。
- `local_model_evolution/config/value_backlog.json`
  - 初始 MAPLAB／Investment OS 高價值候選與驗收界線。
- 本機 LaunchAgent
  - 每小時只跑 deterministic snapshot，不呼叫模型、不消耗 AI 額度。
- Codex automations
  - 重置前 MAPLAB 衝刺。
  - 重置前 Investment OS 衝刺。
  - 重置後跨專案報告。

## 安全邊界

- 不讀 secret value、cookie、`.env`、broker credential。
- 不送 Telegram、不改廣告、不寫 WordPress、不碰 broker/order。
- 不 merge/push，不覆蓋 canonical dirty files。
- 自動衝刺在 Codex worktree 內做 scoped changes；測試失敗不得記 `done`。
- 額度訊號 `unknown`、安全額度不足或不在 activation window 時必須停止。

## 驗收

- [x] `python3 -m unittest local_model_evolution/tests/test_quota_value_cycle.py` — 7 tests PASS。
- [x] `python3 -m py_compile local_model_evolution/bin/quota_value_cycle.py`。
- [x] `quota_value_cycle.py doctor` PASS。
- [x] `quota_value_cycle.py snapshot` 讀到 `limit_id=codex`、used/reset/source receipt。
- [x] LaunchAgent 已載入，2 runs，last exit code 0。
- [x] 三條 Codex automations 都是 ACTIVE + worktree，時間與 prompt 邊界正確。
- [x] `workbook/reviews/JOB-QUOTA-VALUE-CYCLE-20260731/validation_report.md`。

## Resume Prompt

我是接手 T-A1-QUOTA-VALUE-CYCLE-001 的 A1/Codex。先讀 `CURRENT_STATUS.md`、
`pitfalls.md`、本卡、`local_model_evolution/state/STATE.md`、
`local_model_evolution/config/value_backlog.json` 與
`local_model_evolution/bin/quota_value_cycle.py`。

上次做到：額度快照、價值選題、重複熔斷、receipt 與週期報告已落成同一個
deterministic controller；不得再用重複 checkpoint 假裝複利成果。

下一步：先跑 task card 驗收命令，再檢查 LaunchAgent 與三條 Codex automation
runtime readback。成功判準不是「排程存在」，而是 snapshot 有可信 source、
pre-reset job 有 output/tests/commit receipt、post-reset report 有 Owner 可點擊連結。

禁止：不得讀 secrets、不得傳訊、不得外部 mutation、不得碰 broker/order、
不得把 `unknown` quota 猜成百分比。
