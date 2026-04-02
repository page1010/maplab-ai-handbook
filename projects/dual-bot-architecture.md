# MAPLAB 雙 Bot 架構設計規劃
**版本**: v1.0 | **日期**: 2026-04-03 | **作者**: A1

---

## 一、現況說明

| 項目 | 現況 |
|------|------|
| A1 bot（`bot/bot.py`） | 拉 `start_bot.sh` 進 Terminal 視窗跑 |
| A6 bot（`bot_a6/bot_a6.py`） | 已寫好，尚未啟動 |
| Claude Code 連線方式 | 兩個 bot 都用 `claude -p` 子程序呼叫（**每次對話獨立啟動，不共用 session**） |

**重要觀念**：這裡的 `claude -p` 是**非互動式單次呼叫**，不是「進入一個 Claude Code 視窗對話」。每則訊息進來 → 起一個 subprocess → 拿結果 → 結束。兩個 bot 同時跑不會互搶 session。

---

## 二、架構圖

```
Mac mini（24/7 開著）
│
├── launchd Daemon #1 ─→ A1 bot (bot/bot.py)
│   Telegram: A1 私人視窗（你專用）
│   呼叫：claude -p [A1 system prompt + 訊息]
│   功能：系統巡檢、狀態查詢、agent 管理
│
└── launchd Daemon #2 ─→ A6 bot (bot_a6/bot_a6.py)
    Telegram: A6 群組（你 + 業務）
    呼叫：claude -p [A6 system prompt + 訊息]
    功能：報價、品項修改、查詢案件
```

---

## 三、兩種啟動方式比較

| 方式 | 優點 | 缺點 | 適合時機 |
|------|------|------|---------|
| **A. 拉 .sh 進 Terminal**（現在） | 看得到 log、好 debug | 要開兩個視窗、關掉就停 | 開發測試期 |
| **B. launchd 後台 Daemon**（目標） | 開機自動啟動、不用視窗、Mac mini 重開機自動恢復 | log 要去讀檔案 | 正式運行 |

**建議**：開發期用 A，確認 OK 後切 B。

---

## 四、使用者需求（User Stories）

### Owner（你）的需求
| 場景 | 需求 | 對應 bot |
|------|------|---------|
| 在外面手機查系統狀態 | Telegram 私訊 A1 → `/status` | A1 私人窗口 |
| 業務來電急問報價 | 群組說「報價 王小明 婚禮 80人 預算6萬」 | A6 群組 |
| 看業務下了什麼指令 | 群組訊息你都看得到（透明） | A6 群組 |
| Mac mini 重開機後 | 兩個 bot 自動恢復，不用手動操作 | launchd |

### 業務的需求
| 場景 | 指令格式 | 結果 |
|------|---------|------|
| 急件報價 | `報價 客名 類型 人數 預算` | A6 出 QUOTE_WORKBENCH 草稿 |
| 品項修改 | `你幫我把X換成Y` | A6 輸出 diff + 金額差 |
| Y 不在品項表 | A6 問業務輸入臨時成本 | 記入 REVISION_LOG |
| 查詢案件狀態 | `查 客名` | A6 查 SALES_INTAKE 回傳 |

---

## 五、實作步驟

### Phase 1 — 開發驗證（用兩個 Terminal 視窗）

```bash
# 視窗 1：A1 bot
cd /Users/pagemacmini/maplab-ai-handbook/bot
bash start_bot.sh

# 視窗 2：A6 bot（先確認 .env 填好）
cd /Users/pagemacmini/maplab-ai-handbook/bot_a6
source ../bot/venv/bin/activate   # 共用 venv，或 bot_a6 建自己的
python3 bot_a6.py
```

**驗收條件**：
- [ ] 群組傳「報價 測試 婚禮 80人 預算6萬」→ A6 回應
- [ ] 私訊 A1 bot → `/ping` → 回應正常
- [ ] 兩邊同時傳訊息 → 各自處理，不干擾

### Phase 2 — 正式 launchd（兩個 Daemon 都掛）

A6 的 plist 已建好（`bot_a6/com.maplab.a6bot.plist`）。

```bash
# 掛 A6 launchd
cp bot_a6/com.maplab.a6bot.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.maplab.a6bot.plist

# 確認兩個都在跑
launchctl list | grep maplab
```

### Phase 3 — 共用 venv（避免重複安裝）

目前 `bot/venv` 已有 python-telegram-bot。建議 A6 直接共用：

```bash
# bot_a6/run_daemon.sh 裡改成
source /Users/pagemacmini/maplab-ai-handbook/bot/venv/bin/activate
```

---

## 六、待確認項目（Owner Action）

| # | 項目 | 說明 |
|---|------|------|
| 1 | A6 bot token | @BotFather 申請新 bot，填入 `bot_a6/.env` |
| 2 | 業務 Telegram user ID | 業務傳訊息給 @userinfobot，把 ID 填入 `.env` |
| 3 | Phase 1 驗收 | 先用兩個 Terminal 視窗測試再切 launchd |

---

## 七、常見問題

**Q: 兩個 bot 同時呼叫 `claude -p`，會不會搶資源？**  
A: 每個 bot 內部有 semaphore（同時只跑一個 claude 子程序），兩個 bot 各自排隊，互不影響。最壞情況是同時各有一個 claude 在跑，Mac mini M 系列完全吃得下。

**Q: A6 群組訊息，業務說的話我看得到嗎？**  
A: 是的，你和業務都在群組，所有對話雙方都看得到，透明。

**Q: Claude Code 要持續登入嗎？**  
A: `CLAUDE_CODE_OAUTH_TOKEN` 已寫在 `.env`，兩個 bot 共用同一個 token，不需要額外登入。
