#!/usr/bin/env bash
# notify_group.sh — 推送一則訊息到股票討論群（Telegram group chat）
# 模式與 notify_owner.sh 相同,共用 bot/.env 憑證;僅目的地改為群組 chat_id。
# 用途:A0/Fable5 對「群組派工」的成果回交(Owner 12:41 派工模式:各自努力後提交報告)。
# 邊界:僅限回交 Owner 在群組指派的任務成果;一般群聊維持靜默(能力測試 D)。
#
# 用法:
#   bash scripts/notify_group.sh "訊息內容" [chat_id]
# chat_id 預設 -5589898264(股票討論群,見 claude-daily-operations/state/a0_groups.json)。

set -euo pipefail
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ENV_FILE="$REPO_ROOT/bot/.env"

MESSAGE="${1:-}"
GROUP_CHAT_ID="${2:--5589898264}"
if [[ -z "$MESSAGE" ]]; then
  echo "❌ 用法:bash scripts/notify_group.sh \"訊息內容\" [chat_id]"
  exit 1
fi

if [[ ! -f "$ENV_FILE" ]]; then
  echo "❌ 找不到 $ENV_FILE,無法推送"
  exit 1
fi

TELEGRAM_BOT_TOKEN=$(grep -E '^TELEGRAM_BOT_TOKEN=' "$ENV_FILE" | head -1 | cut -d= -f2-)
if [[ -z "$TELEGRAM_BOT_TOKEN" ]]; then
  echo "❌ bot/.env 缺 TELEGRAM_BOT_TOKEN"
  exit 1
fi

# Telegram 單則上限 4096 字元,超過就分段送
MAX=4000
TEXT="$MESSAGE"
while [[ -n "$TEXT" ]]; do
  CHUNK="${TEXT:0:$MAX}"
  TEXT="${TEXT:$MAX}"
  RESP=$(curl -sS -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
    --data-urlencode "chat_id=${GROUP_CHAT_ID}" \
    --data-urlencode "text=${CHUNK}")
  if ! printf '%s' "$RESP" | grep -q '"ok":true'; then
    echo "❌ 群組推送失敗:$(printf '%s' "$RESP" | head -c 300)"
    exit 1
  fi
done
echo "✅ 已推送到群組(chat_id=${GROUP_CHAT_ID})"
