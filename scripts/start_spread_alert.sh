#!/bin/bash
# Launch spread_alert_watch.py detached from the calling window (5404 lesson:
# long-lived jobs must survive session close). Idempotent via the pidfile check
# inside the watcher itself; verification reads the pidfile the daemon writes.
set -u
LOG="$HOME/.maplab/spread_alert.log"
PIDF="$HOME/.maplab/spread_alert.pid"
mkdir -p "$HOME/.maplab"
nohup /usr/bin/python3 /Users/pagemacmini/maplab-ai-handbook/scripts/spread_alert_watch.py --daemon "$@" >> "$LOG" 2>&1 &
disown 2>/dev/null || true
sleep 3
PID="$(cat "$PIDF" 2>/dev/null || true)"
if [[ -n "$PID" ]] && kill -0 "$PID" 2>/dev/null; then
  echo "STARTED pid=$PID"
else
  echo "FAILED (see $LOG)"
  tail -5 "$LOG" 2>/dev/null
fi
