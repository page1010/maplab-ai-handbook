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


---

## 🔒 Owner 已批准的收尾變更（MUST-DO，2026-07-31 加註）— LOCK 到本卡

> 加註者：Cowork 查證員。狀態：卡已 ✅ COMPLETED 且核心機制已 commit（`11b7a4c feat(a1): close quota value cycle`），
> 但以下 5 項是 Owner 事後明確批准的收尾，**尚未套用**。下一個承接本卡的 session 必須套用後再 commit。
> **LOCK**：本卡由單一 session 承接套用這 5 項，避免多 agent 平行改（本輪查證時 repo working tree 曾在 2 分鐘內被別的 session 切換分支，故不做平行 commit）。

### 事實更正（先記，免得照錯前提重做）
- **真實重置日 = 週三**：Codex telemetry `resets_at` = **2026-08-05 12:49 台北**（weekly 視窗 10080min，plan_type=prolite）。**不是** Owner 記憶的「週四 / 07-30」。週三檢查 + 重置後報告的排程對齊此。
- **Fable 5 / Claude 訂閱額度不可程式讀**：只有 Codex 餘量可從 `~/.codex/sessions/*.jsonl` rate_limits 讀到。任何「Fable 額度足夠才跑」的 gate **一律用 Codex 餘量當 proxy**，不得偽造 Claude/Fable 百分比。
- 現況實測：Codex 已用 6% / 剩 94% / 距重置約 118h → 目前 `outside_activation_window`，今天不會自動消耗。

### 5 項 MUST-DO
1. **高階優化改用 Fable 5**：兩條 value sprint 的「實作/優化」步驟改由 `claude --model claude-fable-5 -p "…"` 執行（Codex 仍負責便宜的 plan/gate/record；Fable 5 只做高槓桿的檢查與優化）。**不要**把 Codex automation 的 `model` 欄位直接改成 claude 值（會弄壞 Codex runner）——是在 sprint prompt 內 shell out 到 claude CLI。啟動開關用 Codex 餘量 proxy。
2. **加「消耗前通知、沒回應默認跑」gate**：sprint 在 `gate=ready`、真正開始消耗前，先用 `scripts/notify_owner.sh` 發 Telegram：「準備開始消耗額度做 X，N 分鐘內未回覆將默認開跑」；等待 N 分鐘，**除非 Owner 明確喊停，否則默認開跑**。為此**放寬本自動化的 Telegram 禁令**（僅允許這一則 outbound 通知；其餘 broker/WordPress/廣告/secrets 禁令不變）。
3. **投資候選補上**：在 `local_model_evolution/config/value_backlog.json` 新增一個高優先 `investment-os` 候選：「股票回報 / 投資策略演進（接 risk-master v1、部位、大盤路徑）」，owner_value/step_change 給高分，evidence 指向真實存在的檔（先確認路徑存在，否則 `doctor` 會 fail）。
4. **排程對齊週三重置**：確認 pre-reset sprint 落在重置前 36h 窗內、post-reset report 在週三重置後（現況：sprint 週二/週三 09:00、report 週三 13:30，與 08-05 週三重置吻合）。以 telemetry 為準，非「週四」。
5. **套用後 scoped commit**：只動這條相關檔（value_backlog.json、兩條 sprint automation.toml、本卡），乾淨分支、不碰別 session 的 dirty worktree、不 push/merge。

### 未變更的守則
不讀 secrets/.env/cookies；除第 2 項的單一通知外不送 Telegram；不碰 broker/order；額度 `unknown` 不猜百分比；no_delta 不偽裝成果、同 revision 7 天不重跑。
