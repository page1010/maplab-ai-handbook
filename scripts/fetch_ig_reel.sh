#!/bin/bash
# fetch_ig_reel.sh <url> — download a PUBLIC Instagram reel + caption locally
# and extract frames so the agent can view the content. No login, no cookies,
# no third-party FB/IG code: yt-dlp + ffmpeg only, public content only.
# yt-dlp runs via system python first: the homebrew binary hit a broken expat
# module on 2026-09-20; system /usr/bin/python3 carries the working site-packages.
set -u
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin"
URL="${1:?usage: fetch_ig_reel.sh <url>}"
ID=$(printf '%s' "$URL" | sed -E 's#.*/(reel|reels|p)/([^/?]+).*#\2#')
OUT="$HOME/.maplab/ig/$ID"
mkdir -p "$OUT"
{
  echo "[$(date '+%Y-%m-%dT%H:%M:%S')] fetch start $URL"
  ok=0
  if /usr/bin/python3 -m yt_dlp --version >/dev/null 2>&1; then
    /usr/bin/python3 -m yt_dlp --no-playlist --write-info-json -o "$OUT/video.%(ext)s" "$URL" && ok=1
  fi
  if [ "$ok" = 0 ] && command -v yt-dlp >/dev/null 2>&1; then
    yt-dlp --no-playlist --write-info-json -o "$OUT/video.%(ext)s" "$URL" && ok=1
  fi
  if [ "$ok" = 0 ]; then
    echo "trying user-level yt-dlp install"
    /usr/bin/python3 -m pip install --user --quiet yt-dlp && \
      /usr/bin/python3 -m yt_dlp --no-playlist --write-info-json -o "$OUT/video.%(ext)s" "$URL" && ok=1
  fi
  V=$(ls "$OUT"/video.* 2>/dev/null | grep -v '\.json$' | head -1)
  if [ -n "$V" ]; then
    ffmpeg -y -i "$V" -vf "fps=1/3,scale=720:-1" "$OUT/frame_%02d.png"
    echo "[$(date '+%Y-%m-%dT%H:%M:%S')] DONE frames=$(ls "$OUT"/frame_*.png 2>/dev/null | wc -l)"
  else
    echo "[$(date '+%Y-%m-%dT%H:%M:%S')] FAILED no video file"
  fi
} >> "$OUT/fetch.log" 2>&1
