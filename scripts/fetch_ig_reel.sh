#!/bin/bash
# fetch_ig_reel.sh <url> — download a PUBLIC Instagram reel + caption locally
# and extract frames so the agent can view the content. No login, no cookies,
# no third-party FB/IG code: yt-dlp + ffmpeg only, public content only.
set -u
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"
URL="${1:?usage: fetch_ig_reel.sh <url>}"
ID=$(printf '%s' "$URL" | sed -E 's#.*/(reel|reels|p)/([^/?]+).*#\2#')
OUT="$HOME/.maplab/ig/$ID"
mkdir -p "$OUT"
{
  echo "[$(date '+%Y-%m-%dT%H:%M:%S')] fetch start $URL"
  yt-dlp --no-playlist --write-info-json -o "$OUT/video.%(ext)s" "$URL"
  V=$(ls "$OUT"/video.* 2>/dev/null | grep -v '\.json$' | head -1)
  if [ -n "$V" ]; then
    ffmpeg -y -i "$V" -vf "fps=1/3,scale=720:-1" "$OUT/frame_%02d.png"
    echo "[$(date '+%Y-%m-%dT%H:%M:%S')] DONE frames=$(ls "$OUT"/frame_*.png 2>/dev/null | wc -l)"
  else
    echo "[$(date '+%Y-%m-%dT%H:%M:%S')] FAILED no video file"
  fi
} >> "$OUT/fetch.log" 2>&1
