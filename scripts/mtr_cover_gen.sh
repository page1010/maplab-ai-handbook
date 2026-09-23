#!/bin/bash
# mtr_cover_gen.sh v2 — MAP TABLE RADIO 每日封面產生器(SOP 段 C1+C2,Owner 5250/5255)
# v2(Owner 5255):封面定義偏 cyberpunk — 暮色改藍紫霓虹天、騎樓柱掛霓虹燈牌(洋紅/青)、
# 桌緣霓虹收邊、標題青/洋紅色差殘影;桌面暖橘與吊燈保留(維持 maplabkitchen 暖色識別)。
# 同檔加跑 C2 微動畫 loop(類 lofi girl 呼吸鏡頭,ffmpeg zoompan 24s 無縫)。
# 產出:covers/cover_YYYYMMDD.png + covers/loop_YYYYMMDD.mp4 + loop_preview_YYYYMMDD.png,
# 皆上 Drive anyone-reader 印連結。
# 安全邊界:不用客戶照片、不打 logo、燈牌只做抽象霓虹管不寫假店名;token 只 source 不回顯。
set -u
HB="/Users/pagemacmini/maplab-ai-handbook"
DAILY="$HB/data/music-style-db/daily"
COVERS="$HB/data/music-style-db/covers"
mkdir -p "$COVERS"
TODAY=$(date +%Y%m%d)
BRIEF="$DAILY/brief_$TODAY.md"
OUT="$COVERS/cover_$TODAY.png"
LOOP="$COVERS/loop_$TODAY.mp4"
PREVIEW="$COVERS/loop_preview_$TODAY.png"
[ -f "$BRIEF" ] || { echo "FATAL: 今日 brief 不存在 $BRIEF(先跑晨會)"; exit 1; }

/usr/bin/python3 - "$BRIEF" "$OUT" <<'PYEOF'
import json, re, sys, math
from PIL import Image, ImageDraw, ImageFont

brief_path, out_path = sys.argv[1], sys.argv[2]
raw = open(brief_path, encoding="utf-8").read()
m = re.search(r"\{.*\}", raw, re.S)
meta = json.loads(m.group(0))
title = meta.get("title_zh", "").strip()
prop = meta.get("cover_prop", "").strip()
bpm = meta.get("bpm", "")

W, H = 2560, 1440
img = Image.new("RGB", (W, H))
d = ImageDraw.Draw(img)
# 天色:深藍青 -> 霓虹紫 -> 暖褐地平線(cyberpunk 夜空,桌區仍回暖色)
c1, c2, c3 = (14, 40, 54), (46, 24, 58), (46, 30, 20)
for y in range(H):
    t = y / H
    if t < 0.55:
        k = t / 0.55
        col = tuple(int(a + (b - a) * k) for a, b in zip(c1, c2))
    else:
        k = (t - 0.55) / 0.45
        col = tuple(int(a + (b - a) * k) for a, b in zip(c2, c3))
    d.line([(0, y), (W, y)], fill=col)

ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
od = ImageDraw.Draw(ov)

def glow(cx, cy, r, color, steps=14, amax=110):
    for i in range(steps, 0, -1):
        rr = r * i / steps
        a = int(amax * (1 - i / (steps + 1)) ** 2)
        od.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=color + (a,))

def neon_rrect(box, color, glow_layers=5):
    for g in range(glow_layers, 0, -1):
        pad = g * 5
        a = int(90 * (1 - g / (glow_layers + 1)))
        od.rounded_rectangle([box[0] - pad, box[1] - pad, box[2] + pad, box[3] + pad],
                             radius=18 + pad, outline=color + (a,), width=6)
    od.rounded_rectangle(box, radius=18, outline=color + (235,), width=6)

# 吊燈三盞(靠右,暖光=品牌識別保留)
for lx in (W * 0.58, W * 0.72, W * 0.86):
    od.line([(lx, 0), (lx, H * 0.24)], fill=(20, 14, 10, 255), width=8)
    glow(lx, H * 0.27, 130, (242, 166, 90), amax=140)
    od.ellipse([lx - 44, H * 0.24, lx + 44, H * 0.24 + 78], fill=(250, 196, 120, 255))
    od.ellipse([lx - 26, H * 0.245, lx + 26, H * 0.245 + 46], fill=(255, 232, 180, 255))

