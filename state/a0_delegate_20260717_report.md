# A0 自主派工報告：監控排程去依賴化

**日期**：2026-07-17 14:10
**執行者**：A1 系統總管（Claude Code terminal）
**派工來源**：A0 Fable — 複利文化，根治工具缺口空跑

---

## 任務摘要

Cowork 排程 session 常因 Desktop Commander MCP 不可用而空跑（memory-watch / runtime 鬧鈴 / 備份）。本次將三個監控任務轉為 launchd 本機排程，脫離外部工具依賴。

---

## 交付清單

### 1. scripts/local_memory_watch.sh ✅
- **邏輯**：5 項檢查（Ollama 去抖 free≥12% / 非 Ollama free<20% / swap<5%+free<30% / Codex orphan超2個）
- **超標**：`scripts/notify_owner.sh` 推 Telegram
- **正常**：靜默寫 `state/memory_watch.log`（保留 7 天）
- **launchd**：`com.maplab.memory-watch.plist`（每 2 小時，`StartInterval: 7200`）

### 2. scripts/local_runtime_alarm.sh ✅
- **邏輯**：掃 `New project/state/runtime_escalation_queue.jsonl`，找 `status=open AND severity=CRITICAL`，去重後推 Telegram
- **launchd**：`com.maplab.runtime-alarm.plist`（每日 08:30，`StartCalendarInterval Hour:8 Minute:30`）

### 3. scripts/local_dispatch_backup.sh ✅
- **邏輯**：rsync 三個 repo（maplab-ai-handbook / agent-hq / New project）至 `~/maplab_backup/YYYYMMDD/`；os.walk 走訪建 INDEX（`state/dispatch_backup_index.json`）；保留 7 天
- **launchd**：`com.maplab.dispatch-backup.plist`（每日 03:00，`StartCalendarInterval Hour:3 Minute:0`）

### 4. 裝載與實測結果 ✅

```
launchctl load com.maplab.memory-watch   → ✅ loaded
launchctl load com.maplab.runtime-alarm  → ✅ loaded
launchctl load com.maplab.dispatch-backup → ✅ loaded
```

**memory-watch 手動觸發**（2026-07-17 14:08）：
- free=177MB(0%) + swap_free=884MB(6%) + ollama=true
- 觸發條件：Ollama 啟動中門檻 12%，RAM 0.7% free → 屬**真實告警**（非假門檻測試）
- Telegram 推播成功 ✅
- log 落地：`state/memory_watch.log` ✅

**runtime-alarm 手動觸發**（2026-07-17 14:09）：
- 1 筆 open CRITICAL：US 曝險 82.7%（deadline: 2026-07-17）
- Telegram 推播成功 ✅
- log 落地：`state/runtime_alarm.log` ✅

### 5. docs/local-monitoring-runbook.md ✅
記載三個任務的設計、管理指令（查看/手動觸發/卸載/重新裝載）、設計決策說明。

---

## 附加觀察（真相記錄）

| 現象 | 說明 |
|------|------|
| 系統 RAM free=177MB(0%) | 24GB 機器真實低記憶體，Ollama + 排程 session 佔用大 |
| Swap free=884MB(6%) | 仍有緩衝，但雙重壓力門檻（swap<5%+free<30%）尚未觸發 |
| runtime CRITICAL 1筆 | US 曝險 82.7%，deadline 今日（2026-07-17），Owner 應已知悉 |

---

## Cowork 排程保留原則

Cowork 端排程**保留**（不拆除），launchd 為第一層。Desktop Commander 恢復後自然形成雙重覆蓋（雙保險）。

---

## 後續建議

1. 觀察 memory-watch 告警頻率：若每 2h 都觸發，考慮請 Owner 關閉不必要的常駐程序
2. runtime CRITICAL（US 曝險）deadline 今日，Owner 需確認是否已處理
3. dispatch-backup 首次完整執行為今晚 03:00，可明早查看 `state/dispatch_backup.log` 確認

---

commit: 見本次 checkpoint（`scripts/checkpoint.sh "A1" "A0派工：監控去依賴化3腳本+launchd完成"`）
