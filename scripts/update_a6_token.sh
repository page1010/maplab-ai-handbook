#!/bin/bash
# update_a6_token.sh — 更新 A6 bot token 並重啟服務
# 用法：bash scripts/update_a6_token.sh "新的TOKEN"

set -e

NEW_TOKEN="$1"
ENV_FILE="/Users/pagemacmini/maplab-ai-handbook/bot_a6/.env"

if [ -z "$NEW_TOKEN" ]; then
  echo "❌ 用法：bash scripts/update_a6_token.sh \"新的TOKEN\""
  exit 1
fi

# 驗證 token 格式（數字:英數字）
if ! echo "$NEW_TOKEN" | grep -qE '^[0-9]+:[A-Za-z0-9_-]+$'; then
  echo "❌ Token 格式不對，請確認從 @BotFather 拿到的格式（例：123456789:AAF...）"
  exit 1
fi

echo "🔄 更新 A6_BOT_TOKEN..."
# 用 sed 替換 .env 中的 token
sed -i '' "s|^A6_BOT_TOKEN=.*|A6_BOT_TOKEN=${NEW_TOKEN}|" "$ENV_FILE"

echo "✅ .env 已更新"

echo "🔄 重啟 A6 bot (launchd)..."
launchctl kickstart -k "gui/$(id -u)/com.maplab.a6bot"

sleep 2

# 驗證 bot 是否 online
echo "🔍 驗證 bot 狀態..."
STATUS=$(launchctl list | grep com.maplab.a6bot | awk '{print $2}')
if [ "$STATUS" = "0" ]; then
  echo "✅ A6 bot 已重啟，運行中 (exit code 0)"
else
  echo "⚠️  launchd 狀態碼：$STATUS，請查看 bot_a6/launchd_stderr.log"
fi

echo ""
echo "📋 操作完成。請到 Telegram 測試 A6 bot 是否正常回應。"
