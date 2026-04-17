#!/bin/bash
# rotate-bot-logs.sh — Bot log 輪轉
# 每次執行：截斷超過 5MB 的 log 檔，保留最後 1000 行
# 可掛 launchd 每日執行，或由 patrol.sh 呼叫

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MAX_SIZE=$((5 * 1024 * 1024))  # 5MB
KEEP_LINES=1000

LOG_FILES=(
  "$REPO_ROOT/bot/bot.log"
  "$REPO_ROOT/bot/launchd_stdout.log"
  "$REPO_ROOT/bot/launchd_stderr.log"
  "$REPO_ROOT/bot_a6/bot_a6.log"
  "$REPO_ROOT/bot_a6/launchd_stdout.log"
  "$REPO_ROOT/bot_a6/launchd_stderr.log"
)

rotated=0
for f in "${LOG_FILES[@]}"; do
  [ -f "$f" ] || continue
  size=$(stat -f%z "$f" 2>/dev/null || stat -c%s "$f" 2>/dev/null)
  if [ "$size" -gt "$MAX_SIZE" ]; then
    tail -n "$KEEP_LINES" "$f" > "${f}.tmp" && mv "${f}.tmp" "$f"
    new_size=$(stat -f%z "$f" 2>/dev/null || stat -c%s "$f" 2>/dev/null)
    echo "[rotate] $(basename "$f"): ${size} → ${new_size} bytes (kept last ${KEEP_LINES} lines)"
    rotated=$((rotated + 1))
  fi
done

if [ "$rotated" -eq 0 ]; then
  echo "[rotate] All logs under ${MAX_SIZE} bytes, nothing to do."
else
  echo "[rotate] Rotated ${rotated} file(s)."
fi
