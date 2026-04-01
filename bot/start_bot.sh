#!/usr/bin/env bash
# start_bot.sh — 前台啟動 MAPLAB Telegram bot（dev / debug 用）
# 直接看 log output，Ctrl+C 停止

set -e

BOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$BOT_DIR"

# Check .env
if [ ! -f ".env" ]; then
    echo "❌ .env 不存在！"
    echo "   請執行: cp bot/.env.example bot/.env 並填入 TELEGRAM_BOT_TOKEN"
    exit 1
fi

# Check / create virtualenv
if [ ! -d "venv" ]; then
    echo "📦 建立 Python virtualenv…"
    python3 -m venv venv
fi

# Activate and install deps
source venv/bin/activate
echo "📦 安裝/更新依賴…"
pip install -q -r requirements.txt

# Kill any existing bot.py process before starting
pkill -f bot.py 2>/dev/null && echo "🛑 舊 bot process 已終止" || true
sleep 1

echo ""
echo "🤖 MAPLAB Claude Bot 啟動中（前台模式）…"
echo "   按 Ctrl+C 停止"
echo "   Log: $BOT_DIR/bot.log"
echo ""

python3 bot.py
