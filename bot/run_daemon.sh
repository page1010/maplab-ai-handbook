#!/usr/bin/env bash
# run_daemon.sh — launchd / background daemon wrapper
# launchd 不讀 .env，這個 wrapper 負責 export 環境變數再啟動 bot

BOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$BOT_DIR"

export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH"

# Load .env
if [ -f "$BOT_DIR/.env" ]; then
    set -a
    source "$BOT_DIR/.env"
    set +a
else
    echo "ERROR: $BOT_DIR/.env not found" >&2
    exit 1
fi

exec "$BOT_DIR/venv/bin/python3" "$BOT_DIR/bot.py"
