#!/usr/bin/env bash
# notify_owner.sh — 即時推送一則訊息給 Owner（Telegram）
# 用途：checkpoint.sh --notify、或任何角色完成里程碑任務時，立即通知 Owner，
# 不必等每日 patrol-scheduled.sh。
#
# 用法：
#   bash scripts/notify_owner.sh "訊息內容"
#
# 讀 bot/.env 的 TELEGRAM_BOT_TOKEN / OWNER_CHAT_ID（跟 patrol-scheduled.sh 共用同一組憑證）。

set -euo pipefail
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ENV_FILE="$REPO_ROOT/bot/.env"

MESSAGE="${1:-}"
if [[ -z "$MESSAGE" ]]; then
  echo "❌ 用法：bash scripts/notify_owner.sh \"訊息內容\""
  exit 1
fi

if [[ ! -f "$ENV_FILE" ]]; then
  echo "❌ 找不到 $ENV_FILE，無法推送"
  exit 1
fi

TELEGRAM_BOT_TOKEN=$(grep -E '^TELEGRAM_BOT_TOKEN=' "$ENV_FILE" | head -1 | cut -d= -f2-)
OWNER_CHAT_ID=$(grep -E '^OWNER_CHAT_ID=' "$ENV_FILE" | head -1 | cut -d= -f2-)
OWNER_CHAT_ID="${OWNER_CHAT_ID:-1077768811}"

if [[ -z "$TELEGRAM_BOT_TOKEN" ]]; then
  echo "❌ bot/.env 找不到 TELEGRAM_BOT_TOKEN，無法推送"
  exit 1
fi

HTTP_CODE=$(curl -s -o /tmp/notify_owner_resp.json -w "%{http_code}" \
  "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
  -d "chat_id=${OWNER_CHAT_ID}" \
  --data-urlencode "text=${MESSAGE}")

if [[ "$HTTP_CODE" == "200" ]]; then
  echo "✅ 已推送給 Owner（chat_id=${OWNER_CHAT_ID}）"
else
  echo "❌ 推送失敗（HTTP ${HTTP_CODE}），回應："
  cat /tmp/notify_owner_resp.json 2>/dev/null
  exit 1
fi
