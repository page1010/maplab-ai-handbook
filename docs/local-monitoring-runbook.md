# Local Monitoring Runbook

> 維護者：A1 系統總管
> 建立：2026-07-17 A0 自主派工（監控排程去依賴化）
> 目標：讓 memory-watch / runtime 鬧鈴 / 備份三個排程脫離 Cowork Desktop Commander，直接在 Mac mini 本機 launchd 運行

---

## 三個 launchd 任務總覽

| Label | 腳本 | 觸發頻率 | 告警通道 | Log |
|-------|------|---------|---------|-----|
| `com.maplab.memory-watch` | `scripts/local_memory_watch.sh` | 每 2 小時 | Telegram | `state/memory_watch.log` |
| `com.maplab.runtime-alarm` | `scripts/local_runtime_alarm.sh` | 每日 08:30 | Telegram | `state/runtime_alarm.log` |
| `com.maplab.dispatch-backup` | `scripts/local_dispatch_backup.sh` | 每日 03:00 | Telegram（僅錯誤） | `state/dispatch_backup.log` |

---

## 任務 1：memory-watch（每 2 小時）

**腳本**：`scripts/local_memory_watch.sh`

**五項檢查邏輯**：
1. **Ollama 去抖**：Ollama 啟動中 且 free≥12% → 靜默（正常狀態）
2. **非 Ollama 門檻**：Ollama 未啟動 且 free<20% → Telegram 警告
3. **Ollama 壓力門檻**：Ollama 啟動中 且 free<12% → Telegram 警告
4. **Swap 雙重壓力**：swap_free<5% 且 RAM_free<30% → Telegram 警告
5. **Codex orphan**：codex 程序超過 2 個 → Telegram 警告（列出 pids）

**Log 保留**：7 天（自動修剪）

---

## 任務 2：runtime-alarm（每日 08:30）

**腳本**：`scripts/local_runtime_alarm.sh`

**邏輯**：
- 讀取 `/Users/pagemacmini/Documents/New project/state/runtime_escalation_queue.jsonl`
- 篩選 `status == "open"` AND `severity == "CRITICAL"` 條目
- 去重（相同 routing_key 只報一次）
- 若有 CRITICAL → 推 Telegram（列出 component、description、deadline）
- 無 CRITICAL → log 一行 `✅ 無 open CRITICAL，靜默`

**與 Cowork 關係**：Cowork 端排程保留當第二層，工具恢復時自然雙保險。

---

## 任務 3：dispatch-backup（每日 03:00）

**腳本**：`scripts/local_dispatch_backup.sh`

### 雙目的地設計（2026-07-18 升級）

| 層 | 目的地 | 策略 | 保留 |
|---|--------|------|------|
| 內接碟（快取層） | `~/maplab_backup/YYYYMMDD/` | rsync + `--delete`（快照） | 7 天輪替 |
| 外接碟（長期層） | `/Volumes/MacExternal/MAPLAB_BACKUP/dispatch-sessions/` | rsync -a（累加，絕不 `--delete`） | 永久保留 |

**內接碟備份範圍**（三個 repo）：
- `~/maplab-ai-handbook` → `~/maplab_backup/YYYYMMDD/maplab-ai-handbook/`
- `~/agent-hq` → `~/maplab_backup/YYYYMMDD/agent-hq/`
- `/Users/pagemacmini/Documents/New project/` → `~/maplab_backup/YYYYMMDD/new-project/`

**外接碟備份範圍**（A0 dispatch sessions）：
- 來源：`~/Library/Application Support/Claude/local-agent-mode-sessions/`
- 目的地：`/Volumes/MacExternal/MAPLAB_BACKUP/dispatch-sessions/`

**排除**：`.git`, `__pycache__`, `*.pyc`, `.DS_Store`, `node_modules`, `.venv`

**INDEX 重生**：
- 內接碟：走訪三個 repo（os.walk）→ `state/dispatch_backup_index.json`（含 path / size / mtime）
- 外接碟：走訪 dispatch-sessions/（os.walk）→ `dispatch-sessions/INDEX.md`（Markdown 表格，最新 200 筆）

