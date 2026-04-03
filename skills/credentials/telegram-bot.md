# Telegram Bot 鑰匙技能書

版本：v1.0 | 建立：2026-03-29 | 維護者：A1

---

## 鑰匙位置

| 變數 | 位置 | 說明 |
|------|------|------|
| `A6_BOT_TOKEN` | `bot_a6/.env`（本機，git 不追蹤） | A6 bot token（由 @BotFather 發放） |
| `OWNER_USER_ID` | `bot_a6/.env` | `1077768811` |

> **Token 更換流程（一行指令）：**
> 1. Telegram → @BotFather → `/revoke` → 選 A6 bot → 取得新 token
> 2. 執行：`bash scripts/update_a6_token.sh "新TOKEN"`
> 3. 完成，bot 自動重啟

---

## 取用方法

```bash
# 從 .env 讀取 token（若 bot/ 目錄存在）
grep TELEGRAM_BOT_TOKEN /path/to/bot/.env
```

或在 Python 腳本中：
```python
import os
from dotenv import load_dotenv

load_dotenv("bot/.env")
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
```

### 直接用 curl 發訊息（不依賴 bot.py）

```bash
TOKEN="your_bot_token"
CHAT_ID="1077768811"

curl -s -X POST "https://api.telegram.org/bot${TOKEN}/sendMessage" \
  -H "Content-Type: application/json" \
  -d "{\"chat_id\": \"${CHAT_ID}\", \"text\": \"訊息內容\", \"parse_mode\": \"Markdown\"}"
```

---

## 可用範圍

| 允許操作 | 說明 |
|---------|------|
| ✅ 接收訊息 | getUpdates / webhook |
| ✅ 發送訊息 | sendMessage（純文字 + Markdown） |
| ✅ 發送圖片 | sendPhoto |
| ✅ 發送文件 | sendDocument |

---

## 禁止操作

- ❌ 修改 bot 設定（透過 @BotFather）
- ❌ 廣播給非 Owner 的 chat_id
- ❌ 儲存訊息內容到 GitHub（訊息可能含敏感資訊）

---

## A0 掛了時的備援

A1 可直接用 curl 發 sendMessage 通知 Owner，不依賴 bot.py daemon。
OWNER_CHAT_ID = `1077768811`。
