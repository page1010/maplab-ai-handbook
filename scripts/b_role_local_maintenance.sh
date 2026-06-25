#!/usr/bin/env bash
# B-role 地端維護腳本
# 觸發：launchd com.investmentos.b-role-maintenance（每週一 09:00）
# 執行者：地端模型（Ollama qwen2.5:14b）
# 依 skills/local-agent-b-role-maintenance.md §6 設計
set -euo pipefail

REPO=/Users/pagemacmini/maplab-ai-handbook
DATE=$(date +%Y%m%d)
OUT="$REPO/workbook/reviews/JOB-B2-LOCAL-$DATE"
LOG="$REPO/logs/b_role_maintenance.log"
mkdir -p "$OUT" "$REPO/logs"

log() { echo "[$(date '+%Y-%m-%dT%H:%M:%S')] $*" >> "$LOG"; }

log "B-role maintenance started"

# §1 收集狀態快照
python3 "$REPO/scripts/b_role_health_snapshot.py" > "$OUT/snapshot.json" 2>&1 \
  || { log "SNAPSHOT FAILED"; exit 1; }
log "Snapshot written to $OUT/snapshot.json"

# §2+§3 地端模型分類（需 Ollama 已啟動且 qwen2.5:14b 已 pull）
SNAPSHOT=$(cat "$OUT/snapshot.json")

# 讀取 SOP §3 的 prompt template
PROMPT="你是 Investment OS B2 Reviewer。
以下是系統健康快照（JSON）：
$SNAPSHOT

你的任務：對照門檻表，輸出以下 JSON（只輸出 JSON，不加說明文字）：
{
  \"run_date\": \"$DATE\",
  \"rsi_score\": null,
  \"rsi_band\": \"unknown\",
  \"items\": [
    {\"name\": \"api_error_logs\",     \"value\": DB_COUNT, \"threshold\": 0, \"status\": \"ok|warn|critical\"},
    {\"name\": \"market_signals\",     \"value\": DB_COUNT, \"threshold\": 1, \"status\": \"ok|warn|critical\"},
    {\"name\": \"shadow_concerns\",    \"value\": COUNT,    \"threshold\": 50, \"status\": \"ok|warn|critical\"},
    {\"name\": \"nightwatch_age_days\",\"value\": DAYS,     \"threshold\": 3,  \"status\": \"ok|warn|critical\"},
    {\"name\": \"b2_receipt_age_days\",\"value\": DAYS,     \"threshold\": 7,  \"status\": \"ok|warn|critical\"},
    {\"name\": \"b3_receipt_age_days\",\"value\": DAYS,     \"threshold\": 7,  \"status\": \"ok|warn|critical\"},
    {\"name\": \"b4_receipt_age_days\",\"value\": DAYS,     \"threshold\": 7,  \"status\": \"ok|warn|critical\"}
  ],
  \"critical_count\": 數字,
  \"escalate\": true 或 false
}
escalate=true 條件：critical_count >= 2，或 api_error_logs > 5，或 rsi_band=broken"

if command -v ollama &>/dev/null; then
  ollama run qwen2.5:14b "$PROMPT" > "$OUT/freshness_check_raw.txt" 2>&1 \
    || { log "OLLAMA FAILED"; echo '{"error":"ollama_failed","escalate":true,"critical_count":99}' > "$OUT/freshness_check.json"; }
else
  log "Ollama not found — writing escalation JSON"
  echo '{"error":"ollama_not_installed","escalate":true,"critical_count":99}' > "$OUT/freshness_check.json"
fi

# 提取 JSON 區塊（去掉 markdown fence）
if [ -f "$OUT/freshness_check_raw.txt" ]; then
  python3 - <<PYEOF > "$OUT/freshness_check.json"
import sys, json, re
raw = open("$OUT/freshness_check_raw.txt").read()
match = re.search(r'\{.*\}', raw, re.DOTALL)
if match:
    try:
        d = json.loads(match.group())
        print(json.dumps(d, ensure_ascii=False, indent=2))
    except json.JSONDecodeError as e:
        print(json.dumps({"error": f"json_parse_failed: {e}", "raw": raw[:300], "escalate": True, "critical_count": 99}))
else:
    print(json.dumps({"error": "no_json_found", "raw": raw[:300], "escalate": True, "critical_count": 99}))
PYEOF
fi

log "freshness_check.json written"

# §4 更新 patrol latest
cp "$OUT/freshness_check.json" "$REPO/workbook/hermes/patrol/latest.json" 2>/dev/null || true

# §5 升級檢查
ESCALATE=$(python3 -c "
import json
try:
    d = json.load(open('$OUT/freshness_check.json'))
    print(str(d.get('escalate', False)).lower())
except:
    print('true')
" 2>/dev/null || echo "true")

if [ "$ESCALATE" = "true" ]; then
  log "ESCALATE triggered"
  # 寫 escalation file（由 hermes_status.js 或 A0 patrol 讀取並送 Telegram）
  CRITICAL_COUNT=$(python3 -c "
import json
try:
    d = json.load(open('$OUT/freshness_check.json'))
    print(d.get('critical_count', '?'))
except:
    print('?')
" 2>/dev/null || echo "?")

  cat > "$REPO/workbook/hermes/patrol/b_role_escalation.json" << JSON
{
  "ts": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "escalate": true,
  "critical_count": $CRITICAL_COUNT,
  "receipt": "workbook/reviews/JOB-B2-LOCAL-$DATE/freshness_check.json",
  "action": "召喚 B2-B4 或 Claude 深入分析",
  "telegram_message": "⚠️ B-role 維護警報 $DATE critical=$CRITICAL_COUNT 請召喚 B2-B4"
}
JSON

  # 若有 Telegram env var 則送通知
  if [ -n "${TELEGRAM_BOT_TOKEN:-}" ] && [ -n "${TELEGRAM_CHAT_ID:-}" ]; then
    curl -s "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
      -d "chat_id=${TELEGRAM_CHAT_ID}" \
      -d "text=⚠️ B-role 維護警報 $DATE critical=$CRITICAL_COUNT 請召喚 B2-B4。receipt: JOB-B2-LOCAL-$DATE/" \
      >> "$LOG" 2>&1 || true
  fi
else
  log "OK — no escalation needed"
  # 清掉舊 escalation file（若有）
  rm -f "$REPO/workbook/hermes/patrol/b_role_escalation.json"
fi

log "B-role maintenance done. escalate=$ESCALATE receipt=$OUT/freshness_check.json"
