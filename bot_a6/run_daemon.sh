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

# 使用 A1 bot 的 venv（同一個環境，不重複安裝）
exec "/Users/pagemacmini/maplab-ai-handbook/bot/venv/bin/python3" "$BOT_DIR/bot_a6.py"
