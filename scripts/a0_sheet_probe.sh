#!/bin/bash
# a0_sheet_probe.sh — 唯讀探測：A4 外燴系統 Sheet 的分頁與品項資料（小肚肚案 4996/5002）
# 用途：1) 讀 ITEM_MASTER / PRICE_MASTER 尾列確認資料狀態
#       2) 順帶測 raw.githubusercontent 是否公開可達（Owner 超連結交付判斷）
# 唯讀、不寫雲端；token 只在 sheet_tail.py 內部流動，不 echo。
set -u
PY=/Users/pagemacmini/maplab-ai-handbook/bot/venv/bin/python
ST=/Users/pagemacmini/maplab-ai-handbook/scripts/sheet_tail.py
SID=1fn_woqYI_RY9ggGHVidB5SMygAzwe4CL_SOPLhe91Jg

# 2026-09-09 接通確認：實際分頁名（無 ITEM_MASTER/PRICE_MASTER；品項正典=Items 126列）
for TAB in Items QUOTE_DRAFT OrderLines TERMS_MASTER; do
  echo "=== TAB: $TAB ==="
  "$PY" "$ST" --sheet-id "$SID" --tab "$TAB" --rows 5 --show-cols ALL 2>&1 | head -12
done

echo "=== raw.githubusercontent reachability (public repo check) ==="
curl -s -o /dev/null -w "handbook raw http_code=%{http_code}\n" \
  "https://raw.githubusercontent.com/page1010/maplab-ai-handbook/chore/agent-login-governance-20260816/data/vendor-db/sent-log.md"