# 長桌(桌面+垂布,暖橘保留)
od.rectangle([W * 0.06, H * 0.70, W * 0.94, H * 0.755], fill=(217, 129, 78, 255))
od.rectangle([W * 0.06, H * 0.755, W * 0.94, H * 0.97], fill=(163, 84, 45, 255))
od.rectangle([W * 0.06, H * 0.755, W * 0.94, H * 0.775], fill=(140, 70, 38, 255))
# 桌緣霓虹收邊(青色 rim = cyberpunk 點綴)
od.line([(W * 0.06, H * 0.700), (W * 0.94, H * 0.700)], fill=(90, 230, 255, 90), width=10)
od.line([(W * 0.06, H * 0.700), (W * 0.94, H * 0.700)], fill=(150, 245, 255, 170), width=4)
# 桌上物:盤、杯、燭光
for px in (0.18, 0.34, 0.62, 0.82):
    od.ellipse([W * px - 90, H * 0.706, W * px + 90, H * 0.748], fill=(245, 232, 216, 255))
    od.ellipse([W * px - 58, H * 0.712, W * px + 58, H * 0.742], fill=(234, 214, 190, 255))
for gx in (0.26, 0.47, 0.72, 0.88):
    od.rectangle([W * gx - 14, H * 0.655, W * gx + 14, H * 0.705], fill=(255, 245, 225, 120))
    od.line([(W * gx - 14, H * 0.655), (W * gx + 14, H * 0.655)], fill=(255, 250, 235, 200), width=4)
for cx in (0.41, 0.55):
    glow(W * cx, H * 0.678, 64, (255, 200, 110), amax=90)
    od.ellipse([W * cx - 8, H * 0.668, W * cx + 8, H * 0.694], fill=(255, 236, 170, 255))
    od.rectangle([W * cx - 12, H * 0.694, W * cx + 12, H * 0.706], fill=(214, 190, 160, 255))

# 當日道具位(桌面右三分之一):發光星芒(brief cover_prop 驅動)
sx, sy = W * 0.62, H * 0.60
od.rectangle([sx - 26, sy + 55, sx + 26, H * 0.71], fill=(210, 225, 220, 90))
od.line([(sx, sy), (sx, sy + 90)], fill=(120, 90, 60, 255), width=7)
glow(sx, sy, 120, (255, 214, 120), amax=200)
for k in range(16):
    ang = k * math.pi / 8
    r1, r2 = 28, 96 if k % 2 == 0 else 62
    od.line([(sx + r1 * math.cos(ang), sy + r1 * math.sin(ang)),
             (sx + r2 * math.cos(ang), sy + r2 * math.sin(ang))],
            fill=(255, 236, 170, 230), width=6)

# 蒸氣兩縷
for bx in (W * 0.34, W * 0.47):
    for s in range(3):
        od.arc([bx - 40, H * 0.50 - s * 55, bx + 40, H * 0.62 - s * 55],
               200, 340 if s % 2 == 0 else 320, fill=(255, 255, 255, 46), width=10)

# 騎樓框(左右柱+頂梁+圓角)
od.rectangle([0, 0, W * 0.045, H], fill=(16, 11, 8, 255))
od.rectangle([W * 0.955, 0, W, H], fill=(16, 11, 8, 255))
od.rectangle([0, 0, W, H * 0.06], fill=(16, 11, 8, 255))
od.pieslice([W * 0.045 - 260, H * 0.06 - 10, W * 0.045 + 260, H * 0.06 + 510], 180, 270, fill=(16, 11, 8, 255))
od.pieslice([W * 0.955 - 260, H * 0.06 - 10, W * 0.955 + 260, H * 0.06 + 510], 270, 360, fill=(16, 11, 8, 255))

# 霓虹燈牌x2:掛在騎樓柱上(不浮空=9/14 v1 教訓),抽象霓虹管不寫假店名
lb = [W * 0.045 + 8, H * 0.42, W * 0.045 + 92, H * 0.66]
od.rounded_rectangle(lb, radius=18, fill=(12, 9, 16, 255))
neon_rrect(lb, (255, 70, 170))
for i in range(3):
    yy = H * (0.46 + i * 0.055)
    od.line([(lb[0] + 20, yy), (lb[2] - 20, yy)], fill=(255, 120, 200, 210), width=5)
rb = [W * 0.955 - 92, H * 0.34, W * 0.955 - 8, H * 0.56]
od.rounded_rectangle(rb, radius=18, fill=(9, 12, 16, 255))
neon_rrect(rb, (70, 220, 255))
for i in range(3):
    yy = H * (0.38 + i * 0.05)
    od.line([(rb[0] + 20, yy), (rb[2] - 20, yy)], fill=(140, 240, 255, 210), width=5)

img = Image.alpha_composite(img.convert("RGBA"), ov)

