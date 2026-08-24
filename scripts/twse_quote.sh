#!/usr/bin/env bash
# twse_quote.sh — 台股官方即時/收盤查價(TWSE MIS API,免金鑰)
# SOP 配套:docs/RESEARCH_PRICE_FRESHNESS_SOP.md —— 研究報告引用台股價格前必跑。
# 用法:
#   bash scripts/twse_quote.sh 2392 2603 2609          # 上市
#   bash scripts/twse_quote.sh otc_5274 otc_3105       # 上櫃加 otc_ 前綴
# 輸出:code|名稱|最新/收盤|昨收|漲跌%|資料日期|時間(13:30:00=收盤價)
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "用法:bash scripts/twse_quote.sh <代碼> [代碼...](上櫃加 otc_ 前綴)" >&2
  exit 1
fi

EX_CH=""
for CODE in "$@"; do
  if [[ "$CODE" == otc_* ]]; then
    EX_CH+="otc_${CODE#otc_}.tw|"
  else
    EX_CH+="tse_${CODE}.tw|"
  fi
done
EX_CH="${EX_CH%|}"

RESP=$(curl -sS "https://mis.twse.com.tw/stock/api/getStockInfo.jsp?ex_ch=${EX_CH}&json=1&delay=0")

if ! printf '%s' "$RESP" | jq -e '.msgArray | length > 0' >/dev/null 2>&1; then
  echo "❌ 查無資料或 API 異常:$(printf '%s' "$RESP" | head -c 200)" >&2
  exit 1
fi

printf '%s\n' "code|名稱|最新價|昨收|漲跌%|資料日期|時間"
printf '%s' "$RESP" | jq -r '.msgArray[] |
  (if (.z // "-") == "-" then (.y // "-") else .z end) as $px |
  [ .c, .n, $px, .y,
    (if ($px != "-" and .y != null and .y != "-" and (.y|tonumber) != 0)
     then ((($px|tonumber) - (.y|tonumber)) / (.y|tonumber) * 1000 | round / 10 | tostring) + "%"
     else "-" end),
    .d, .t ] | join("|")'
echo ""
echo "資料源:TWSE MIS(官方)。時間 13:30:00 = 當日收盤;盤中為即時價。引用時照 SOP 標資料日期。"
