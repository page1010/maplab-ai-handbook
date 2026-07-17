#!/usr/bin/env bash
# local_runtime_alarm.sh — 每日 08:30 掃 runtime_escalation_queue.jsonl
# 找 status=open AND severity=CRITICAL 條目 → 推 Telegram
# 作為 Cowork 排程第二層保障，Cowork 工具恢復時自然雙保險

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
NOTIFY="$REPO_ROOT/scripts/notify_owner.sh"
QUEUE="/Users/pagemacmini/Documents/New project/state/runtime_escalation_queue.jsonl"
LOG_FILE="$REPO_ROOT/state/runtime_alarm.log"

ts()  { date '+%Y-%m-%d %H:%M:%S'; }
log() { echo "[$(ts)] $*" >> "$LOG_FILE"; }

log "=== runtime alarm check ==="

if [[ ! -f "$QUEUE" ]]; then
    log "⚠️ queue not found: $QUEUE"
    exit 0
fi

RESULT=$(python3 - <<'PYEOF'
import json, sys

QUEUE = "/Users/pagemacmini/Documents/New project/state/runtime_escalation_queue.jsonl"

criticals = []
seen_keys = set()
with open(QUEUE) as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        try:
            r = json.loads(line)
        except Exception:
            continue
        if r.get('status') == 'open' and r.get('severity') == 'CRITICAL':
            key = r.get('routing_key', r.get('id', ''))
            if key not in seen_keys:
                seen_keys.add(key)
                criticals.append(r)

if not criticals:
    print("OK")
else:
    lines = [f"🚨 [runtime-alarm] {len(criticals)} 筆 open CRITICAL:"]
    for r in criticals[:5]:
        deadline = r.get('deadline_at', '?')
        comp = r.get('component', '?')
        desc = r.get('description', '?')
        lines.append(f"  • [{comp}] {desc} (deadline: {deadline})")
    if len(criticals) > 5:
        lines.append(f"  ... 另 {len(criticals)-5} 筆")
    print('\n'.join(lines))
PYEOF
)

log "$RESULT"

if [[ "$RESULT" != "OK" ]]; then
    bash "$NOTIFY" "$RESULT" 2>/dev/null || log "NOTIFY_FAILED（Telegram 推播失敗）"
    log "推播已觸發"
else
    log "✅ 無 open CRITICAL，靜默"
fi
