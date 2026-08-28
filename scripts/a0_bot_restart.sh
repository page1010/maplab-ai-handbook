#!/usr/bin/env bash
# a0_bot_restart.sh — A0 自助重啟 Telegram bot(不需 Owner 動終端機)
# 背景:Owner 2026-08-28 msg 4296/4314 明令:授權即授權,不得再要求 Owner 開終端機。
# 機制:精準結束 launchd 追蹤的 bot.py 進程;com.maplab.telegrambot 的
# KeepAlive=true 會在 ThrottleInterval(30s)內自動重生,載入最新 bot.py
# (含 resume 白名單修正 beaec1d)。
# 安全:pkill pattern 鎖全路徑 maplab-ai-handbook/bot/bot.py,不會誤殺
# a6 bot、claude 進程或其他程式;每次重啟留 log 供稽核。
set -u
LOG=/Users/pagemacmini/claude-daily-operations/state/a0_bot_restart.log
STAMP="$(date '+%Y-%m-%dT%H:%M:%S')"
echo "[$STAMP] restart requested (caller pid $$)" >> "$LOG"
# 延遲 2 秒再殺,讓呼叫方(回覆腳本)先乾淨收尾、回報送達
nohup /bin/bash -c "sleep 2; /usr/bin/pkill -f 'maplab-ai-handbook/bot/bot.py'; echo \"[\$(date '+%Y-%m-%dT%H:%M:%S')] pkill issued; launchd KeepAlive respawning\" >> '$LOG'" >/dev/null 2>&1 &
echo "[$STAMP] detached killer scheduled (fires in 2s)" >> "$LOG"
