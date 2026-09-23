#!/bin/bash
# process_takeout_menu.sh — 菜單圖後處理:
# 1) menu_09(PARTY SNACKS 菜單)切成放大 tile,確認有無單價小字
# 2) 另抓「服務內容訂購須知」頁圖片(價目可能在該頁)
# 唯讀下載+本地影像處理,不碰雲端資料。
set -euo pipefail

BASE="$(cd "$(dirname "$0")/.." && pwd)/data/takeout-menu"
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"

# --- 1) 菜單圖切 tile 放大 ---
/usr/bin/python3 - "$BASE" <<'PYEOF'
import sys, os
from PIL import Image
base = sys.argv[1]
src = os.path.join(base, "menu_09.png")
im = Image.open(src)
w, h = im.size
print(f"[info] menu_09 原始尺寸: {w}x{h}")
# 菜單卡在左半(約 0~52%),右半是照片;切 3 直欄 x 2 橫列,各放大 2 倍
menu = im.crop((0, 0, int(w*0.52), h))
mw, mh = menu.size
cols, rows = 3, 2
outdir = os.path.join(base, "tiles")
os.makedirs(outdir, exist_ok=True)
for r in range(rows):
    for c in range(cols):
        box = (mw*c//cols, mh*r//rows, mw*(c+1)//cols, mh*(r+1)//rows)
        t = menu.crop(box)
        t = t.resize((t.width*2, t.height*2), Image.LANCZOS)
        p = os.path.join(outdir, f"tile_r{r}c{c}.png")
        t.save(p)
        print(f"[info] {p} {t.size}")
PYEOF

# --- 2) 抓 服務內容訂購須知 頁 ---
OUT2="$BASE/terms"
mkdir -p "$OUT2"
PAGE2="https://sites.google.com/view/maplabkitchen/%E6%9C%8D%E5%8B%99%E5%85%A7%E5%AE%B9%E8%A8%82%E8%B3%BC%E9%A0%88%E7%9F%A5"
JAR="$OUT2/.cookies.txt"
HTML="$OUT2/.page.html"
rm -f "$JAR"
curl -sL --max-time 90 -A "$UA" -c "$JAR" -o "$HTML" "$PAGE2"
echo "[info] 訂購須知頁已抓: $(wc -c < "$HTML") bytes"
sed 's/\\u003d/=/g; s/\\\//\//g' "$HTML" \
  | grep -o 'https://lh3\.googleusercontent\.com/sitesv/[A-Za-z0-9_=-]*' \
  | sort -u > "$OUT2/.urls.txt"
N=$(wc -l < "$OUT2/.urls.txt" | tr -d ' ')
echo "[info] 訂購須知頁找到 $N 個圖址"
i=0; ok=0
while IFS= read -r url; do
  [ -z "$url" ] && continue
  i=$((i+1))
  n=$(printf "terms_%02d" "$i")
  if curl -sL --max-time 120 -A "$UA" -b "$JAR" -e "$PAGE2" -o "$OUT2/$n" "$url"; then
    t=$(file -b --mime-type "$OUT2/$n" 2>/dev/null || echo unknown)
    case "$t" in
      image/png)  mv "$OUT2/$n" "$OUT2/$n.png";  ok=$((ok+1)) ;;
      image/jpeg) mv "$OUT2/$n" "$OUT2/$n.jpg";  ok=$((ok+1)) ;;
      image/webp) mv "$OUT2/$n" "$OUT2/$n.webp"; ok=$((ok+1)) ;;
      *)          mv "$OUT2/$n" "$OUT2/$n.bin" ;;
    esac
  fi
done < "$OUT2/.urls.txt"
rm -f "$JAR"
ls -la "$OUT2"
echo "完成:訂購須知頁 $ok/$i 張圖片落地 $OUT2"
