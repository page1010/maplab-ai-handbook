# B-Role 維護 SOP — 地端模型版

版本：v1.0 | 建立：2026-06-25 | 維護：A1 / B4
觸發條件：任何 agent 需要做 B2-B4 維護，或 launchd 排程定期觸發

> **設計目標：** 地端模型（qwen2.5:14b / Ollama）可獨立完成本 SOP 的 §1-§4。
> 只有 §5 的升級條件才需要回報 Claude 或 Owner。
> Claude 不再做例行巡查，只做升級時的深度分析。

---

## 整體架構

```
launchd（每週一次）
  └→ 地端模型（qwen2.5:14b via Ollama）
        執行 §1 讀狀態 → §2 比較門檻 → §3 分類 → §4 產 JSON report
        若有 §5 升級條件 → Telegram 警報 → Owner / Claude 介入
```

---

## §1 讀狀態（每次都要做，順序固定）

地端模型執行以下 bash 指令（不改任何檔案，只讀）：

```bash
# 1a. Investment OS DB 健康
python3 - <<'EOF'
import sqlite3, json
DB = '/Users/pagemacmini/.local/share/investmentos-telegram-operator/data/investment_os.sqlite3'
conn = sqlite3.connect(DB, timeout=5)
result = {}
# Row counts for key tables
for t in ['influencer_insights','influencer_cross_checks','market_signals',
          'simulated_positions','research_signals','api_error_logs',
          'agent_outputs','evidence_items']:
    try:
        result[t] = conn.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0]
    except:
        result[t] = 'TABLE_MISSING'
conn.close()
print(json.dumps(result, indent=2))
EOF

# 1b. shadow concern 數量
wc -l /Users/pagemacmini/Documents/New\ project/reports/shadow/local_model_findings.jsonl 2>/dev/null || echo "0"

# 1c. nightwatch 最新時間
head -3 /Users/pagemacmini/Documents/New\ project/reports/nightwatch/latest.md 2>/dev/null || echo "NOT_FOUND"

# 1d. B-role receipt 最後更新
ls -t /Users/pagemacmini/maplab-ai-handbook/workbook/reviews/JOB-B2-REVIEW-*/dataflow_review.md 2>/dev/null | head -1
ls -t /Users/pagemacmini/maplab-ai-handbook/workbook/reviews/JOB-B3-ARCHIVE-*/b_role_rsi_archive.md 2>/dev/null | head -1
ls -t /Users/pagemacmini/maplab-ai-handbook/workbook/reviews/JOB-B4-PATROL-*/fit_check.md 2>/dev/null | head -1

# 1e. 上次 RSI 分數（從最新 JSON 讀）
python3 -c "
import glob, json
files = sorted(glob.glob('/Users/pagemacmini/maplab-ai-handbook/workbook/reviews/JOB-B*/b_role_recursive_self_improvement.json'))
if files:
    with open(files[-1]) as f: d = json.load(f)
    print(f'RSI score: {d.get(\"score\", \"N/A\")} band: {d.get(\"band\", \"N/A\")} date: {d.get(\"generated_at\", \"N/A\")}')
else:
    print('RSI JSON: NOT_FOUND')
" 2>/dev/null
```

---

## §2 門檻比較（地端模型讀 §1 輸出後對照）

| 項目 | 門檻 | 超過就標 🔴 |
|------|------|------------|
| `api_error_logs` rows | 0 | > 0 |
| `market_signals` rows | > 0 | == 0 |
| `local_model_findings.jsonl` 行數 | < 50 | ≥ 50（堆積）|
| nightwatch 文件距今天數 | < 3 天 | ≥ 3 天 |
| B2 receipt 距今天數 | < 7 天 | ≥ 7 天 |
| B3 receipt 距今天數 | < 7 天 | ≥ 7 天 |
| B4 receipt 距今天數 | < 7 天 | ≥ 7 天 |
| RSI band | working（70+）| broken/degraded |

---

## §3 分類（地端模型做，輸出 JSON）

地端模型使用以下 **prompt template**（貼給 `ollama run qwen2.5:14b`）：

