#!/usr/bin/env bash
# a0_reply_thread_check.sh — 驗證「回覆會引用 Owner 原訊息」這條管道沒壞
#
# 由來：Owner 2026-09-22 msg 5882「當我跟他溝通順便檢查他回覆我telegram 只看得到
# 成果和單向對他說話，沒有辦法溝通了」。成因查到兩處：
#   1) notify_owner.sh 的 sendMessage 從來沒帶 reply_to_message_id
#      → 每則回覆都是獨立訊息，Telegram 上看不出在回哪一句
#   2) a0_reply.sh 只在「ts 省略」時才去查 message_id，而 A0 回覆一律明確帶 ts
#      → message_id 永遠是 null，連收據都沒記到
# 修法：a0_reply.sh 改成不論 ts 從哪來都回頭查 message_id，傳給 notify_owner.sh
# 當引用目標；查不到就照舊送獨立訊息（fail-soft，不給回覆管道新增失敗點）。
#
# 本腳本不送任何訊息，只做語法檢查與 message_id 反查的乾跑。
# 用法：bash scripts/a0_reply_thread_check.sh
set -uo pipefail
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
INBOX_FILE="${A0_INBOX_FILE:-/Users/pagemacmini/claude-daily-operations/state/a0_inbox.jsonl}"
FAIL=0

echo "=== a0 reply threading check $(date '+%Y-%m-%d %H:%M:%S') ==="

echo "--- 語法檢查 ---"
for s in scripts/a0_reply.sh scripts/notify_owner.sh scripts/a0_reply_from_file.sh; do
  if bash -n "$REPO_ROOT/$s" 2>&1; then
    echo "OK   $s"
  else
    echo "FAIL $s"
    FAIL=1
  fi
done

echo "--- notify_owner.sh 必須真的會帶 reply_to_message_id ---"
if grep -q "reply_to_message_id" "$REPO_ROOT/scripts/notify_owner.sh"; then
  echo "OK   sendMessage 有 reply_to_message_id 參數"
else
  echo "FAIL sendMessage 沒帶 reply_to_message_id：回覆仍是單向獨立訊息"
  FAIL=1
fi
if grep -q "allow_sending_without_reply" "$REPO_ROOT/scripts/notify_owner.sh"; then
  echo "OK   有 allow_sending_without_reply（原訊息不在時仍送得出去）"
else
  echo "FAIL 少了 allow_sending_without_reply：引用失敗會整則發不出去"
  FAIL=1
fi

echo "--- message_id 反查乾跑（用 inbox 最後三則，不送訊息）---"
if [[ ! -f "$INBOX_FILE" ]]; then
  echo "SKIP 找不到 inbox：$INBOX_FILE"
else
  TS_LIST=$(tail -n 3 "$INBOX_FILE" | jq -r '.ts // empty' 2>/dev/null)
  if [[ -z "$TS_LIST" ]]; then
    echo "FAIL inbox 尾段抓不到 ts"
    FAIL=1
  fi
  while IFS= read -r ts; do
    [[ -z "$ts" ]] && continue
    MID=$(jq -r --arg ts "$ts" \
      'select(.ts == $ts) | if (.message_id? != null) then .message_id else empty end' \
      "$INBOX_FILE" 2>/dev/null | tail -n 1)
    if [[ -n "$MID" ]]; then
      # 大括號不可省：$MID 後面接全形括號會被當成變數名的一部分（set -u 會炸）
      echo "OK   ${ts} -> message_id ${MID}（回覆會引用這一則）"
    else
      echo "WARN ${ts} -> 查無 message_id（照舊送獨立訊息，不算壞）"
    fi
  done <<<"$TS_LIST"
fi

echo "--- 結果 ---"
if [[ "$FAIL" == "0" ]]; then
  echo "PASS 回覆引用管道正常"
else
  echo "FAIL 回覆引用管道有問題，見上面 FAIL 行"
fi
echo "=== end ==="
exit "$FAIL"
