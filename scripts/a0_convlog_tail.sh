#!/bin/bash
# a0_convlog_tail.sh — 唯讀探測:LINE 收單管線活性檢查(5590)
# 只印 CONVERSATION_LOG 尾列的 timestamp,source(sheet_tail.py 預設去識別欄),不印客訊內容。
set -u
PY=/Users/pagemacmini/maplab-ai-handbook/bot/venv/bin/python
ST=/Users/pagemacmini/maplab-ai-handbook/scripts/sheet_tail.py
SID=1fn_woqYI_RY9ggGHVidB5SMygAzwe4CL_SOPLhe91Jg
LOG="$HOME/.maplab/a0_convlog_tail.log"
{
  echo "--- probe $(date '+%Y-%m-%d %H:%M:%S') ---"
  "$PY" "$ST" --sheet-id "$SID" --tab CONVERSATION_LOG --rows "${1:-6}"
} >> "$LOG" 2>&1
