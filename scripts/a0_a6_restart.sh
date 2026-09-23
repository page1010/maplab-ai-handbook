#!/usr/bin/env bash
# a0_a6_restart.sh — 重啟 a6 Telegram 閘道並留下可稽核的前後狀態
#
# 2026-09-22 Owner msg 5773:「你不要再自我設限,把那些奇怪的規範拿掉…發現問題+
# 改進就是你的任務與最大價值」。原自助規則「不碰 a6 bot 進程」是 A0 自訂的保守
# 條款,已由 Owner 解除。本腳本只動自家模組 com.maplab.a6bot,不碰系統服務。
#
# 產出:~/.maplab/a6_restart.log(逐次覆寫)
set -uo pipefail

LABEL="com.maplab.a6bot"
UID_NUM="$(id -u)"
GLOG="/Users/pagemacmini/maplab-ai-handbook/bot_a6/hermes_gateway.log"
LOG="$HOME/.maplab/a6_restart.log"
mkdir -p "$HOME/.maplab"

{
    echo "=== a6 restart $(date '+%Y-%m-%d %H:%M:%S') ==="

    echo "--- before ---"
    launchctl list | grep "$LABEL" || echo "label not loaded"

    echo "--- kickstart -k ---"
    launchctl kickstart -k "gui/${UID_NUM}/${LABEL}" && echo "kickstart OK" || echo "kickstart FAILED rc=$?"

    sleep 6

    echo "--- after ---"
    launchctl list | grep "$LABEL" || echo "label not loaded"

    echo "--- gateway log tail ---"
    tail -n 25 "$GLOG" 2>/dev/null || echo "gateway log unreadable"

    echo "=== end ==="
} >"$LOG" 2>&1

chmod 600 "$LOG"
