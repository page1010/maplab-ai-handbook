# MAPLAB Project State

## Current Task
Telegram Bot Daemon 建立 — 獨立 Python long-polling daemon

## Last Completed
Telegram bot daemon 建立完成（bot/ 目錄，launchd 自啟，auto-reconnect）

## Next Task
1. 填入 bot/.env（TELEGRAM_BOT_TOKEN）
2. 跑 `bash bot/start_bot.sh` 驗證連線
3. 安裝 launchd plist 讓 bot 開機自啟
4. Python pipeline collector.py 測試跑通（原有任務）

## Blockers
- TELEGRAM_BOT_TOKEN 尚未填入 bot/.env（需要手動 cp .env.example → .env）
- Google Cloud credentials.json 待建立（pipeline 任務）

## Notes
Mac Mini M4 尚未到貨，n8n 等到貨後安裝

---

## Telegram Bot 斷線根因分析 (2026-03-26)

### 舊方案：Claude Code MCP Plugin (plugin:telegram:telegram)
**根本問題：MCP plugin 不是 daemon**
- MCP tool 是「工具呼叫」，只在 Claude Code session 活躍時存在
- 每次 Claude Code 重啟，polling session 就斷線
- 需要手動執行 `/mcp refresh Telegram` 才能重新連上
- 沒有 auto-reconnect，網路閃斷即永久斷開
- 無法在 Claude Code 離線時收訊息

### 新方案：獨立 Python Daemon (bot/bot.py)
**架構：**
```
Mac Mini
├── launchd (PID 1)
│   └── auto-start com.maplab.telegrambot
│       └── run_daemon.sh → bot.py
│           └── python-telegram-bot (long polling)
│               └── Telegram API <-> Owner (chat_id=1077768811)
└── Claude Code (independent, on-demand)
```

**優點：**
- 完全獨立於 Claude Code，24/7 常駐
- launchd KeepAlive=true：crash 後 30 秒自動重啟
- run_polling 內建 reconnect logic，網路斷開會自動重試
- PYTHONUNBUFFERED=1 確保 log 即時輸出
- 所有訊息記錄到 bot/bot.log

### Bot 操作指令
```bash
# 安裝依賴 + 首次啟動（前台測試）
bash bot/start_bot.sh

# 安裝 launchd 自啟
cp bot/com.maplab.telegrambot.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.maplab.telegrambot.plist

# 查看狀態
launchctl list | grep maplab

# 查看 log
tail -f bot/bot.log
tail -f bot/launchd_stdout.log

# 停止
launchctl unload ~/Library/LaunchAgents/com.maplab.telegrambot.plist

# 重啟
launchctl kickstart -k gui/$(id -u)/com.maplab.telegrambot
```

### 重啟後確認步驟
1. `launchctl list | grep maplab` — 確認 PID 存在（非 -）
2. 在 Telegram 傳 `/ping` 給 maplab claude bot
3. 收到 `pong` = bot 正常運作
