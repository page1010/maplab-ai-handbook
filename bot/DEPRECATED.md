# ⚠️ DEPRECATED — 此資料夾已棄用

建立日期：2026-03-27
棄用日期：2026-03-27
棄用原因：走了彎路

---

## 棄用的東西

- **bot.py** — 獨立 Telegram bot，用 `claude -p` one-shot 呼叫，沒有持續記憶
- **ccbot** — Telegram ↔ tmux bridge，需要話題群組，過度複雜
- **com.maplab.telegrambot.plist** — launchd 自啟配置（已 unload）
- **start_bot.sh / run_daemon.sh** — 啟動腳本

---

## 正確方案

**終端機 Claude Code 常駐（tmux session 不關）+ Telegram MCP plugin**

- Claude Code 自己就有持續記憶（同一個 session）
- Telegram MCP plugin 是通訊管道，不是獨立 bot
- MCP plugin 斷線 → 在 Claude Code 裡 `/mcp refresh` 即可

---

## 成功的遠端操作方法

- **Chrome Remote Desktop 監控 Windows Agent**：能看、能辨識、能切螢幕
- **遠端打字到 Claude 側邊欄**：CRD「傳送文字」textbox 用 `form_input` 填入指令 → JavaScript `dispatchEvent` 送出
- 詳見 `skills/remote-desktop-agent-bridge.md`

---

## 教訓（見 experience-log.md EXP-F006）

1. **先修復現有系統，不要重新發明輪子** — MCP 斷線只需 `/mcp refresh`
2. **先研究現有認證機制，不要假設需要另外付費** — Claude Code 用 OAuth，不用買 API key
3. **聽懂 Owner 要的是什麼，不要把簡單問題複雜化** — 常駐 session 本來就有記憶
4. **Owner 給了提示就立即搜尋驗證，不要自己亂猜**
