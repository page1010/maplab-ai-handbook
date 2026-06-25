#!/usr/bin/env bash
# log_rotate.sh — MAPLAB log rotate job (T-HQ-001 P5)
# 執行時機：每週一 03:00（由 com.maplab.log-rotate.plist 觸發）
# 安全原則：只 rename+gzip，不刪任何 <7 天的檔案

set -euo pipefail

REPO_ROOT="/Users/pagemacmini/maplab-ai-handbook"
HERMES_LOG="${HOME}/.hermes/logs"
MAX_SIZE_BYTES=10485760  # 10 MB
KEEP_ROTATED=10          # 每個目錄保留最多 10 個壓縮版本
LOG_FILE="${REPO_ROOT}/logs/log_rotate_run.log"
DATE=$(date +%Y%m%d)

mkdir -p "${REPO_ROOT}/logs"

log() {
  echo "[$(date '+%Y-%m-%dT%H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

rotate_if_large() {
  local file="$1"
  if [[ ! -f "$file" ]]; then return 0; fi
  local size
  size=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null || echo 0)
  if (( size > MAX_SIZE_BYTES )); then
    local rotated="${file%.md}.${DATE}.md"
    mv "$file" "$rotated"
    gzip "$rotated"
    log "rotated: $file (${size} bytes) → ${rotated}.gz"
  fi
}

prune_old_rotated() {
  local dir="$1"
  local pattern="$2"
  # delete oldest beyond KEEP_ROTATED
  while IFS= read -r f; do
    rm -f "$f"
    log "pruned old rotated: $f"
  done < <(find "$dir" -name "${pattern}" -type f | sort | head -n -${KEEP_ROTATED})
}

log "=== log_rotate start ==="

# bot telegram logs
for f in "${REPO_ROOT}/data/telegram-logs/"*.md; do
  rotate_if_large "$f"
done
prune_old_rotated "${REPO_ROOT}/data/telegram-logs" "*.gz"

# bot main log
rotate_if_large "${REPO_ROOT}/bot/bot.log"
rotate_if_large "${REPO_ROOT}/bot/launchd_stdout.log"
rotate_if_large "${REPO_ROOT}/bot/launchd_stderr.log"
prune_old_rotated "${REPO_ROOT}/bot" "*.gz"

# hermes logs
if [[ -d "$HERMES_LOG" ]]; then
  for f in "${HERMES_LOG}/"*.log; do
    rotate_if_large "$f"
  done
  prune_old_rotated "$HERMES_LOG" "*.gz"
fi

log "=== log_rotate done ==="
