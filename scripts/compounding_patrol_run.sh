#!/usr/bin/env bash
# compounding_patrol_run.sh — launchd-safe runner for the weekly compounding patrol.
# Why: the scheduled-tasks (Cowork) version silently failed because Desktop Commander/osascript
# need tool approval in that context. launchd runs plain shell = no approval layer.
# Writes state/compounding_patrol_last_ok on success; skips if another claude -p is running.
set -uo pipefail
REPO="$HOME/maplab-ai-handbook"; cd "$REPO" || exit 1
PROMPT="skills/compounding-patrol-prompt.md"; [ -f "$PROMPT" ] || { echo "FATAL: $PROMPT missing"; exit 2; }
# 2026-09-23 修:launchd 不繼承登入 shell 的 PATH,而 claude 裝在 ~/.local/bin,
# 所以 9/20 20:05 第一次 launchd 觸發就 rc=127 (claude: command not found)。
# 這裡自己補 PATH 並解析成絕對路徑,不依賴 plist 有沒有 EnvironmentVariables。
export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"
CLAUDE_BIN="$(command -v claude || true)"
[ -n "$CLAUDE_BIN" ] || { echo "FATAL: claude not found (PATH=$PATH)"; exit 127; }
if [ "$(pgrep -f 'claude -p' | wc -l | tr -d ' ')" -gt 0 ]; then echo "skip: another claude -p running"; exit 0; fi
git pull -q 2>/dev/null || true
export CLAUDE_CODE_OAUTH_TOKEN="$(grep '^CLAUDE_CODE_OAUTH_TOKEN=' .env | cut -d= -f2-)"
LOG="state/compounding_patrol_$(date +%Y%m%d).log"
"$CLAUDE_BIN" -p "$(cat "$PROMPT")" --dangerously-skip-permissions > "$LOG" 2>&1; rc=$?
if [ $rc -eq 0 ] && [ -s "$LOG" ]; then
  date '+%Y-%m-%dT%H:%M:%S%z' > state/compounding_patrol_last_ok
  echo "patrol OK rc=0 -> last_ok updated"
else
  echo "patrol FAILED rc=$rc (log: $LOG)"
fi
exit $rc
