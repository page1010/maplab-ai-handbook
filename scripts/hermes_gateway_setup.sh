#!/bin/bash
# hermes_gateway_setup.sh — 讓 hermes 成為常駐 Telegram 窗口(Owner 備援對話窗)
# 用法: bash hermes_gateway_setup.sh [TELEGRAM_BOT_TOKEN]
#   - 金鑰不經過對話、不進 git:OPENROUTER_API_KEY 直接從 ~/.maplab/free_compute.env 複製,
#     bot token 由參數傳入(或先跑一次無參數,之後手動補進 ~/.hermes/.env)。
# 設計:hermes gateway 常駐=Owner 隨時多一個對話窗;Fable5 額度滿時這個窗自然就是備援,
#   不需要任何「切換」動作(程式觸發=長駐,比條件觸發簡單可靠)。
set -euo pipefail

HERMES_HOME="$HOME/.hermes"
HERMES_REPO="$HERMES_HOME/hermes-agent"
ENV_FILE="$HERMES_HOME/.env"
FREE_ENV="$HOME/.maplab/free_compute.env"
OWNER_ID="1077768811"

touch "$ENV_FILE"; chmod 600 "$ENV_FILE"

# 1) OpenRouter 金鑰:從 free_compute.env 複製(不回顯)
if ! grep -q "^OPENROUTER_API_KEY=" "$ENV_FILE" 2>/dev/null; then
  if grep -q "^OPENROUTER_API_KEY=" "$FREE_ENV" 2>/dev/null; then
    grep "^OPENROUTER_API_KEY=" "$FREE_ENV" >> "$ENV_FILE"
    echo "[setup] OPENROUTER_API_KEY 已從 free_compute.env 複製進 hermes .env"
  else
    echo "[setup] 警告:$FREE_ENV 沒有 OPENROUTER_API_KEY,hermes 模型呼叫會失敗"
  fi
else
  echo "[setup] OPENROUTER_API_KEY 已存在,略過"
fi

# 2) Telegram bot token(參數傳入)+ 只允許 Owner 對話
if [ $# -ge 1 ] && [ -n "$1" ]; then
  if grep -q "^TELEGRAM_BOT_TOKEN=" "$ENV_FILE"; then
    echo "[setup] TELEGRAM_BOT_TOKEN 已存在,不覆寫(要換 token 請手動編輯 $ENV_FILE)"
  else
    echo "TELEGRAM_BOT_TOKEN=$1" >> "$ENV_FILE"
    echo "[setup] TELEGRAM_BOT_TOKEN 已寫入"
  fi
fi
if ! grep -q "^TELEGRAM_ALLOWED_USERS=" "$ENV_FILE"; then
  echo "TELEGRAM_ALLOWED_USERS=$OWNER_ID" >> "$ENV_FILE"
  echo "[setup] 已限定只有 Owner($OWNER_ID)可對話"
fi

# 3) 檢查 config(模型應為 OpenRouter 雲端,不准 gemma4 本地)
if grep -q "gemma4:latest" "$HERMES_HOME/config.yaml"; then
  echo "[setup] 錯誤:config.yaml 仍指向本地 gemma4,先修 config 再啟動" && exit 1
fi

# 4) 啟動 gateway(長駐;建議之後改用 launchd/com.hermes.telegram-gateway.plist)
if ! grep -q "^TELEGRAM_BOT_TOKEN=" "$ENV_FILE"; then
  echo "[setup] 尚無 TELEGRAM_BOT_TOKEN——先去 BotFather /newbot 拿 token 再跑一次本腳本"
  exit 0
fi
cd "$HERMES_REPO"
echo "[setup] 啟動 hermes telegram gateway(官方 CLI;常駐請載入 launchd plist)"
exec "$HERMES_REPO/.venv/bin/hermes" gateway start
