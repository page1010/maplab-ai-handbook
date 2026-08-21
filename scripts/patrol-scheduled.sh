#!/usr/bin/env bash
# patrol-scheduled.sh — 定時巡查 + 推送結果到 Telegram
# 由 launchd 每天自動執行，也可手動：bash scripts/patrol-scheduled.sh
# 加 --dry-run 只顯示不推送

set -euo pipefail
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LOG_DIR="${MAPLAB_RUNTIME_LOG_DIR:-$REPO_ROOT/logs/runtime}"
LOG_FILE="$LOG_DIR/patrol-scheduled.log"
mkdir -p "$LOG_DIR"

# ── 載入 .env ──
ENV_FILE="$REPO_ROOT/bot/.env"
if [[ -f "$ENV_FILE" ]]; then
  # macOS bash 3.2 的 `source <(...)` 不會設定變數（2026-06-11 實測），改直接賦值
  TELEGRAM_BOT_TOKEN=$(grep -E '^TELEGRAM_BOT_TOKEN=' "$ENV_FILE" | head -1 | cut -d= -f2-)
  OWNER_CHAT_ID=$(grep -E '^OWNER_CHAT_ID=' "$ENV_FILE" | head -1 | cut -d= -f2-)
fi

BOT_TOKEN="${TELEGRAM_BOT_TOKEN:-}"
CHAT_ID="${OWNER_CHAT_ID:-1077768811}"

DRY_RUN=false
[[ "${1:-}" == "--dry-run" ]] && DRY_RUN=true

# ── 執行 patrol.sh ──
echo "[$(date '+%Y-%m-%d %H:%M:%S')] patrol-scheduled 開始" >> "$LOG_FILE"

RESULT=$(bash "$REPO_ROOT/scripts/patrol.sh" 2>&1) || true

# ── 獨立 grader：客觀 repo 健康關卡（T-A1-PATROL-GRADER-001）──
# patrol.sh 是任務狀態機（會給「差不多」的決策佇列）；grader 只看客觀產出物
# （衝突標記/未收尾 merge/失控落後/漂移/逾期）給 PASS/FAIL——獨立驗證者勝過自我批評。
set +e
GRADER=$(bash "$REPO_ROOT/scripts/patrol_grader.sh" 2>&1)
GRADER_RC=$?
set -e

# ── 加上時間戳標題（grader FAIL → 標題標 🔴，確保 Owner 一定看到、不被蓋章吃掉）──
if [[ "$GRADER_RC" -ne 0 ]]; then
  HEADER="🔴 每日自動巡查（repo 健康 FAIL，需處理）— $(date '+%Y-%m-%d %H:%M')"
else
  HEADER="📋 每日自動巡查 — $(date '+%Y-%m-%d %H:%M')"
fi
MESSAGE="$HEADER

$RESULT

── repo 健康關卡（獨立 grader）──
$GRADER"

# ── 存 log ──
echo "$MESSAGE" >> "$LOG_FILE"
echo "---" >> "$LOG_FILE"

# ── Hermes / Codex reaction packet ──
# 不呼叫 LLM、不吃 Claude、不改外部系統；只把巡查結果轉成 Hermes、
# Chrome Extension、Codex/A1/B1 可接手的 next-step packet 與面板資料。
BRIDGE_OUTPUT=$(printf '%s\n' "$MESSAGE" | python3 "$REPO_ROOT/tools/hermes_patrol_bridge.py" --repo "$REPO_ROOT" --stdin --quiet 2>&1) || {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] Hermes patrol bridge failed: $BRIDGE_OUTPUT" >> "$LOG_FILE"
}
if [[ -n "${BRIDGE_OUTPUT:-}" ]]; then
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] Hermes patrol bridge: $BRIDGE_OUTPUT" >> "$LOG_FILE"
fi

# ── 推送到 Telegram ──
if [[ "$DRY_RUN" == "true" ]]; then
  echo "[dry-run] 以下內容不會推送："
  echo "$MESSAGE"
  exit 0
fi

if [[ -z "$BOT_TOKEN" ]]; then
  echo "[ERROR] 找不到 TELEGRAM_BOT_TOKEN，無法推送" >> "$LOG_FILE"
  exit 1
fi

# 清掉無效 UTF-8 位元組（Telegram 會 400: strings must be encoded in UTF-8）
MESSAGE=$(printf '%s' "$MESSAGE" | iconv -f UTF-8 -t UTF-8 -c)

# Telegram 訊息上限 4096 字，超過就截斷
if [[ ${#MESSAGE} -gt 4000 ]]; then
  MESSAGE="${MESSAGE:0:3990}

...（已截斷）"
fi

HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
  "https://api.telegram.org/bot${BOT_TOKEN}/sendMessage" \
  -d "chat_id=${CHAT_ID}" \
  --data-urlencode "text=${MESSAGE}" \
  --max-time 30)

if [[ "$HTTP_CODE" == "200" ]]; then
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] 推送成功" >> "$LOG_FILE"
else
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] 推送失敗 HTTP=$HTTP_CODE" >> "$LOG_FILE"
fi
