#!/usr/bin/env bash
# a0_reply.sh — A0/Fable5 的標準回覆管道
#
# Owner 2026-08-22 21:37 決策：bot 在 A0 心跳存活時不再發「已收到」ack
# （洗板），改成靜默等待 A0_WAIT_TIMEOUT_S（bot/bot.py，預設 150 秒）；
# 這段期間 bot 是靠「A0 有沒有真的送出回覆」來判斷要不要自己接手代答，
# 而不是靠再收到一句 ack。判斷依據就是這支腳本寫的收據檔。
#
# Codex 審查（FABLE5_CONTINUITY_COGOV_REVIEW_20260822.md 路線 A）2026-08-22
# 最小項修正：收據從單純 {"ts":...,"len":...} 改成「成對」收據 ——
# 每一筆都帶 reply_to_inbox_ts，明確標出這筆回覆是在回哪一則 a0_inbox 訊息，
# 而不是只靠 ts >= 訊息時間的粗略比對（那樣快答的下一則訊息會誤配到前一則
# 還沒逾時的等待）。bot/bot.py 的 _a0_has_replied_for() 現在用
# reply_to_inbox_ts 做精確比對。
#
# A0 之後回覆 Owner 一律呼叫本腳本，而不要直接呼叫 notify_owner.sh：
#   1) 呼叫 notify_owner.sh 把文字實際送出去（Telegram）
#   2) 送出成功後，在 A0_REPLIES_FILE 追加一筆收據
#      {"ts":<epoch 秒>,"reply_to_inbox_ts":"<對應的 a0_inbox ts>",
#       "message_id":<a0_inbox 訊息的 Telegram message_id，若有；否則 null>,
#       "output_hash":"<回覆文字的 sha256>","len":<字數>}
#
# bot/bot.py 的 handle_message() 在 Owner 訊息進來、且 A0 心跳存活時，會記下
# 該則訊息的 inbox ts（reply_to_inbox_ts）並等待最多 A0_WAIT_TIMEOUT_S；期間
# 只要這個收據檔出現 reply_to_inbox_ts 精確吻合的一筆，就代表 A0 真的接住了
# 這一則訊息，bot 什麼都不做；逾時仍沒有吻合的收據，bot 視為 A0 沒接到，改用
# fresh-context relay（或 `claude -p --resume <A0_SESSION_ID>`）接續代答
# （見 bot/bot.py 的 _a0_resume_or_fallback）。
#
# 用法：
#   bash scripts/a0_reply.sh "回覆文字" [reply_to_inbox_ts]
#
# reply_to_inbox_ts 省略時，預設取 A0_INBOX_FILE 最後一則訊息的 "ts" 欄位
# （並順便帶上該則的 message_id，如果有的話）。多輪對話、或要明確回覆某一
# 則較早的訊息時，請明確傳入第二參數。

set -euo pipefail
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
REPLIES_FILE="${A0_REPLIES_FILE:-/Users/pagemacmini/claude-daily-operations/state/a0_replies.jsonl}"
INBOX_FILE="${A0_INBOX_FILE:-/Users/pagemacmini/claude-daily-operations/state/a0_inbox.jsonl}"

MESSAGE="${1:-}"
REPLY_TO_INBOX_TS="${2:-}"

if [[ -z "$MESSAGE" ]]; then
  echo "❌ 用法：bash scripts/a0_reply.sh \"回覆文字\" [reply_to_inbox_ts]"
  exit 1
fi

MESSAGE_ID_JSON="null"
if [[ -z "$REPLY_TO_INBOX_TS" ]]; then
  if [[ -f "$INBOX_FILE" ]]; then
    LAST_LINE=$(tail -n 1 "$INBOX_FILE" 2>/dev/null || true)
    if [[ -n "$LAST_LINE" ]]; then
      REPLY_TO_INBOX_TS=$(printf '%s' "$LAST_LINE" | jq -r '.ts // empty' 2>/dev/null || true)
      MID=$(printf '%s' "$LAST_LINE" | jq -r 'if (.message_id? != null) then .message_id else empty end' 2>/dev/null || true)
      if [[ -n "$MID" ]]; then
        MESSAGE_ID_JSON="$MID"
      fi
    fi
  fi
fi

if [[ -z "$REPLY_TO_INBOX_TS" ]]; then
  echo "❌ 找不到可對應的 a0_inbox 訊息，請明確傳入 reply_to_inbox_ts 第二參數" >&2
  echo "   用法：bash scripts/a0_reply.sh \"回覆文字\" \"<inbox ts>\"" >&2
  exit 1
fi

bash "$REPO_ROOT/scripts/notify_owner.sh" "$MESSAGE"

mkdir -p "$(dirname "$REPLIES_FILE")"
TS=$(date +%s)
LEN=${#MESSAGE}
OUTPUT_HASH=$(printf '%s' "$MESSAGE" | shasum -a 256 | awk '{print $1}')

jq -nc \
  --argjson ts "$TS" \
  --arg reply_to_inbox_ts "$REPLY_TO_INBOX_TS" \
  --argjson message_id "$MESSAGE_ID_JSON" \
  --arg output_hash "$OUTPUT_HASH" \
  --argjson len "$LEN" \
  '{ts:$ts, reply_to_inbox_ts:$reply_to_inbox_ts, message_id:$message_id, output_hash:$output_hash, len:$len}' \
  >> "$REPLIES_FILE"

echo "✅ 已記錄 A0 回覆收據 → $REPLIES_FILE (reply_to_inbox_ts=$REPLY_TO_INBOX_TS)"
