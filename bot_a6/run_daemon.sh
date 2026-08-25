#!/usr/bin/env bash
# run_daemon.sh — A6 bot launchd wrapper
# launchd 不讀 .env，這個 wrapper 負責 export 環境變數再啟動

BOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$BOT_DIR"

# Load .env
if [ -f "$BOT_DIR/.env" ]; then
    set -a
    source "$BOT_DIR/.env"
    set +a
else
    echo "ERROR: $BOT_DIR/.env not found" >&2
    exit 1
fi

# 2026-08-25 Owner 指示「把 A6 bot 接給 hermes」:Telegram 側改跑 hermes 閘道,
# 舊報價助理 bot_a6.py 退出 Telegram 輪詢(程式保留在原地,LINE/GAS 流程不受影響)。
# 閘道只用標準庫,任何 python3 都能跑;沿用同一 venv 免 PATH 意外。
exec "/Users/pagemacmini/maplab-ai-handbook/bot/venv/bin/python3" "$BOT_DIR/hermes_telegram_gateway.py"
