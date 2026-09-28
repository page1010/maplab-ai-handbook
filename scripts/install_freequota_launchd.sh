#!/bin/bash
# install_freequota_launchd.sh — 安裝/重載 com.maplab.freequota 使用者層排程(#89)
# 冪等:重跑會先卸載再載入。只動自家 label,不碰其他 LaunchAgents。
set -eu
SRC="/Users/pagemacmini/maplab-ai-handbook/scripts/com.maplab.freequota.plist"
DST="$HOME/Library/LaunchAgents/com.maplab.freequota.plist"
UID_NUM="$(id -u)"
mkdir -p "$HOME/Library/LaunchAgents"
cp "$SRC" "$DST"
launchctl bootout "gui/$UID_NUM/com.maplab.freequota" 2>/dev/null || true
launchctl bootstrap "gui/$UID_NUM" "$DST"
echo "--- 驗證 ---"
launchctl print "gui/$UID_NUM/com.maplab.freequota" | grep -E "state|program|com.maplab" | head -6
echo "OK: com.maplab.freequota 已載入(02/06/10/14/18/22 各時 05 分喚醒)"
