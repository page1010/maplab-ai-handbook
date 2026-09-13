#!/usr/bin/env bash
# compounding_patrol_run.sh — launchd-safe runner for the weekly compounding patrol.
# Why: the scheduled-tasks (Cowork) version silently failed because Desktop Commander/osascript
# need tool approval in that context. launchd runs plain shell = no approval layer.
# Writes state/compounding_patrol_last_ok on success; skips if another claude -p is running.
set -uo pipefail
REPO="$HOME/maplab-ai-handbook"; cd "$REPO" || exit 1
PROMPT="skills/compounding-patrol-prompt.md"; [ -f "$PROMPT" ] || { echo "FATAL: $PROMPT missing"; exit 2; }
if [ "$(pgrep -f 'claude -p' | wc -l | tr -d ' ')" -gt 0 ]; then echo "skip: another claude -p running"; exit 0; fi
git pull -q 2>/dev/null || true
export CLAUDE_CODE_OAUTH_TOKEN="$(grep '^CLAUDE_CODE_OAUTH_TOKEN=' .env | cut -d= -f2-)"
LOG="state/compounding_patrol_$(date +%Y%m%d).log"
claude -p "$(cat "$PROMPT")" --dangerously-skip-permissions > "$LOG" 2>&1; rc=$?
if [ $rc -eq 0 ] && [ -s "$LOG" ]; then
  date '+%Y-%m-%dT%H:%M:%S%z' > state/compounding_patrol_last_ok
  echo "patrol OK rc=0 -> last_ok updated"
else
  echo "patrol FAILED rc=$rc (log: $LOG)"
fi
exit $rc
