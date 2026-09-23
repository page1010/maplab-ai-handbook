#!/usr/bin/env bash
# compounding_patrol_staleness.sh — Telegram-remind Owner if the weekly patrol has not succeeded in > 8 days.
# Root-fixes "silent skip": a missed patrol used to leave no trace. Run daily (launchd).
set -uo pipefail
F="$HOME/maplab-ai-handbook/state/compounding_patrol_last_ok"
NOTIFY="$HOME/maplab-ai-handbook/scripts/notify_owner.sh"
now=$(date +%s); MAXD=8
if [ ! -f "$F" ]; then msg="⚠️ 複利巡查從未記錄成功(無 last_ok)。請確認 launchd com.maplab.compounding-patrol 有跑。"; bash "$NOTIFY" "$msg" >/dev/null 2>&1; echo "$msg"; exit 3; fi
last=$(python3 -c 'import sys,re,datetime;s=open(sys.argv[1]).read().strip();s=re.sub(r"([+-]\d{2})(\d{2})$",r"\1:\2",s);print(int(datetime.datetime.fromisoformat(s).timestamp()))' "$F" 2>/dev/null || echo 0)
days=$(( (now - last) / 86400 ))
if [ "$days" -gt "$MAXD" ]; then
  msg="⚠️ 複利巡查已 ${days} 天沒成功跑(上次 $(cat "$F"))。排程可能靜默失效,請看 state/compounding_patrol_*.log。"
  bash "$NOTIFY" "$msg" >/dev/null 2>&1; echo "$msg"; exit 3
fi
echo "OK: last patrol ${days}d ago"
