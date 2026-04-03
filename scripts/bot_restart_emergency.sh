#!/bin/bash
# bot_restart_emergency.sh — 緊急重啟兩個 Bot（A1 + A6）
# 用途：Claude Code session 掛掉、Bot 無回應時，執行這個腳本恢復

set -e

echo "=== MAPLAB Bot 緊急重啟 ==="
echo "$(date '+%Y-%m-%d %H:%M:%S')"
echo ""

A1_JOB="com.maplab.telegrambot"
A6_JOB="com.maplab.a6bot"

restart_bot() {
  local job=$1
  local name=$2
  echo "[$name] 重啟中..."
  launchctl bootout gui/$(id -u) "$HOME/Library/LaunchAgents/${job}.plist" 2>/dev/null || true
  sleep 1
  launchctl bootstrap gui/$(id -u) "$HOME/Library/LaunchAgents/${job}.plist"
  sleep 2
  if launchctl list | grep -q "$job"; then
    echo "[$name] ✅ 已啟動"
  else
    echo "[$name] ❌ 啟動失敗，請檢查 plist"
  fi
}

restart_bot "$A1_JOB" "A1 Bot"
restart_bot "$A6_JOB" "A6 Bot"

echo ""
echo "=== 狀態確認 ==="
launchctl list | grep maplab

echo ""
echo "完成。如果 Bot 還是沒回應，執行以下查 log："
echo "  tail -20 ~/maplab-ai-handbook/bot/launchd_stdout.log"
echo "  tail -20 ~/maplab-ai-handbook/bot_a6/launchd_stdout.log"
