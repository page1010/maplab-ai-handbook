# Hermes 記憶啟用 SOP (T-HQ-001 P6)

建立：2026-06-24（B1 Builder）  
⚠️ 啟用 provider 需 Owner/A1 批准（會改變 Hermes 行為）

## 現況（2026-06-24 量測）

```
~/.hermes/memories/     → 空目錄（0 bytes）
~/.hermes/SOUL.md       → 已存在，Investment OS 角色定義（共用）
hermes memory status    → Built-in: always active; Provider: (none — built-in only)
```

Hermes 已在跑（PID 951，ai.hermes.gateway），但沒有啟用任何記憶 provider。

## 記憶機制說明

Hermes 有兩層記憶：
1. **Built-in**（永久啟用）：`~/.hermes/SOUL.md`（角色定義 + 操作原則）
2. **外部 provider**（需 setup）：
   - `holographic`（本地，無需 API key）← 推薦
   - `honcho`、`mem0`、`hindsight`（需 API key）

## 啟用步驟（需 Owner 批准後執行）

### 步驟一：確認已安裝 holographic provider

```bash
hermes memory status     # 確認 holographic 在 Installed plugins 清單
```

### 步驟二：啟用本地 holographic provider

```bash
hermes memory setup holographic
# 互動式設定，會問儲存路徑；建議設為 ~/.hermes/memories/maplab/
```

### 步驟三：測試記憶寫入

```bash
# 在 Hermes 任務結束後，在 Hermes 對話中說：
# "請把這次學到的操作步驟記憶到 memories"
# Hermes 應該自動呼叫 memory provider 寫入。
```

### 步驟四：MAPLAB context 加入 SOUL.md

⚠️ `~/.hermes/SOUL.md` 目前是 Investment OS 設定，修改前需確認不影響 IOS 工作流程。
若要加入 MAPLAB 操作記憶，建議另建 `~/.hermes/memories/maplab/maplab_ops.md` 而不修改 SOUL.md。

## agent-hq 記憶鏡像（人工同步）

```bash
# B3 Archivist 每週執行
rsync -av ~/.hermes/memories/ /Users/pagemacmini/agent-hq/memory/hermes/
```

## A7 LINE JSONL export

- 腳本：`scripts/export_a7_line_jsonl.py`
- 目前狀況：23 筆客戶問句，**無業務回覆側資料**（LINE webhook only 捕捉客戶→OA）
- 啟用客戶問句 export：`python3 scripts/export_a7_line_jsonl.py --inputs-only`
- 完整 QA pair：需 LINE OA Manager 後台 CSV 匯出業務回覆側（Owner 操作）
- Launchd 每晚 23:50 自動跑：`scripts/com.maplab.a7-line-export.plist`

Owner 啟用 A7 launchd job 指令：
```bash
cp scripts/com.maplab.a7-line-export.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.maplab.a7-line-export.plist
```

## ⚠️ Owner 待辦

1. **Hermes memory provider 啟用**：批准後執行 `hermes memory setup holographic`（低風險，本地儲存）
2. **A7 JSONL launchd 啟用**：執行上方 `cp + launchctl load` 指令
3. **LINE OA Manager CSV 匯出**：若要完整 QA pairs，需從 LINE OA Manager 後台匯出業務回覆資料
