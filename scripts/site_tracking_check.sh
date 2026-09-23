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

# --verify-clarity-id <id>:驗「Owner 給的 Clarity 專案識別碼是不是真的活的」。
#   做法=抓 https://www.clarity.ms/tag/<id>。真專案會回 200 且內容是 clarity 的 tag 腳本;
#   假的/打錯的 id 會回非 200 或空內容。
#   這一步跟「站上有沒有裝」是兩件事,不可混講:id 有效 ≠ 已佈碼。
if [ "${1:-}" = "--verify-clarity-id" ]; then
  CID="${2:-}"
  if [ -z "$CID" ]; then
    echo "[ERR] --verify-clarity-id 要帶專案識別碼"
    exit 2
  fi
  echo "=== 驗 Clarity 專案識別碼:$CID"
  tmp=$(mktemp)
  code=$(curl -s -L --max-time 30 -o "$tmp" -w '%{http_code}' "https://www.clarity.ms/tag/${CID}")
  size=$(wc -c < "$tmp" | tr -d ' ')
  hit=$(grep -c "$CID" "$tmp")
  echo "HTTP=$code BYTES=$size 內容含該 id 次數=$hit"
  if [ "$code" = "200" ] && [ "$size" -gt 200 ]; then
    echo "  → 識別碼有效(clarity 回得出 tag 腳本)。注意:這只證明 id 是真的,不代表站上已佈碼。"
    rm -f "$tmp"
    exit 0
  fi
  echo "  ✗ 識別碼查無有效回應,先跟 Owner 核對字串再佈碼"
  rm -f "$tmp"
  exit 3
fi

# --verify-gtm <GTM-ID> <要找的字串>:GTM 注入的標籤「不會」出現在頁面 HTML 裡,
#   curl 頁面永遠看不到,所以不能用頁面結果判「沒裝」。真正的證據在容器腳本
#   https://www.googletagmanager.com/gtm.js?id=<GTM-ID> —— 而且只有「已發布」的版本才會進去。
#   容器裡找得到 = 代碼層真的通了;找不到 = 標籤存了但沒發布,或裝在別的容器。
if [ "${1:-}" = "--verify-gtm" ]; then
  GID="${2:-}"; NEEDLE="${3:-}"
  if [ -z "$GID" ] || [ -z "$NEEDLE" ]; then
    echo "[ERR] 用法: --verify-gtm <GTM-ID> <要找的字串>"
    exit 2
  fi
  echo "=== 驗 GTM 容器是否已發布含「${NEEDLE}」的標籤:$GID"
  tmp=$(mktemp)
  code=$(curl -s -L --max-time 30 -o "$tmp" -w '%{http_code}' "https://www.googletagmanager.com/gtm.js?id=${GID}")
  size=$(wc -c < "$tmp" | tr -d ' ')
  hit=$(grep -c "$NEEDLE" "$tmp")
  cla=$(grep -c "clarity" "$tmp")
  echo "HTTP=$code BYTES=$size 含「${NEEDLE}」次數=$hit 含 clarity 字樣次數=$cla"
  rm -f "$tmp"
  if [ "$code" = "200" ] && [ "$hit" -gt 0 ]; then
    echo "  → 已發布:容器裡找得到,代碼層通了(資料層仍要看後台即時報表)"
    exit 0
  fi
  echo "  ✗ 容器裡找不到。可能=標籤存了但容器沒按「發布」,或裝到別的容器/其他路徑去了"
  exit 3
fi

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
