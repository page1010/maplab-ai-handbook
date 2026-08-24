#!/usr/bin/env bash
# a0_reply_from_file.sh — 從檔案讀回覆內容,轉呼叫 a0_reply.sh
# 用途:長訊息/多行訊息先落檔再送,避免命令列引號地獄;排程腳本也可用。
# 用法:bash scripts/a0_reply_from_file.sh <message_file> [reply_to_inbox_ts]
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

MSG_FILE="${1:-}"
REPLY_TO_INBOX_TS="${2:-}"

if [[ -z "$MSG_FILE" || ! -f "$MSG_FILE" ]]; then
  echo "❌ 用法:bash scripts/a0_reply_from_file.sh <message_file> [reply_to_inbox_ts]" >&2
  exit 1
fi

MESSAGE="$(cat "$MSG_FILE")"
if [[ -z "$MESSAGE" ]]; then
  echo "❌ 訊息檔是空的:$MSG_FILE" >&2
  exit 1
fi

if [[ -n "$REPLY_TO_INBOX_TS" ]]; then
  bash "$REPO_ROOT/scripts/a0_reply.sh" "$MESSAGE" "$REPLY_TO_INBOX_TS"
else
  bash "$REPO_ROOT/scripts/a0_reply.sh" "$MESSAGE"
fi
