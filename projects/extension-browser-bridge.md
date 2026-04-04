# Extension Browser Bridge — 使用者需求 v1.0

> 建立：2026-04-04 ｜ 紀錄者：A1 ｜ 狀態：待開發
> 目標 Agent：A1 + Chrome Extension

---

## 背景與動機

**根本問題**：A1（Claude Code）無法直接點擊瀏覽器按鈕、操作網頁表單。

**使用場景**：A6 業務快反應部隊（Telegram 報價助手）透過 Telegram 接收業務需求、出報價單。報價單系統的按鈕（有計數與建立新表單的程式碼）A6 運行在 Claude Code 裡，按不到。

---

## 使用者需求（Owner 確認，2026-04-04）

### 核心目標

```
A1 (Claude Code)
    ↓ 透過本地 HTTP（Port 9876）
Chrome Extension
    ↓ 偵測到新指令後自動觸發
claude.ai 側邊欄 Claude（眼睛+手的分身）
    ↓ 實際執行（填表單、點按鈕、截圖）
結果回傳給 A1
```

**A1 不需要 Owner 手動點任何按鈕，全部自主完成。**

### 兩條並行方案

| 方案 | 說明 | 優先 |
|------|------|------|
| 方案 A | 寫報價單按鈕的 URL 讓 A1 直接 HTTP 觸發（繞過瀏覽器） | 優先嘗試 |
| 方案 B | A1 → Extension → 側邊欄 Claude 分身（眼睛+手） | 通用解，場景更廣 |

---

## 方案 B 詳細設計需求

### 觸發流程

1. A1 把指令寫到 `localhost:9876/inject`
2. Extension content script **定時輪詢**（建議每 2 秒）偵測到新指令
3. Extension 把指令**自動注入**到 claude.ai 側邊欄對話框 + 自動送出
4. 側邊欄 Claude 執行（點按鈕、填表單、截圖回報）
5. 結果透過某種方式回傳 A1（待設計）

### 回傳機制（待確認）

- 選項 1：側邊欄 Claude 把結果輸出到頁面，Extension 截圖後寫到 `localhost:9876/result`，A1 輪詢讀取
- 選項 2：側邊欄 Claude 直接打 `localhost:9876/result` 回傳（需要 Claude 能執行 JS）

### 移除功能（已確認不需要）

- ~~「📋 從 Bot 抓取」按鈕~~（Telegram clipboard bridge）— 雞肋，刪除
- ~~Port 9876 作為剪貼板橋接~~（改為指令注入橋接）

---

## 開發前確認清單

- [ ] 確認方案 A 可行性：報價單按鈕是否有對應的 HTTP endpoint 可直接觸發？
- [ ] 確認 Extension 能否偵測 claude.ai 側邊欄 DOM（可能有 iframe 限制）
- [ ] 確認側邊欄 Claude 能否執行「模擬送出」（Enter / button click）
- [ ] 決定結果回傳機制（選項 1 vs 選項 2）

---

## 相關檔案

- Extension 程式碼：`chrome-extension/`
- Bot 程式碼：`bot/bot.py`
- HTTP bridge（現有）：`bot/http_bridge.py`（或確認實際檔名）
