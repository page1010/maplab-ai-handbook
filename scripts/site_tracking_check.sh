#!/usr/bin/env bash
# site_tracking_check.sh — 實查線上頁面的追蹤碼是否真的在 HTML 裡
#
# 用途:回答「GA4 / Clarity 通了嗎」的「代碼層」那一半。
#   代碼層 = 標籤有沒有出現在線上 HTML(這支腳本能查)
#   資料層 = 後台即時報表有沒有人數(要登入,這支腳本查不到,不得冒充)
#
# 用法: bash scripts/site_tracking_check.sh [URL ...]
#   不給參數就用預設清單。
#
# 退出碼: 0 = 全部頁面都抓得到 HTML(不代表標籤齊全,看輸出)
#         3 = 有頁面抓不到

set -uo pipefail

URLS=("$@")
if [ ${#URLS[@]} -eq 0 ]; then
  URLS=("https://maplabkitchen.com/")
fi

FAIL=0

for url in "${URLS[@]}"; do
  echo "=== $url"
  tmp=$(mktemp)
  code=$(curl -s -L --max-time 30 -A 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)' -o "$tmp" -w '%{http_code}' "$url")
  size=$(wc -c < "$tmp" | tr -d ' ')
  echo "HTTP=$code BYTES=$size"
  if [ "$code" != "200" ] || [ "$size" -lt 500 ]; then
    echo "  ✗ 抓不到頁面,以下判讀全部無效"
    FAIL=3
    rm -f "$tmp"
    continue
  fi

  # GA4 measurement id: G-XXXXXXX
  ga4=$(grep -oE 'G-[A-Z0-9]{8,12}' "$tmp" | sort -u | tr '\n' ' ')
  # GTM container: GTM-XXXXXX / GT-XXXXXXX
  gtm=$(grep -oE 'GT[M]?-[A-Z0-9]{6,12}' "$tmp" | sort -u | tr '\n' ' ')
  # Google Ads: AW-XXXXXXXXXX
  aw=$(grep -oE 'AW-[0-9]{9,12}' "$tmp" | sort -u | tr '\n' ' ')
  # Microsoft Clarity: clarity.ms 腳本 或 clarity project id
  clarity_host=$(grep -c 'clarity\.ms' "$tmp")
  clarity_word=$(grep -ci 'clarity' "$tmp")

  echo "  GA4      : ${ga4:-(無)}"
  echo "  GTM/GT   : ${gtm:-(無)}"
  echo "  Ads      : ${aw:-(無)}"
  echo "  Clarity  : clarity.ms 出現 ${clarity_host} 次 / clarity 字樣 ${clarity_word} 次"

  if [ "$clarity_host" -gt 0 ]; then
    echo "  → Clarity 代碼層: 已安裝"
  else
    echo "  → Clarity 代碼層: 未安裝"
  fi
  if [ -n "$ga4" ]; then
    echo "  → GA4 代碼層: 已安裝(資料層仍需後台即時報表確認,本腳本查不到)"
  else
    echo "  → GA4 代碼層: 未安裝"
  fi
  rm -f "$tmp"
done

exit $FAIL
