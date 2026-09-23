#!/usr/bin/env bash
# a0_model_now.sh — 這個 A0 視窗「現在實際跑的是哪個模型」
#
# 由來:Owner 2026-09-23 msg 6029「你不是 fable5 你是 claude,底層模型是可切換的,
# 你們公司的限額,所以可能是 sonet opus 等」。
#
# 為什麼需要這支:
#   state/a0_session.json 寫的是 bot 呼叫 `claude -p --resume` 時「要求」的模型
#   (目前寫死 claude-fable-5,updated 停在 2026-08-22),那是願望不是事實。
#   真正跑的模型會因為額度而被換掉,事實只記在 session 逐字稿的每一則 assistant
#   訊息的 "model" 欄位裡。要回答「現在是誰在寫字」就得讀那裡。
#
# 用法: bash scripts/a0_model_now.sh [session_id]
# 輸出: 最後一則 assistant 訊息的模型 + 整條 session 的模型分佈

set -uo pipefail

SESSION_ID="${1:-3a3df70f-b5ce-4c45-9d85-6651d7022e4b}"
TRANSCRIPT="/Users/pagemacmini/.claude/projects/-Users-pagemacmini-Documents/${SESSION_ID}.jsonl"
SESSION_JSON="/Users/pagemacmini/claude-daily-operations/state/a0_session.json"

if [ ! -f "$TRANSCRIPT" ]; then
  echo "✗ 找不到逐字稿: $TRANSCRIPT"
  exit 3
fi

echo "=== session: $SESSION_ID"

echo "--- 現在實際跑的模型(逐字稿最後一則 assistant 的 model 欄)"
tail -200 "$TRANSCRIPT" | grep -oE '"model":"claude-[a-z0-9-]+"' | tail -1 \
  | sed 's/"model":"//; s/"$//' | sed 's/^/  /'

echo "--- 這條 session 用過的模型分佈(全檔統計)"
grep -oE '"model":"claude-[a-z0-9-]+"' "$TRANSCRIPT" \
  | sed 's/"model":"//; s/"$//' | sort | uniq -c | sort -rn | sed 's/^/  /'

echo "--- bot 呼叫時「要求」的模型(願望,不是事實)"
if [ -f "$SESSION_JSON" ]; then
  grep -oE '"model"[ ]*:[ ]*"[^"]+"' "$SESSION_JSON" | sed 's/^/  a0_session.json: /'
  grep -oE '"updated"[ ]*:[ ]*"[^"]+"' "$SESSION_JSON" | sed 's/^/  /'
else
  echo "  (讀不到 $SESSION_JSON)"
fi

echo
echo "判讀規則:兩者不一致時以逐字稿為準。a0_session.json 只說明 bot 想叫哪個模型,"
echo "額度用完時 CLI 會換模型,但那份檔不會自己更新。"
