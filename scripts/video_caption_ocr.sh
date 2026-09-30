#!/bin/bash
# video_caption_ocr.sh — 讀出影片素材上疊的字卡(純本機、零上雲、零安裝)
#
# 由來:2026-09-30 抓周影片重製版交回來,逐格比對只能證明「字卡帶重畫了」,
#       證不了「寫的是過閘的那 12 句」。當時本機找不到離線文字辨識:
#       tesseract 沒裝、pip 裝 Vision 套件被權限擋、系統捷徑要授權。
#       只好把驗收外包給交件方自己貼純文字——等於產出者跑自己的閘門,
#       違反企業文化原則 2「閘門必須獨立執行」。
#
# 解法:macOS 從 10.15 起內建 Vision 文字辨識框架,osascript 的 JavaScript
#       模式可以直接呼叫,不必安裝任何套件、不必額外授權、影像不離開本機。
#       實測讀得出繁體中文字卡。這支腳本把那條路固定下來。
#
# 用法:bash scripts/video_caption_ocr.sh <影片檔> [每秒抽幾張] [字卡帶上緣] [字卡帶下緣]
#       例:bash scripts/video_caption_ocr.sh video.mp4 1 0.50 0.90
#       上下緣是畫面高度的比例,預設 0.50~0.90(疊字通常在下半部)。
#       先用逐格比對找出差異集中的橫帶,再把比例填進來,準確度最高。
#
# 輸出:每張畫格一行,格式「時間點秒數 : 讀到的文字」。
#       要接文案閘門就把去重後的句子存成一行一句,餵給
#       bash scripts/ad_copy_voice_check.sh <檔> ad
#
# 隱私:抽出來的畫格落在 ~/.maplab/ 之下,含人臉,不得上傳、不得進版控、
#       不得用 Read 打開送上雲。本腳本全程只在本機處理。
set -u

SRC="${1:-}"
FPS="${2:-1}"
TOP="${3:-0.50}"
BOT="${4:-0.90}"

if [ -z "$SRC" ] || [ ! -f "$SRC" ]; then
  echo "用法:bash scripts/video_caption_ocr.sh <影片檔> [每秒抽幾張] [上緣比例] [下緣比例]"
  exit 2
fi

FFMPEG=/opt/homebrew/bin/ffmpeg
PY="$HOME/.maplab/cvenv312/bin/python"
[ -x "$FFMPEG" ] || { echo "FATAL: 找不到 ffmpeg"; exit 1; }
[ -x "$PY" ] || { echo "FATAL: 找不到影像處理用的 python 環境"; exit 1; }

WORK="$HOME/.maplab/caption_ocr_$$"
rm -rf "$WORK"
mkdir -p "$WORK"

"$FFMPEG" -v error -i "$SRC" -vf "fps=$FPS" "$WORK/f%04d.png" || { echo "FATAL: 抽格失敗"; exit 1; }

CAPTION_TOP="$TOP" CAPTION_BOT="$BOT" WORKDIR="$WORK" "$PY" - <<'PY'
# -*- coding: utf-8 -*-
import os, cv2
d = os.environ['WORKDIR']
top = float(os.environ['CAPTION_TOP'])
bot = float(os.environ['CAPTION_BOT'])
n = 0
for fn in sorted(os.listdir(d)):
    if not (fn.startswith('f') and fn.endswith('.png')):
        continue
    img = cv2.imread(os.path.join(d, fn))
    h, w = img.shape[:2]
    band = img[int(h * top):int(h * bot), 0:w]
    # 放大兩倍,小字的辨識率差很多
    band = cv2.resize(band, (band.shape[1] * 2, band.shape[0] * 2),
                      interpolation=cv2.INTER_CUBIC)
    cv2.imwrite(os.path.join(d, 'band_' + fn), band)
    n += 1
print('已裁出字卡帶 %d 張' % n)
PY

cat > "$WORK/ocr.js" <<'JS'
ObjC.import('Vision');
ObjC.import('Foundation');
ObjC.import('AppKit');
function run(argv) {
  var url = $.NSURL.fileURLWithPath($(argv[0]));
  var img = $.NSImage.alloc.initWithContentsOfURL(url);
  var rep = $.NSBitmapImageRep.imageRepWithData(img.TIFFRepresentation);
  var handler = $.VNImageRequestHandler.alloc.initWithCGImageOptions(rep.CGImage, $());
  var out = [];
  var req = $.VNRecognizeTextRequest.alloc.initWithCompletionHandler(function(r, e) {
    var results = r.results;
    for (var i = 0; i < results.count; i++) {
      var c = results.objectAtIndex(i).topCandidates(1);
      if (c.count > 0) { out.push(ObjC.unwrap(c.objectAtIndex(0).string)); }
    }
  });
  req.recognitionLevel = 0;          // 0 = accurate
  req.recognitionLanguages = $(['zh-Hant', 'en-US']);
  req.usesLanguageCorrection = false; // 不要讓它自動改字,要的是畫面上原本寫什麼
  handler.performRequestsError($([req]), $());
  return out.join(' / ');
}
JS

echo "--- 字卡逐格 ---"
i=0
for f in "$WORK"/band_f*.png; do
  i=$((i + 1))
  T=$(/usr/bin/python3 -c "print(round(($i - 1) / float('$FPS'), 2))")
  printf '%ss : ' "$T"
  /usr/bin/osascript -l JavaScript "$WORK/ocr.js" "$f" 2>&1 | head -1
done

echo "--- 畫格暫存在 $WORK(含人臉,不得上傳/入版控;看完自行刪除)---"
