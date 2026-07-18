# T-A1-LEARNING-LOOP-001 — MAPLAB Learning Loop v0 Reaction Ledger

## 接續狀態
- **狀態**: 🔄 進行中（P1 reaction ledger 已落地；P2 token capital registry / P3 eval harness 待做）
- **最後活動**: 2026-07-19 7efc03e
- **接續點**: 建立 token capital registry，登記可複用 prompt / eval / task packet / skill / pitfall；接著做 ledger closure/eval harness。
- **阻塞**: 無。Google OAuth reauth 是 `google-oauth-reauth-card` 的獨立 Owner 5 分鐘 action，不阻塞 ledger 機制。
- **assigned_session**: 2026-06-16 / A0 Dispatch Secretary + Codex
- **last_committed_by**: Codex（本輪待 commit）

建立：2026-06-16
負責：A1 / A0 Dispatch
依據：Owner 指示「先確認目前我們系統現況與這個描述差多少，哪裡有做哪裡沒做如何改進？打算怎麼改？」與「好 去做」。

## 目標

把 MAPLAB patrol 從「每天送出狀態」升級為「感測器 -> 初判 -> 分流 -> 執行 -> 人工確認 -> 失敗回收 -> 版本更新」。

## 已完成

- [x] P1: `tools/hermes_patrol_bridge.py` 產生 `workbook/learning_loop/reaction_ledger.jsonl`。
- [x] P1: 每張 reaction card 自動分成 `owner_5min` / `direct_do` / `delegated` / `memory_candidate` / `closed`。
- [x] P1: `workbook/learning_loop/reaction_ledger_summary.md` 顯示 open、stale、overdue 與決策統計。
- [x] P1: `workbook/hermes/patrol/latest.md` 和 Telegram card 顯示 ledger 指標。

## 待做

- [ ] P2: Token capital registry。欄位至少包含 asset_id、asset_type、owner_role、source_path、eval_status、last_used_at、promotion_rule。
- [ ] P3: Ledger eval harness。每日檢查 open reaction 是否逾期、是否已回寫 task card、是否符合三層阻塞審查。
- [ ] P4: Closure writer。完成後能用證據把 ledger row 關閉，並保留 closed_at / closure_evidence。

## 驗收

- 跑 `rtk python3 tools/hermes_patrol_bridge.py --repo /Users/pagemacmini/maplab-ai-handbook --raw-text-file logs/patrol-scheduled.log` 後，會更新 ledger 與 summary。
- Ledger 中不能只有「提醒 Owner」；至少要能分出 direct-do / delegated / owner_5min。
- 7 天以上未關閉 reaction 必須被 task card 或 `pitfalls.md` 回收，不可只留在 Telegram 訊息。
- **Verification（主觀任務）**：`workbook/hermes/patrol/telegram_decision_card.md` 的文案品質（資訊密度/格式一致/措辭安全/資料層級透明）依 `rubrics/telegram-digest-quality.md` 評分，不是 agent 自己判斷「看起來還行」。

## Resume Prompt

我是 A1/Codex。請先讀 `CURRENT_STATUS.md`、`pitfalls.md`、`handoff/tasks/T-A1-LEARNING-LOOP-001.md`、`workbook/learning_loop/README.md`、`workbook/learning_loop/reaction_ledger_summary.md`。
下一步是做 P2 token capital registry：設計 `workbook/learning_loop/token_capital_registry.jsonl` schema，登記現有 `skills/`、`workbook/hermes/patrol/hermes_prompt.md`、A0 issue #14 的 prompt/packet 資產，並加一個 summary 檢查哪些資產還沒有 eval_status。
