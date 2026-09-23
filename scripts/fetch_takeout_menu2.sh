#!/bin/bash
# fetch_takeout_menu2.sh (v3) — 唯讀下載 google.site「預約外帶取餐」頁的菜單圖片
# v2 教訓：HTML 抽出的 sitesv 網址「本身已含 =wXXXX 簽名後綴」,再硬加 =w1600
#          會破壞簽名 → 403(圖示網址無後綴故存活)。
# v3 作法：網址原樣使用不加後綴;每張記 HTTP code;同 session cookie+referer。
# 安全邊界：只讀公開頁面、只寫 data/takeout-menu/,不需登入、不碰雲端。
set -uo pipefail

OUT="$(cd "$(dirname "$0")/.." && pwd)/data/takeout-menu"
mkdir -p "$OUT"
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
PAGE="https://sites.google.com/view/maplabkitchen/%E9%A0%90%E7%B4%84%E5%A4%96%E5%B8%B6%E5%8F%96%E9%A4%90"
JAR="$OUT/.cookies.txt"
HTML="$OUT/.page.html"

rm -f "$JAR"
curl -sL --max-time 90 -A "$UA" -c "$JAR" -o "$HTML" "$PAGE"
echo "[info] 頁面已抓: $(wc -c < "$HTML") bytes"

URLS=$(sed 's/\\u003d/=/g' "$HTML" \
  | grep -o 'https://lh[0-9]\.googleusercontent\.com/[A-Za-z0-9_/=-]*' \
  | sort -u)

if [ -z "$URLS" ]; then
  echo "[error] 頁面裡找不到 googleusercontent 圖址"
  exit 1
fi
echo "[info] 找到 $(echo "$URLS" | wc -l | tr -d ' ') 個圖址"

i=0
ok=0
while IFS= read -r url; do
  [ -z "$url" ] && continue
  i=$((i+1))
  n=$(printf "img_%02d" "$i")
  code=$(curl -sL --max-time 90 -A "$UA" -b "$JAR" -e "$PAGE" \
          -o "$OUT/$n" -w "%{http_code}" "$url" || echo curl_fail)
  t=$(file -b --mime-type "$OUT/$n" 2>/dev/null || echo unknown)
  sz=$(wc -c < "$OUT/$n" | tr -d ' ')
  echo "[$n] http=$code mime=$t bytes=$sz  ${url:0:60}..."
  case "$t" in
    image/png)  mv "$OUT/$n" "$OUT/$n.png";  ok=$((ok+1)) ;;
    image/jpeg) mv "$OUT/$n" "$OUT/$n.jpg";  ok=$((ok+1)) ;;
    image/webp) mv "$OUT/$n" "$OUT/$n.webp"; ok=$((ok+1)) ;;
    image/gif)  mv "$OUT/$n" "$OUT/$n.gif";  ok=$((ok+1)) ;;
    *)          rm -f "$OUT/$n" ;;
  esac
done <<< "$URLS"

rm -f "$JAR"
echo ""
echo "完成：$ok/$i 張圖片已落地 $OUT"
ls -la "$OUT"
