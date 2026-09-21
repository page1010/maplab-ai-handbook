#!/bin/bash
# Launch a0_morning_brief.py detached (same 5404 lesson as start_spread_alert.sh:
# long-lived jobs must survive session close). Idempotent via the pidfile check
# inside the daemon; verification reads the pidfile the daemon writes.
set -u
LOG="$HOME/.maplab/a0_morning_brief.log"
PIDF="$HOME/.maplab/a0_morning_brief.pid"
mkdir -p "$HOME/.maplab"
{ echo "--- dry-run $(date '+%Y-%m-%dT%H:%M:%S') ---";
  /usr/bin/python3 /Users/pagemacmini/maplab-ai-handbook/scripts/a0_morning_brief.py --once;
} >> "$LOG" 2>&1
nohup /usr/bin/python3 /Users/pagemacmini/maplab-ai-handbook/scripts/a0_morning_brief.py >> "$LOG" 2>&1 &
disown 2>/dev/null || true
sleep 3
PID="$(cat "$PIDF" 2>/dev/null || true)"
if [[ -n "$PID" ]] && kill -0 "$PID" 2>/dev/null; then
  echo "STARTED pid=$PID"
else
  echo "FAILED (see $LOG)"
  tail -5 "$LOG" 2>/dev/null
fi