```
你是 Investment OS B2 Reviewer。
以下是系統健康快照（JSON）：
[貼入 §1 輸出]

你的任務：
1. 對照以下門檻表，標記每個項目是 ok / warn / critical
2. 用以下 JSON 格式輸出結果（不要加任何說明文字，只輸出 JSON）：

{
  "run_date": "YYYY-MM-DD",
  "rsi_score": 數字或 null,
  "rsi_band": "字串",
  "items": [
    {"name": "api_error_logs", "value": 數字, "threshold": 0, "status": "ok|warn|critical"},
    {"name": "market_signals", "value": 數字, "threshold": 0, "status": "ok|warn|critical"},
    {"name": "shadow_concerns", "value": 數字, "threshold": 50, "status": "ok|warn|critical"},
    {"name": "nightwatch_age_days", "value": 數字, "threshold": 3, "status": "ok|warn|critical"},
    {"name": "b2_receipt_age_days", "value": 數字, "threshold": 7, "status": "ok|warn|critical"},
    {"name": "b3_receipt_age_days", "value": 數字, "threshold": 7, "status": "ok|warn|critical"},
    {"name": "b4_receipt_age_days", "value": 數字, "threshold": 7, "status": "ok|warn|critical"}
  ],
  "critical_count": 數字,
  "escalate": true 或 false
}

escalate = true 的條件：critical_count >= 2，或 api_error_logs > 5，或 rsi_band 為 broken
```

---

## §4 產出 Report（寫檔，不需要 Claude）

地端模型完成 §3 後，把 JSON 寫入：

```bash
OUTPUT_DIR="/Users/pagemacmini/maplab-ai-handbook/workbook/reviews/JOB-B2-LOCAL-$(date +%Y%m%d)"
mkdir -p "$OUTPUT_DIR"
# 把 §3 的 JSON 輸出寫到：
# $OUTPUT_DIR/freshness_check.json
```

然後用 bash 更新 `latest.json`（patrol-style）：
```bash
cp "$OUTPUT_DIR/freshness_check.json" \
  /Users/pagemacmini/maplab-ai-handbook/workbook/hermes/patrol/latest.json
```

**完成條件（地端模型可自己判斷）：**
- `freshness_check.json` 檔案存在
- JSON 格式合法（`python3 -m json.tool freshness_check.json` 不報錯）
- `escalate: false` → 不用做任何事，任務完成

---

## §5 升級條件（escalate: true 時才做）

地端模型把以下訊息透過 Telegram 推給 Owner：

```bash
# 讀 Telegram bot token（從環境變數，不寫進腳本）
curl -s "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
  -d chat_id="${TELEGRAM_CHAT_ID}" \
  -d text="⚠️ B-role 維護警報 $(date +%Y-%m-%d)
critical_count: X
主要問題: [從 JSON items 讀 critical 項的 name 列表]
請召喚 B2-B4 或 Claude 深入處理。
receipt: workbook/reviews/JOB-B2-LOCAL-YYYYMMDD/"
```

**升級後 Claude/B-role 介入步驟：**
1. 讀 `workbook/reviews/JOB-B2-LOCAL-YYYYMMDD/freshness_check.json`
2. 讀 `workbook/reviews/JOB-B3-ARCHIVE-*/resume_prompt.md` 中的召喚 prompt
3. 執行完整 B2-B4 Claude session（依本文件之前的流程）
4. 產出新的 B2/B3/B4 review bundle
5. 更新 `source_freshness_matrix.md`

---

## §6 launchd 排程設計

### plist 檔案（存為 `scripts/com.investmentos.b-role-maintenance.plist`）

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>com.investmentos.b-role-maintenance</string>

  <key>ProgramArguments</key>
  <array>
    <string>/bin/bash</string>
    <string>/Users/pagemacmini/maplab-ai-handbook/scripts/b_role_local_maintenance.sh</string>
  </array>

  <!-- 每週一 09:00 跑一次 -->
  <key>StartCalendarInterval</key>
  <dict>
    <key>Weekday</key>
    <integer>1</integer>
    <key>Hour</key>
    <integer>9</integer>
    <key>Minute</key>
    <integer>0</integer>
  </dict>

  <key>StandardOutPath</key>
  <string>/Users/pagemacmini/maplab-ai-handbook/logs/b_role_maintenance.log</string>
  <key>StandardErrorPath</key>
  <string>/Users/pagemacmini/maplab-ai-handbook/logs/b_role_maintenance_err.log</string>

  <!-- 最長跑 10 分鐘，超過就 kill -->
  <key>TimeOut</key>
  <integer>600</integer>
