#!/usr/bin/env bash
# a0_reply.sh — A0/Fable5 的標準回覆管道
#
# Owner 2026-08-22 21:37 決策：bot 在 A0 心跳存活時不再發「已收到」ack
# （洗板），改成靜默等待 A0_WAIT_TIMEOUT_S（bot/bot.py，預設 150 秒）；
# 這段期間 bot 是靠「A0 有沒有真的送出回覆」來判斷要不要自己接手代答，
# 而不是靠再收到一句 ack。判斷依據就是這支腳本寫的收據檔。
#
# A0 之後回覆 Owner 一律呼叫本腳本，而不要直接呼叫 notify_owner.sh：
#   1) 呼叫 notify_owner.sh 把文字實際送出去（Telegram）
#   2) 送出成功後，在 A0_REPLIES_FILE 追加一筆收據
#      {"ts":<epoch 秒>,"len":<字數>}
#
# bot/bot.py 的 handle_message() 在 Owner 訊息進來、且 A0 心跳存活時，會記下
# 訊息時間並等待最多 A0_WAIT_TIMEOUT_S；期間只要這個收據檔出現
# ts >= 訊息時間的一筆，就代表 A0 真的接住了，bot 什麼都不做；逾時仍沒有
# 收據，bot 視為 A0 沒接到，改用 `claude -p --resume <A0_SESSION_ID>`
# 接續 A0 的 session 自動代答（見 bot/bot.py 的 _a0_resume_or_fallback）。
#
# 用法：
#   bash scripts/a0_reply.sh "回覆文字"

set -euo pipefail
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
REPLIES_FILE="${A0_REPLIES_FILE:-/Users/pagemacmini/claude-daily-operations/state/a0_replies.jsonl}"

MESSAGE="${1:-}"
if [[ -z "$MESSAGE" ]]; then
  echo "❌ 用法：bash scripts/a0_reply.sh \"回覆文字\""
  exit 1
fi

bash "$REPO_ROOT/scripts/notify_owner.sh" "$MESSAGE"

mkdir -p "$(dirname "$REPLIES_FILE")"
TS=$(date +%s)
LEN=${#MESSAGE}
printf '{"ts":%s,"len":%s}\n' "$TS" "$LEN" >> "$REPLIES_FILE"
echo "✅ 已記錄 A0 回覆收據 → $REPLIES_FILE"
