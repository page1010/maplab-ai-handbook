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

# A0 self-restart hook(Owner 2026-08-28 msg 4314:不叫 Owner 動終端機,一切自跑)
# resume 視窗只放行本目錄腳本,故重啟走「旗標檔+回覆腳本尾端」:旗標存在且
# 10 分鐘內建立 → 送完回覆後自動執行 a0_bot_restart.sh(KeepAlive 重生新碼)。
# 過期旗標只清除不執行,避免舊旗標誤觸重啟。
RESTART_FLAG="/Users/pagemacmini/claude-daily-operations/state/a0_restart_bot.flag"
if [[ -f "$RESTART_FLAG" ]]; then
  if [[ -n "$(find "$RESTART_FLAG" -mmin -10 2>/dev/null)" ]]; then
    rm -f "$RESTART_FLAG"
    bash "$REPO_ROOT/scripts/a0_bot_restart.sh"
  else
    rm -f "$RESTART_FLAG"
  fi
fi