</dict>
</plist>
```

**啟用指令：**
```bash
cp scripts/com.investmentos.b-role-maintenance.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.investmentos.b-role-maintenance.plist
```

### 主腳本（`scripts/b_role_local_maintenance.sh`）

```bash
#!/usr/bin/env bash
# B-role 地端維護腳本
# 被 launchd 觸發，用 Ollama 完成 §1-§4
set -euo pipefail

REPO=/Users/pagemacmini/maplab-ai-handbook
DB=/Users/pagemacmini/.local/share/investmentos-telegram-operator/data/investment_os.sqlite3
DATE=$(date +%Y%m%d)
OUT="$REPO/workbook/reviews/JOB-B2-LOCAL-$DATE"
mkdir -p "$OUT"

echo "[$(date)] B-role maintenance started" >> "$REPO/logs/b_role_maintenance.log"

# §1 收集狀態快照
python3 "$REPO/scripts/b_role_health_snapshot.py" > "$OUT/snapshot.json" 2>&1

# §2+§3 地端模型分類
SNAPSHOT=$(cat "$OUT/snapshot.json")
PROMPT="你是 Investment OS B2 Reviewer。以下是系統健康快照：$SNAPSHOT
按 skills/local-agent-b-role-maintenance.md §3 的 JSON 格式輸出分類結果，只輸出 JSON。"

ollama run qwen2.5:14b "$PROMPT" > "$OUT/freshness_check_raw.txt" 2>&1

# 提取 JSON（去掉 markdown code fences）
python3 -c "
import sys, json, re
raw = open('$OUT/freshness_check_raw.txt').read()
# 嘗試提取 JSON 區塊
match = re.search(r'\{.*\}', raw, re.DOTALL)
if match:
    d = json.loads(match.group())
    print(json.dumps(d, ensure_ascii=False, indent=2))
else:
    print(json.dumps({'error': 'JSON parse failed', 'raw': raw[:200]}))
" > "$OUT/freshness_check.json"

# §4 更新 patrol latest
cp "$OUT/freshness_check.json" "$REPO/workbook/hermes/patrol/latest.json"

# §5 升級檢查
ESCALATE=$(python3 -c "
import json
d = json.load(open('$OUT/freshness_check.json'))
print(str(d.get('escalate', False)).lower())
" 2>/dev/null || echo "false")

if [ "$ESCALATE" = "true" ]; then
  echo "[$(date)] ESCALATE triggered" >> "$REPO/logs/b_role_maintenance.log"
  # 發 Telegram（需要 env var）
  if [ -n "${TELEGRAM_BOT_TOKEN:-}" ] && [ -n "${TELEGRAM_CHAT_ID:-}" ]; then
    CRITICAL_COUNT=$(python3 -c "import json; d=json.load(open('$OUT/freshness_check.json')); print(d.get('critical_count',0))")
    curl -s "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
      -d chat_id="${TELEGRAM_CHAT_ID}" \
      -d text="⚠️ B-role 維護警報 $DATE critical=$CRITICAL_COUNT 請召喚 B2-B4。receipt: JOB-B2-LOCAL-$DATE/"
  fi
fi

echo "[$(date)] B-role maintenance done. escalate=$ESCALATE" >> "$REPO/logs/b_role_maintenance.log"
```

---

## §7 健康快照腳本（`scripts/b_role_health_snapshot.py`）

```python
#!/usr/bin/env python3
"""
B-role health snapshot — 只讀，不寫任何 DB 或生產檔案。
輸出 JSON 給地端模型判斷。
"""
import sqlite3, json, os, glob
from datetime import datetime, timezone

DB = os.path.expanduser(
    '~/.local/share/investmentos-telegram-operator/data/investment_os.sqlite3')
REPO = os.path.expanduser('~/maplab-ai-handbook')
IOS = os.path.expanduser('~/Documents/New project')

result = {'snapshot_time': datetime.now(timezone.utc).isoformat()}

# 1. DB row counts
try:
    conn = sqlite3.connect(DB, timeout=5)
    for t in ['influencer_insights', 'influencer_cross_checks', 'market_signals',
              'simulated_positions', 'research_signals', 'api_error_logs',
              'agent_outputs', 'evidence_items']:
        try:
            result[f'db_{t}'] = conn.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0]
        except:
            result[f'db_{t}'] = 'TABLE_MISSING'
    conn.close()
    result['db_accessible'] = True
