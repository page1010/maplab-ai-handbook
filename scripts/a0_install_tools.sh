#!/usr/bin/env bash
# Owner-ordered installs (msg 4756 consent + msg 4781 「第三點馬上安裝」).
# q1 = video-teardown toolchain (yt-dlp, ffmpeg, whisper-cpp via Homebrew)
# q3 = Futu OpenD GUI (download→mount→/Applications) + futu-api SDK, per
#      ~/.claude/skills/install-futu-opend (GUI 版 only; SIMULATE only; login
#      is Owner's manual GUI step — this script never touches credentials).
set -uo pipefail
LOG_DIR="/Users/pagemacmini/maplab-ai-handbook/data/install_logs"
mkdir -p "$LOG_DIR"
STAMP="$(date '+%Y%m%d-%H%M%S')"
BREW=/opt/homebrew/bin/brew

q1() {
  local log="$LOG_DIR/q1-teardown-$STAMP.log"
  {
    echo "== Q1 teardown toolchain =="
    date
    "$BREW" install yt-dlp ffmpeg whisper-cpp 2>&1
    echo "-- versions --"
    "$BREW" list --versions yt-dlp ffmpeg whisper-cpp 2>&1
    echo "exit=$?"
  } >> "$log" 2>&1
  echo "Q1 log: $log"
  tail -5 "$log"
}

q3() {
  local log="$LOG_DIR/q3-opend-$STAMP.log"
  local work="$HOME/Desktop/futu_opend_install"
  {
    echo "== Q3 Futu OpenD (GUI) =="
    date
    mkdir -p "$work"
    echo "-- download (official fetch-lasted-link) --"
    curl -L --max-time 600 -o "$work/opend-macos.tar.gz" \
      "https://www.futunn.com/download/fetch-lasted-link?name=opend-macos"
    echo "curl exit=$?"
    ls -lh "$work"
    echo "-- extract --"
    tar -xzf "$work/opend-macos.tar.gz" -C "$work"
    find "$work" -name "*.dmg" -maxdepth 3
    local dmg
    dmg="$(find "$work" -name "*.dmg" -maxdepth 3 | head -1)"
    if [ -z "$dmg" ]; then echo "FAIL: no dmg found"; exit 1; fi
    echo "-- mount + copy GUI app (Futu_OpenD, 帶下劃線) --"
    local mnt="/Volumes/a0_futu_opend"
    hdiutil attach "$dmg" -nobrowse -mountpoint "$mnt"
    ls "$mnt"
    local app
    app="$(ls -d "$mnt"/Futu_OpenD*.app 2>/dev/null | head -1)"
    if [ -z "$app" ]; then echo "FAIL: no Futu_OpenD*.app in dmg"; hdiutil detach "$mnt"; exit 1; fi
    rm -rf "/Applications/$(basename "$app")"
    cp -R "$app" /Applications/
    hdiutil detach "$mnt"
    ls -d /Applications/Futu_OpenD*.app
    echo "-- SDK: pip3 install --user futu-api --"
    /usr/bin/pip3 install --user futu-api 2>&1 | tail -5
    /usr/bin/pip3 show futu-api 2>&1 | grep -E "^(Name|Version):"
    echo "0.1.1" > "$HOME/.futu_skill_version"
    echo "DONE: app in /Applications; NEXT = Owner opens app + GUI login (帳密只在 GUI 輸入, 全程 SIMULATE)"
  } >> "$log" 2>&1
  echo "Q3 log: $log"
  tail -8 "$log"
}

case "${1:-}" in
  q1) q1 ;;
  q3) q3 ;;
  *) echo "usage: a0_install_tools.sh <q1|q3>"; exit 2 ;;
esac
