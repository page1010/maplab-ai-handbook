#!/bin/bash
# render_slideshow_draft.sh v1 — 8 格幻燈影片草稿渲染(6154 Gogo 影片線)
# 用法: ./render_slideshow_draft.sh <concat_list.txt> <audio_file> <output.mp4> [秒數]
# 只讀寫 maplab-ai-handbook 內路徑;素材=已上線網站自家圖+music-style-db 自有音軌。
set -u

LIST="$1"
AUDIO="$2"
OUT="$3"
DUR="${4:-40}"

FFMPEG="/opt/homebrew/bin/ffmpeg"
if [ ! -x "$FFMPEG" ]; then echo "FATAL: ffmpeg 不存在"; exit 1; fi
if [ ! -f "$LIST" ]; then echo "FATAL: 清單不存在: $LIST"; exit 1; fi
if [ ! -f "$AUDIO" ]; then echo "FATAL: 音檔不存在: $AUDIO"; exit 1; fi

FADE_OUT_START=$((DUR - 3))

"$FFMPEG" -y -f concat -safe 0 -i "$LIST" -i "$AUDIO" \
  -vf "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=0x111111,fps=30,format=yuv420p" \
  -af "atrim=0:${DUR},afade=t=in:st=0:d=1,afade=t=out:st=${FADE_OUT_START}:d=3" \
  -t "$DUR" -c:v libx264 -preset medium -crf 20 -c:a aac -b:a 192k -shortest "$OUT" 2>&1 | tail -3

if [ -f "$OUT" ]; then
  echo "OK: $OUT"
  ls -la "$OUT"
else
  echo "FATAL: 輸出未產生"
  exit 1
fi
