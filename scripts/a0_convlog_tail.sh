#!/bin/bash
# a0_convlog_tail.sh — 唯讀探測:LINE 收單管線活性檢查(5590)
# 只讀 CONVERSATION_LOG 尾列的 timestamp,source(sheet_tail.py 預設去識別欄),不碰客訊內容。
# 結果 append 到 ~/.maplab/a0_convlog_tail.log,並以【bot 代答】推播摘要給 Owner(比照 spread_alert 通道)。
# token 只在行程內流動,不 echo、不落檔。
set -u
PY=/Users/pagemacmini/maplab-ai-handbook/bot/venv/bin/python
ST=/Users/pagemacmini/maplab-ai-handbook/scripts/sheet_tail.py
SID=1fn_woqYI_RY9ggGHVidB5SMygAzwe4CL_SOPLhe91Jg
BOT_ENV=/Users/pagemacmini/maplab-ai-handbook/bot/.env
LOG="$HOME/.maplab/a0_convlog_tail.log"
ROWS="${1:-8}"

OUT="$("$PY" "$ST" --sheet-id "$SID" --tab CONVERSATION_LOG --rows "$ROWS" 2>&1)"
{
  echo "--- probe $(date '+%Y-%m-%d %H:%M:%S') ---"
  echo "$OUT"
} >> "$LOG"

TOKEN="$(grep '^TELEGRAM_BOT_TOKEN=' "$BOT_ENV" | cut -d= -f2-)"
CHAT="$(grep '^OWNER_CHAT_ID=' "$BOT_ENV" | cut -d= -f2-)"
if [[ -z "$TOKEN" || -z "$CHAT" ]]; then
  echo "[push skip] bot env missing keys" >> "$LOG"
  exit 0
fi

TAIL_LINES="$(echo "$OUT" | tail -6)"
if echo "$TAIL_LINES" | grep -q "2026-09"; then
  VERDICT="判讀:9 月仍有來訊進表,webhook 收單管線活著。"
elif echo "$OUT" | grep -qiE "error|denied|invalid|expired"; then
  VERDICT="判讀:讀取失敗(非管線問題,是探測通道問題),下輪人工查。"
else
  VERDICT="判讀:尾列沒有 9 月時間戳,管線可能自 5/19 後斷線,下輪我查 webhook 佈署狀態。"
fi

MSG="【bot 代答・收單管線探測(5590)】CONVERSATION_LOG 尾列(只含時間/來源欄):
${TAIL_LINES}
${VERDICT}"

curl -s -o /dev/null -w "push http=%{http_code}\n" \
  -X POST "https://api.telegram.org/bot${TOKEN}/sendMessage" \
  --data-urlencode "chat_id=${CHAT}" \
  --data-urlencode "text=${MSG}" >> "$LOG" 2>&1
