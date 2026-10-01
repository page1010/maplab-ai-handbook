#!/usr/bin/env bash
# a0_send_photo.sh — 送一張圖給 Owner(Telegram sendPhoto / sendDocument)
#
# 由來:Owner msg 2026-10-01T18:07:33「sheet連結有一個問題,我看不到縮圖,
# telegram 呈現的驗收方式要在討論一下如何優化」。
# 真因之一:這條線的回覆管道 notify_owner.sh 只會 sendMessage 純文字,
# 從來沒有送圖的能力;而 Google Sheet 的連結需要登入,Telegram 的預覽爬蟲
# 只會拿到登入頁,所以不論連結怎麼貼都不會有縮圖。要讓 Owner 在 Telegram 裡
# 直接看到東西,只能自己把內容畫成圖送過去。
#
# 用法:
#   bash scripts/a0_send_photo.sh <圖檔> [說明文字] [reply_to_message_id] [doc]
#   第四個參數給 doc = 改走 sendDocument(不被 Telegram 壓縮,小字才看得清楚)
#
# 安全:權杖只在本腳本內流動,不 echo、不入 commit;對外只印 HTTP 狀態碼與檔名。
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ENV_FILE="$REPO_ROOT/bot/.env"

PHOTO="${1:-}"
CAPTION="${2:-}"
REPLY_TO_MESSAGE_ID="${3:-}"
MODE="${4:-photo}"

if [[ -z "$PHOTO" || ! -f "$PHOTO" ]]; then
  echo "❌ 用法:bash scripts/a0_send_photo.sh <圖檔> [說明文字] [reply_to_message_id] [doc]" >&2
  exit 1
fi
if [[ ! -f "$ENV_FILE" ]]; then
  echo "❌ 找不到 bot/.env,無法推送" >&2
  exit 1
fi

TELEGRAM_BOT_TOKEN=$(grep -E '^TELEGRAM_BOT_TOKEN=' "$ENV_FILE" | head -1 | cut -d= -f2-)
OWNER_CHAT_ID=$(grep -E '^OWNER_CHAT_ID=' "$ENV_FILE" | head -1 | cut -d= -f2-)
OWNER_CHAT_ID="${OWNER_CHAT_ID:-1077768811}"
if [[ -z "$TELEGRAM_BOT_TOKEN" ]]; then
  echo "❌ bot/.env 找不到 TELEGRAM_BOT_TOKEN,無法推送" >&2
  exit 1
fi

if [[ "$MODE" == "doc" ]]; then
  API=sendDocument; FIELD=document
else
  API=sendPhoto; FIELD=photo
fi

CURL_ARGS=(-F "chat_id=${OWNER_CHAT_ID}" -F "${FIELD}=@${PHOTO}")
if [[ -n "$CAPTION" ]]; then
  CURL_ARGS+=(-F "caption=${CAPTION}")
fi
if [[ -n "$REPLY_TO_MESSAGE_ID" ]]; then
  CURL_ARGS+=(-F "reply_to_message_id=${REPLY_TO_MESSAGE_ID}" -F "allow_sending_without_reply=true")
fi

HTTP_CODE=$(curl -s -o /tmp/a0_send_photo_resp.json -w "%{http_code}" \
  "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/${API}" "${CURL_ARGS[@]}")

if [[ "$HTTP_CODE" == "200" ]]; then
  echo "✅ 已送出 ${API}:$(basename "$PHOTO")(chat_id=${OWNER_CHAT_ID})"
else
  echo "❌ 送出失敗(HTTP ${HTTP_CODE})"
  # 回應可能含 chat_id,但不含權杖;仍只印 description 欄
  /usr/bin/python3 -c "import json,sys;d=json.load(open('/tmp/a0_send_photo_resp.json'));print('描述:',d.get('description'))" 2>/dev/null || true
  exit 1
fi
