# B1 Builder — 2026-06-24 Implementation Plan

## Role
B1 Investment OS Builder

## Dispatch Source
Owner Telegram dispatch 2026-06-24（今日額度刷新後交辦）

## Scope
1. 確認 Chrome Extension B1 快速召喚同步狀態
2. 取回上一次 dispatch 紀錄
3. 推進 T-HQ-001 P5（data-policy 落地：log rotate + archive 壓縮）
4. 推進 T-HQ-001 P6（Hermes 記憶啟用 + A7 LINE JSONL export）

## Findings on Dispatch Records

- `workbook/telegram-dispatch/` 目錄不存在於 repo — 2026-06-17 已實作 dispatch receipt 機制（commits 9f84998/877af04），但尚未有真實 TG-DISPATCH-* 目錄落地（Owner 在 Telegram 送出召喚時才會建立）。
- 上一次 "Maplab supervision resume" session 有未 commit 的變更（hermes patrol history、A2 SEO plan、A8 update_checklist.py、JOB-A8-EVENT assets），均為其他角色域，B1 不代為處理。
- 上一次 B1 工作：JOB-B1-BUILDER-20260620 調查 @maplab_claude_bot Claude/Hermes 手動切換，Phase 1 only read — Phase 2（`/model` 指令）已由 A1 於 2026-06-22 實作（commit 4564c5f）。

## Findings on Extension Sync

| 指標 | 狀態 |
|------|------|
| B1.json 上次產生 | 2026-06-20T20:39:40 |
| 本次重建 | 2026-06-24T22:53:32 |
| CURRENT_STATUS.md | 52,507B → 73,250B (+40%) |
| AGENT_RULES.md | 42,958B → 47,470B (+10%) |
| pitfalls.md | 46,189B → 47,784B |
| TASK_QUEUE.md | 之前不存在 → 現存在 |
| module_source_state | NOT SET（未設此欄位）|
| **結論** | **stale → 已更新（本次 build script 重建）** |

A6.json 最明顯：新增了 `docs/data-locations.md` 至 read_first（是真實內容變化，非只是 hash）。其他模組主要是 SHA256/size 更新反映文件成長。

## T-HQ-001 P5 Plan

**目標**：log rotate + archive 壓縮 launchd job

步驟：
1. 新增 `scripts/data-policy.md`（保留規則文件）
2. 新增 `scripts/log_rotate.sh`（rotate bot/data/hermes logs > 10MB）
3. 新增 `runtime/launchd/com.maplab.log-rotate.plist`（weekly launchd job）
4. py_compile / shell syntax check 驗證
5. 說明 Owner 啟用步驟（launchctl load）

## T-HQ-001 P6 Plan

**目標**：Hermes 記憶啟用 + A7 LINE JSONL export

步驟：
1. 新增 `scripts/hermes_memory_prompt.md`（Hermes 任務結束後寫記憶的 SOP prompt）
2. 新增 `scripts/export_a7_line_jsonl.py`（讀 case_store SQLite → 輸出 JSONL）
3. 新增 `scripts/a7_line_export_cron.sh`（每晚 23:50 執行 export）
4. 新增 `runtime/launchd/com.maplab.a7-line-export.plist`（launchd daily job）
5. JSON validation / py_compile 驗證

## Guardrails
- 不讀 secrets / .env
- 不碰 broker/runtime 高風險 surface
- 不 push main
- 只改 scope 內檔案
