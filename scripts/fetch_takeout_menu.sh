#!/bin/bash
# fetch_takeout_menu.sh v3 — 唯讀下載 google.site「預約外帶取餐」頁的菜單圖片
# v1 教訓:sitesv 簽名圖址綁 session,離線引用他人 session 的 URL 會 403。
# v2 教訓:對已含 =wXXXX 尺寸參數的 URL 再硬加 =w1600 會弄壞簽名 → 403;
#          成功抓到的只有社群圖示。
# v3 作法:同 session 抓頁面 → URL 原樣使用(不改參數) → 同 cookie 下載;
#          另存 URL 清單供除錯。
set -euo pipefail

OUT="$(cd "$(dirname "$0")/.." && pwd)/data/takeout-menu"
mkdir -p "$OUT"
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
PAGE="https://sites.google.com/view/maplabkitchen/%E9%A0%90%E7%B4%84%E5%A4%96%E5%B8%B6%E5%8F%96%E9%A4%90"
JAR="$OUT/.cookies.txt"
HTML="$OUT/.page.html"

MODE="${1:-full}"   # full=抓+處理, tile-only=只做本地切圖(不重抓,免得檔名重新洗牌)

if [ "$MODE" = "tile-only" ]; then
  echo "[info] tile-only 模式:跳過下載,直接處理既有檔案"
else
rm -f "$JAR" "$OUT"/menu_*.bin
curl -sL --max-time 90 -A "$UA" -c "$JAR" -o "$HTML" "$PAGE"
echo "[info] 頁面已抓: $(wc -c < "$HTML") bytes"

# 抽出 sitesv 圖址:先還原 = 逸出,原樣保留整串(含 =wXXXX 參數)
sed 's/\\u003d/=/g; s/\\\//\//g' "$HTML" \
  | grep -o 'https://lh3\.googleusercontent\.com/sitesv/[A-Za-z0-9_=-]*' \
  | sort -u > "$OUT/.urls.txt"

N=$(wc -l < "$OUT/.urls.txt" | tr -d ' ')
if [ "$N" -eq 0 ]; then
  echo "[error] 頁面裡找不到 sitesv 圖址"
  exit 1
fi
echo "[info] 找到 $N 個圖址(原樣,不改參數)"

i=0
ok=0
while IFS= read -r url; do
  [ -z "$url" ] && continue
  i=$((i+1))
  n=$(printf "menu_%02d" "$i")
  if curl -sL --max-time 120 -A "$UA" -b "$JAR" -e "$PAGE" -o "$OUT/$n" "$url"; then
    t=$(file -b --mime-type "$OUT/$n" 2>/dev/null || echo unknown)
    case "$t" in
      image/png)  mv "$OUT/$n" "$OUT/$n.png";  ok=$((ok+1)) ;;
      image/jpeg) mv "$OUT/$n" "$OUT/$n.jpg";  ok=$((ok+1)) ;;
      image/webp) mv "$OUT/$n" "$OUT/$n.webp"; ok=$((ok+1)) ;;
      *)          mv "$OUT/$n" "$OUT/$n.bin";  echo "[warn] $n 非圖片: $t ($url 前60字: ${url:0:60})" ;;
    esac
  else
    echo "[warn] 第 $i 張下載失敗"
  fi
done < "$OUT/.urls.txt"

rm -f "$JAR"
echo ""
ls -la "$OUT"
echo ""
echo "完成:$ok/$i 張圖片已落地 $OUT"
fi   # end of full-fetch mode

# ============================================================
# v4 後處理階段(同任務範疇:唯讀抓圖+本地影像處理)
# 1) menu_09(PARTY SNACKS 菜單)切 tile 放大,確認有無單價小字
# 2) 另抓「服務內容訂購須知」頁圖片(價目可能在該頁)
# ============================================================

/usr/bin/python3 - "$OUT" <<'PYEOF'
import sys, os, glob
from PIL import Image
base = sys.argv[1]
# 每次抓檔名會洗牌,改用「最大檔=文字最密的菜單卡」規則選圖
cands = sorted(glob.glob(os.path.join(base, "menu_*.png")), key=os.path.getsize)
src = cands[-1]
im = Image.open(src)
w, h = im.size
print(f"[info] 選中 {os.path.basename(src)} ({os.path.getsize(src)} bytes) 尺寸: {w}x{h}")
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

if [ "$MODE" = "tile-only" ]; then
  echo "[info] tile-only 模式:結束(不重抓訂購須知頁)"
  exit 0
fi

OUT2="$OUT/terms"
mkdir -p "$OUT2"
PAGE2="https://sites.google.com/view/maplabkitchen/%E6%9C%8D%E5%8B%99%E5%85%A7%E5%AE%B9%E8%A8%82%E8%B3%BC%E9%A0%88%E7%9F%A5"
JAR2="$OUT2/.cookies.txt"
HTML2="$OUT2/.page.html"
rm -f "$JAR2"
curl -sL --max-time 90 -A "$UA" -c "$JAR2" -o "$HTML2" "$PAGE2"
echo "[info] 訂購須知頁已抓: $(wc -c < "$HTML2") bytes"
sed 's/\\u003d/=/g; s/\\\//\//g' "$HTML2" \
  | grep -o 'https://lh3\.googleusercontent\.com/sitesv/[A-Za-z0-9_=-]*' \
  | sort -u > "$OUT2/.urls.txt"
N2=$(wc -l < "$OUT2/.urls.txt" | tr -d ' ')
echo "[info] 訂購須知頁找到 $N2 個圖址"
j=0; ok2=0
while IFS= read -r url; do
  [ -z "$url" ] && continue
  j=$((j+1))
  n=$(printf "terms_%02d" "$j")
  if curl -sL --max-time 120 -A "$UA" -b "$JAR2" -e "$PAGE2" -o "$OUT2/$n" "$url"; then
    t=$(file -b --mime-type "$OUT2/$n" 2>/dev/null || echo unknown)
    case "$t" in
      image/png)  mv "$OUT2/$n" "$OUT2/$n.png";  ok2=$((ok2+1)) ;;
      image/jpeg) mv "$OUT2/$n" "$OUT2/$n.jpg";  ok2=$((ok2+1)) ;;
      image/webp) mv "$OUT2/$n" "$OUT2/$n.webp"; ok2=$((ok2+1)) ;;
      *)          mv "$OUT2/$n" "$OUT2/$n.bin" ;;
    esac
  fi
done < "$OUT2/.urls.txt"
rm -f "$JAR2"
ls -la "$OUT2"
echo "完成:訂購須知頁 $ok2/$j 張圖片落地 $OUT2"