# 文字層:字型逐字驗證(Songti 部分 face 缺鹽/頭/慶等繁字,9/14 教訓)
td = ImageDraw.Draw(img)
CAND = [("/System/Library/Fonts/Supplemental/Songti.ttc", i) for i in range(6)] + \
       [("/System/Library/Fonts/PingFang.ttc", i) for i in range(4)]
def pick(chars, size):
    for path, idx in CAND:
        try:
            f = ImageFont.truetype(path, size, index=idx)
        except Exception:
            continue
        if all(f.getmask(c).getbbox() is not None for c in chars if c.strip()):
            return f
    return ImageFont.load_default()
serif = pick(title or "曲", 118)
serif_s = pick("0123456789 BPM/instrumental by maplabkitchen", 54)
try:
    eng = ImageFont.truetype("/System/Library/Fonts/Supplemental/Georgia.ttf", 58)
except Exception:
    eng = serif_s
tag = "M A P   T A B L E   R A D I O"
td.text((W * 0.075 + 3, H * 0.115 + 3), tag, font=eng, fill=(0, 0, 0, 120))
td.text((W * 0.075, H * 0.115), tag, font=eng, fill=(242, 205, 148, 255))
td.line([(W * 0.075, H * 0.175), (W * 0.075 + 620, H * 0.175)], fill=(120, 235, 255, 220), width=4)
# 標題:青/洋紅色差殘影(cyberpunk chromatic)+ 主字奶油白
td.text((W * 0.075 - 5, H * 0.215), title, font=serif, fill=(90, 230, 255, 150))
td.text((W * 0.075 + 5, H * 0.215 + 3), title, font=serif, fill=(255, 70, 170, 140))
td.text((W * 0.075, H * 0.215), title, font=serif, fill=(255, 244, 228, 255))
sub = f"{bpm} BPM / instrumental" if bpm else "instrumental"
td.text((W * 0.075, H * 0.335), sub, font=serif_s, fill=(226, 188, 138, 255))
td.text((W * 0.660, H * 0.905), "by maplabkitchen", font=serif_s, fill=(222, 186, 140, 210))

img.convert("RGB").save(out_path, "PNG")
print(f"[ok] cover -> {out_path}  title={title}  prop={prop}")
PYEOF
rc=$?
[ $rc -eq 0 ] || { echo "FATAL: 繪圖失敗 rc=$rc"; exit $rc; }

# C2 微動畫 loop(類 lofi girl):呼吸變焦 24s 無縫,25fps 600 幀,sin 全週期=首尾同幀
FFMPEG="/opt/homebrew/bin/ffmpeg"
if [ -x "$FFMPEG" ]; then
  "$FFMPEG" -y -loglevel error -loop 1 -i "$OUT" \
    -vf "zoompan=z='1.02+0.012*sin(2*PI*on/600)':d=600:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1920x1080:fps=25" \
    -frames:v 600 -c:v libx264 -preset medium -crf 20 -pix_fmt yuv420p "$LOOP" \
    && echo "[ok] loop -> $LOOP (24s seamless)" \
    || echo "[warn] loop 產出失敗,靜圖照常交付"
  [ -f "$LOOP" ] && "$FFMPEG" -y -loglevel error -ss 6 -i "$LOOP" -frames:v 1 "$PREVIEW" \
    && echo "[ok] preview -> $PREVIEW"
else
  echo "[warn] ffmpeg 不在 /opt/homebrew/bin,跳過 loop"
fi

# 上 Drive anyone-reader(venv python;token 不回顯)
"$HB/bot/venv/bin/python" - "$OUT" "$LOOP" <<'PYEOF' 2>&1 | grep -v FutureWarning
import json, os, socket, sys, time
socket.setdefaulttimeout(300)
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

info = json.load(open("/Users/pagemacmini/.claude/mcp-keys/google-token.json"))
info.pop("expiry", None)
creds = Credentials.from_authorized_user_info(info)
drive = build("drive", "v3", credentials=creds)

def retry(fn, n=3):
    for i in range(n):
        try:
            return fn()
        except Exception:
            if i == n - 1:
                raise
            time.sleep(5)

for path in sys.argv[1:]:
    if not os.path.exists(path):
        continue
    name = path.split("/")[-1]
    mime = "video/mp4" if path.endswith(".mp4") else "image/png"
    media = MediaFileUpload(path, mimetype=mime, resumable=True)
    f = retry(lambda: drive.files().create(body={"name": f"MTR-{name}"}, media_body=media, fields="id").execute())
    fid = f["id"]
    retry(lambda: drive.permissions().create(fileId=fid, body={"type": "anyone", "role": "reader"}).execute())
    print(f"[drive] {name} https://drive.google.com/file/d/{fid}/view")
PYEOF
echo "[done] mtr_cover_gen $TODAY"
