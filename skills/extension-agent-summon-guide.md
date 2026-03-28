# Extension Agent 召喚技能書 — 透過 MAPLAB Agent Commander 啟動 Agent

版本：v1.0 | 建立：2026-03-28 | 維護者：A0

---

## 目的

透過 Chrome Extension（MAPLAB Agent Commander）在任何 Chrome 瀏覽器上召喚 A0-A8 任一角色，讓其在 Claude 側邊欄中以正確身份啟動。

Mac mini 和 Windows 都有安裝 Extension，兩邊都能用。

---

## 召喚步驟（已驗證 2026-03-28）

### Step 1. 開啟 Extension
在 Chrome 瀏覽器點擊 MAPLAB Agent Commander 圖示（Side Panel 模式）

### Step 2. 確認 GitHub 連線
Extension 會從 GitHub 讀取：
- CURRENT_STATUS.md → 系統版本、進行中任務、Blockers
- AGENT_RECALL_PROMPTS.md → 各角色 prompt

確認頂部顯示系統版本號（目前 v5.2）。如果沒有，檢查 GitHub Raw Base URL 設定。

### Step 3. 選角色
下拉選單選 A0-A8 任一角色。Extension 會：
1. 從 AGENT_RECALL_PROMPTS.md 讀取該角色的 code block（正則：/## (A\d)[^\n]*\n[\s\S]*?```\n([\s\S]*?)```/g）
2. 填入 textarea
3. 從 CURRENT_STATUS.md 篩出該角色的任務顯示在 role-status 區

### Step 4. 複製 Startup Prompt
點「複製 Startup Prompt」按鈕 → navigator.clipboard.writeText()

### Step 5. 貼到 Claude
- 開新 Claude tab 或側邊欄
- Ctrl+V / Cmd+V 貼入
- Claude 會按照 prompt 啟動：讀 CURRENT_STATUS → 讀 AGENT_RULES → 輸出 Startup Check

---

## 平台差異

| 平台 | 使用方式 | 注意事項 |
|------|---------|---------|
| Windows Chrome | 側邊欄直接用 | 貼到同一瀏覽器的 Claude 側邊欄 |
| Mac mini Chrome | 側邊欄直接用 | 貼到 Claude 側邊欄或終端機 Claude Code |
| A0 Cowork 遠端 | 透過 Chrome Remote Desktop 操作 Windows Extension | 精度限制，大按鈕可點，打字用 CRD 傳送文字 |

---

## 角色可用清單

| 角色 | Extension 可用 | 正確貼到哪裡 |
|------|---------------|-------------|
| A0 | ✅ | Cowork（但 Cowork 有自己的 auto-memory，通常不需要手動召喚）|
| A1 | ✅ | 終端機 Claude Code |
| A2 | ✅ | Chrome 側邊欄 |
| A3 | ✅ | Chrome 側邊欄 |
| A4 | ✅ | Chrome 側邊欄（搭配 Colab tab）|
| A5 | ✅ | Chrome 側邊欄（搭配 Google Sheets tab）|
| A6 | ✅ | Chrome 側邊欄 |
| A7 | ✅ | Chrome 側邊欄 |
| A8 | ✅ | Chrome 側邊欄（待建立）|

---

## overdue 偵測

Extension 會檢查最近 8 筆 commit：
- 如果任務狀態是 🔄 但最近 commit 都沒有該 Task ID → 顯示 ⏰ 警示徽章
- 純警示，不影響 prompt

---

## A0 遠端召喚 SOP（Mac mini → Windows Extension）

1. Chrome Remote Desktop 連上 DESKTOP-PAGEHOME
2. 切到有 Extension 的 Chrome 窗口
3. 點 Extension Side Panel 圖示
4. 選角色
5. 點「複製 Startup Prompt」
6. 點 Claude 側邊欄的「Reply to Claude」
7. Ctrl+V 貼入（或用 CRD 傳送文字功能）

---

## 經驗紀錄

### 2026-03-28 首次 Extension 召喚成功
- Owner 在 Windows 和 Mac mini 都有安裝 Extension
- Mac mini 的 Extension 可以直接使用（不需要走遠端桌面）
- AGENT_RECALL_PROMPTS.md 裡 A0-A8 的格式都符合 Extension 正則解析

---

*建立者：A0 Cowork Dispatch Secretary | 2026-03-28*
