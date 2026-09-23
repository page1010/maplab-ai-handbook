#!/usr/bin/env bash
# a6_hermes_activate.sh — 把 A6 bot 的 Telegram 側切到 hermes 閘道(Owner 2026-08-25 指示)
# 原理:舊 bot_a6.py 殭屍進程退場後,launchd com.maplab.a6bot KeepAlive 會用改過的
# run_daemon.sh 重生 = 直接跑 bot_a6/hermes_telegram_gateway.py。
# 可重複執行:已切換時只回報狀態,不重殺。不讀不印任何 token。
set -euo pipefail
BOT_DIR="/Users/pagemacmini/maplab-ai-handbook/bot_a6"
PY="/Users/pagemacmini/maplab-ai-handbook/bot/venv/bin/python3"
LOG="$BOT_DIR/hermes_gateway.log"

# 0) 先驗閘道語法,壞的話不殺舊進程(至少 launchd 不會空轉)
if ! "$PY" -m py_compile "$BOT_DIR/hermes_telegram_gateway.py"; then
  echo "[abort] hermes_telegram_gateway.py 語法錯誤,未動任何進程"
  exit 1
fi
echo "[ok] 閘道語法檢查通過"

if pgrep -f "bot_a6/hermes_telegram_gateway.py" >/dev/null 2>&1; then
  echo "[ok] hermes 閘道已在線,不需切換"
else
  if pgrep -f "bot_a6/bot_a6.py" >/dev/null 2>&1; then
    pkill -f "bot_a6/bot_a6.py"
    echo "[done] 舊 bot_a6.py 已請退,等 launchd 重生(ThrottleInterval 30s)"
  else
    echo "[info] 舊 bot_a6.py 不在線,嘗試載入 launchd job"
    launchctl load "$HOME/Library/LaunchAgents/com.maplab.a6bot.plist" 2>/dev/null || true
  fi
  for _ in 1 2 3 4 5 6 7 8 9 10 11 12; do
    sleep 5
    pgrep -f "bot_a6/hermes_telegram_gateway.py" >/dev/null 2>&1 && break
  done
fi

if pgrep -f "bot_a6/hermes_telegram_gateway.py" >/dev/null 2>&1; then
  echo "[ok] hermes 閘道進程在線"
else
  echo "[fail] 閘道 60 秒內沒起來,查 $BOT_DIR/launchd_stderr.log 與 $LOG"
  exit 1
fi

# 日誌可能含 Owner 對話摘要；啟動器只回報檔案是否存在，不把內容印到終端。
if [[ -f "$LOG" ]]; then
  echo "[info] 閘道日誌已建立（內容不在終端顯示）"
else
  echo "[info] 閘道日誌尚未建立"
fi