**backup.log**：每次完成追加一行到 `dispatch-sessions/backup.log`

**告警邏輯**：
- 內接碟 rsync 來源找不到 → Telegram 警告
- 外接碟未掛載或不可寫 → 只記 log，**不告警**（外接碟可能正常拔走）

**保留**：內接碟 7 天（自動刪除）；外接碟永久累加

---

## 管理指令

### 查看狀態

```bash
# 確認三個任務已裝載
launchctl list | grep com.maplab.memory-watch
launchctl list | grep com.maplab.runtime-alarm
launchctl list | grep com.maplab.dispatch-backup

# 查看 log
tail -20 ~/maplab-ai-handbook/state/memory_watch.log
tail -20 ~/maplab-ai-handbook/state/runtime_alarm.log
tail -20 ~/maplab-ai-handbook/state/dispatch_backup.log
```

### 手動觸發（測試用）

```bash
bash ~/maplab-ai-handbook/scripts/local_memory_watch.sh
bash ~/maplab-ai-handbook/scripts/local_runtime_alarm.sh
bash ~/maplab-ai-handbook/scripts/local_dispatch_backup.sh
```

### 卸載（停用）

```bash
launchctl unload ~/Library/LaunchAgents/com.maplab.memory-watch.plist
launchctl unload ~/Library/LaunchAgents/com.maplab.runtime-alarm.plist
launchctl unload ~/Library/LaunchAgents/com.maplab.dispatch-backup.plist
```

### 重新裝載（更新腳本後）

```bash
# 先更新腳本，再：
REPO=~/maplab-ai-handbook/scripts
cp $REPO/com.maplab.memory-watch.plist ~/Library/LaunchAgents/
cp $REPO/com.maplab.runtime-alarm.plist ~/Library/LaunchAgents/
cp $REPO/com.maplab.dispatch-backup.plist ~/Library/LaunchAgents/

for label in com.maplab.memory-watch com.maplab.runtime-alarm com.maplab.dispatch-backup; do
    launchctl unload ~/Library/LaunchAgents/${label}.plist 2>/dev/null || true
    launchctl load  ~/Library/LaunchAgents/${label}.plist
done
```

### 看 launchd 錯誤

```bash
# 每個任務都有獨立 launchd log
tail -20 ~/maplab-ai-handbook/logs/memory_watch_launchd.log
tail -20 ~/maplab-ai-handbook/logs/runtime_alarm_launchd.log
tail -20 ~/maplab-ai-handbook/logs/dispatch_backup_launchd.log
```

---

## 設計決策

**為何不用 Cowork 排程？**
Cowork 排程 session 需要 Desktop Commander MCP，工具不可用時整個排程空跑。launchd 是 macOS 原生排程，無外部依賴，Mac mini 開機即自動啟動。

**雙保險原則**：Cowork 端排程仍保留，launchd 為第一層。Desktop Commander 恢復後自然成雙重覆蓋。

**Ollama 去抖邏輯**：Ollama 運行時 RAM 消耗較高屬正常，門檻從 20% 降至 12%，避免誤報。

**dispatch-backup 雙目的地設計（2026-07-18）**：
- 發現 Cowork 原排程停止後，外接碟備份停留在 07-17（74 小時斷檔）。
- 修補方案：launchd 備份腳本加外接碟段，採「累加、絕不 --delete」策略，確保歷史永久保留。
- 外接碟未掛載屬正常情況（Owner 拔走屬預期），不推 Telegram 告警，只記 log。
- 實測（2026-07-18）：769 個 jsonl，129.7MB，INDEX.md 時間戳已更新。

---

## 首次實測結果（2026-07-17 14:08）

- `memory-watch` 手動觸發：free=177MB(0%) + swap_free=6% → 觸發 WARN（系統確實低記憶體）
- `runtime-alarm` 手動觸發：1 筆 open CRITICAL（US 曝險 82.7%，deadline 2026-07-17）→ Telegram 推播成功
- 兩個告警路徑 log 落地 + Telegram 推播均確認 ✅
