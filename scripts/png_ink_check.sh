#!/usr/bin/env bash
# png_ink_check.sh — 驗一張 PNG 到底「有沒有墨」(唯讀,不改檔)
#
# 為什麼有這支:
#   2026-09-23,浮水印 tainan_chillout_watermark_150.png 只有 167 bytes。
#   用看圖工具打開是一片白 —— 但那證明不了它是空的,因為它是
#   「白色圖案畫在透明底上」,白底檢視器本來就會看起來全白。
#   當時我只能說「沒驗過」,不能說「它是空的」。這支就是來把這句話補完的。
#
#   同一天 13:05 的 YouTube Studio 截圖裡,「自訂影片浮水印」的預覽框
#   是整片空白,而 antigravity 仍然按了「完成」。
#   = 沒有人在按下發布前,真的確認過那張圖裡有東西。
#
# 用法: bash scripts/png_ink_check.sh <a.png> [b.png ...]
#
# 判讀:
#   opaque_px = alpha > 16 的像素數。0 -> 這張圖是空的,發出去等於沒有浮水印。
#   若有 alpha,額外印出不透明區的平均亮度,確認是「白墨」還是「黑墨」。
set -uo pipefail

if [ "$#" -eq 0 ]; then
  echo "用法: bash scripts/png_ink_check.sh <a.png> [b.png ...]" >&2
  exit 64
fi

/usr/bin/python3 - "$@" <<'PY'
import sys
try:
    from PIL import Image
except ImportError:
    print("✗ 這個 python3 沒有 PIL。請用系統 /usr/bin/python3(agent-hq-and-photo-pipeline 教訓)。")
    sys.exit(4)

bad = False
for path in sys.argv[1:]:
    try:
        im = Image.open(path)
    except Exception as e:
        print(f"✗ {path}: 開不起來 {e}")
        bad = True
        continue

    name = path.rsplit("/", 1)[-1]
    print(f"=== {name}  {im.size[0]}x{im.size[1]}  mode={im.mode} ===")

    if im.mode not in ("RGBA", "LA"):
        rgb = im.convert("RGB")
        ext = rgb.getextrema()
        flat = all(lo == hi for lo, hi in ext)
        print(f"  無 alpha 通道。各通道範圍={ext}")
        print("  ✗ 整張單一顏色 = 空圖。" if flat else "  OK 有顏色變化,不是空圖。")
        if flat:
            bad = True
        print()
        continue

    rgba = im.convert("RGBA")
    a = rgba.getchannel("A")
    hist = a.histogram()
    opaque = sum(hist[17:])
    total = im.size[0] * im.size[1]
    pct = 100.0 * opaque / total
    print(f"  alpha>16 的像素:{opaque} / {total}  ({pct:.2f}%)")

    if opaque == 0:
        print("  ✗ 完全透明 = 這張圖是空的。貼到影片上等於沒有浮水印。")
        bad = True
        print()
        continue

    px = rgba.load()
    tot, n = 0, 0
    for y in range(im.size[1]):
        for x in range(im.size[0]):
            r, g, b, al = px[x, y]
            if al > 16:
                tot += (r + g + b) / 3.0
                n += 1
    mean = tot / n
    ink = "白墨(淺色,適合壓在深色畫面上)" if mean > 160 else \
          "黑墨(深色,壓在深色畫面上會看不見)" if mean < 96 else "中間調"
    print(f"  OK 有墨。不透明區平均亮度={mean:.1f} -> {ink}")
    if pct < 0.5:
        print(f"  WARN 只有 {pct:.2f}% 的像素有墨,小尺寸下可能等同看不見。")
    print()

sys.exit(3 if bad else 0)
PY
