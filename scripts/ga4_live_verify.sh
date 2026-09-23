#!/usr/bin/env bash
# ga4_live_verify.sh — 自己親手驗一次:線上首頁到底有沒有追蹤碼
#
# 背景:win-01 在 drafts/win-01/ga4-clarity/INSTALL_PATH.md 回報「已用 curl 抓首頁 HTML 確認
# 有 gtag('config','G-GCK6LKMZ25')、GTM-T2Z52GP、GT-TWTP4CS、AW-5523160542,沒有 Clarity」。
# 依 CULTURE_DECISION_LOGIC.md 制度 D 第 4 條:別人回報的,在自己驗過之前只能說「它回報」。
# 這支就是自己驗的那一手。
#
# ⚠ 這支只能證明「代碼在頁面上」= 會送資料。
#    它【不能】證明「資料真的進到 GA4 報表」——那要登入 Google 後台看即時報表,
#    依紅線 agent 不碰 Owner 的 Google 帳號,那一步只有 Owner 本人做得到(30 秒)。
#    回報時兩件事要分開講,不得混為一談。
#
# 安全:只讀公開網頁,不帶 cookie、不登入、不寫任何東西到站上。
set -uo pipefail

URL="${1:-https://www.maplabkitchen.com/}"
TMP="$(mktemp -t ga4live.XXXXXX)"
trap 'rm -f "$TMP"' EXIT

echo "=== 抓公開首頁(不帶 cookie、不登入) ==="
echo "url=$URL"
HTTP="$(curl -sL --max-time 40 -A 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)' "$URL" -o "$TMP" -w '%{http_code}')"
BYTES="$(wc -c <"$TMP" | tr -d ' ')"
echo "http=$HTTP bytes=$BYTES"
if [ "$HTTP" != "200" ] || [ "$BYTES" -lt 2000 ]; then
  echo "FATAL: 抓不到頁面,無法查核。不要據此對 Owner 宣稱任何結論。"
  exit 1
fi

echo
echo "=== 逐項比對 win-01 的回報 ==="
hit() {
  local label="$1" pat="$2" expect="$3"
  local n
  n="$(grep -o -c -E "$pat" "$TMP" 2>/dev/null || true)"
  [ -z "$n" ] && n=0
  if [ "$n" -gt 0 ]; then got="在"; else got="不在"; fi
  if [ "$got" = "$expect" ]; then mark="一致"; else mark="⚠ 與回報不符"; fi
  printf '%-22s 出現 %-3s 次 -> %-4s (win-01 回報:%s) %s\n' "$label" "$n" "$got" "$expect" "$mark"
}

hit "GA4 G-GCK6LKMZ25"   'G-GCK6LKMZ25'   "在"
hit "GTM-T2Z52GP"        'GTM-T2Z52GP'    "在"
hit "GT-TWTP4CS"         'GT-TWTP4CS'     "在"
hit "Google Ads AW-"     'AW-5523160542'  "在"
hit "Microsoft Clarity"  'clarity\.ms|[^a-z]clarity[^a-z]' "不在"

echo
echo "=== 頁面上出現的所有 G- / GT- / GTM- / AW- 代號(去重,看有沒有第二組 GA4) ==="
grep -o -E '\b(G|GT|GTM|AW)-[A-Z0-9]{6,}\b' "$TMP" | sort -u

echo
echo "=== 結論 ==="
if grep -q 'G-GCK6LKMZ25' "$TMP"; then
  echo "PASS(代碼層):線上首頁確實掛著 GA4 G-GCK6LKMZ25,win-01 的回報屬實,我自己也驗過了。"
else
  echo "FAIL(代碼層):線上首頁找不到 G-GCK6LKMZ25。win-01 的回報與現況不符,要回頭查。"
fi
echo
echo "⚠ 仍未驗,而且我驗不了:"
echo "   「資料有沒有真的進到 GA4 報表」。代碼在 = 會送;有沒有收到要看後台即時報表。"
echo "   依紅線不碰 Owner 的 Google 帳號 → 這一步只有 Owner 本人能做:"
echo "   開 analytics.google.com → 報表 → 即時 → 同時用手機開一次首頁 → 看作用中使用者有沒有跳到 1。"