except Exception as e:
    result['db_accessible'] = False
    result['db_error'] = str(e)

# 2. shadow concern count
sc_file = os.path.join(IOS, 'reports/shadow/local_model_findings.jsonl')
result['shadow_concern_count'] = sum(1 for _ in open(sc_file)) if os.path.exists(sc_file) else 0

# 3. nightwatch age (days)
nw_file = os.path.join(IOS, 'reports/nightwatch/latest.md')
if os.path.exists(nw_file):
    age_sec = (datetime.now() - datetime.fromtimestamp(os.path.getmtime(nw_file))).total_seconds()
    result['nightwatch_age_days'] = round(age_sec / 86400, 1)
else:
    result['nightwatch_age_days'] = 999

# 4. B-role receipt ages (days)
for role, pattern in [
    ('b2', 'JOB-B2-REVIEW-*/dataflow_review.md'),
    ('b3', 'JOB-B3-ARCHIVE-*/b_role_rsi_archive.md'),
    ('b4', 'JOB-B4-PATROL-*/fit_check.md'),
]:
    files = sorted(glob.glob(os.path.join(REPO, 'workbook/reviews', pattern)))
    if files:
        age_sec = (datetime.now() - datetime.fromtimestamp(os.path.getmtime(files[-1]))).total_seconds()
        result[f'{role}_receipt_age_days'] = round(age_sec / 86400, 1)
    else:
        result[f'{role}_receipt_age_days'] = 999

# 5. RSI score from latest JSON
rsi_files = sorted(glob.glob(
    os.path.join(REPO, 'workbook/reviews/JOB-B*/b_role_recursive_self_improvement.json')))
if rsi_files:
    try:
        with open(rsi_files[-1]) as f:
            rsi_data = json.load(f)
        result['rsi_score'] = rsi_data.get('score')
        result['rsi_band'] = rsi_data.get('band')
        result['rsi_date'] = rsi_data.get('generated_at')
    except:
        result['rsi_score'] = None
        result['rsi_band'] = 'unknown'
else:
    result['rsi_score'] = None
    result['rsi_band'] = 'no_json_found'

print(json.dumps(result, indent=2, ensure_ascii=False))
```

---

## 邊界規則（地端模型必須遵守）

1. **不下單、不建模擬單、不給買賣建議**（Investment OS B-role 共用規則）
2. **不讀 `.env` / secrets / cookies**
3. **不寫入生產 DB**（只讀 SQLite，不 INSERT/UPDATE/DELETE）
4. **不 push main**（只寫 workbook/reviews/ 目錄下的新文件）
5. **不碰正在進行的 B1 任務**（本次 B1 在動 .gitignore / line_booking / AGENT_RULES）
6. **escalate = true 時只推 Telegram 通知，不自己決定修復方案**

---

## 快速驗收（第一次啟動後檢查）

```bash
# 驗收 1：snapshot 腳本可跑
python3 scripts/b_role_health_snapshot.py | python3 -m json.tool

# 驗收 2：Ollama 可用
ollama list | grep qwen2.5

# 驗收 3：plist 已載入
launchctl list | grep b-role-maintenance

# 驗收 4：手動觸發一次
bash scripts/b_role_local_maintenance.sh
cat workbook/reviews/JOB-B2-LOCAL-$(date +%Y%m%d)/freshness_check.json | python3 -m json.tool
```

---

## 已知邊界（地端模型接手後 Claude 不再做的事）

| 以前 Claude 做 | 現在地端做 | Claude 只在 escalate 時介入 |
|---------------|----------|--------------------------|
| 每日 B2 freshness check | qwen2.5 每週一次 | critical_count ≥ 2 |
| shadow concern triage（機械性）| qwen2.5 分類 ok/warn/critical | 需深度推理才回 Claude |
| B-role receipt 時間比較 | python3 + bash | N/A |
| IOS-KOL digest gate 確認（checklist）| 地端模型對照 gate 規則 | rubric 評分 + 異常才 Claude |
| RSI 分數估算 | scorer Python 腳本 | 分數解讀 + 改進建議 |

---

*建立：2026-06-25 | 觸發條件：B2-B4 任何維護場景 | 地端模型：qwen2.5:14b via Ollama*
