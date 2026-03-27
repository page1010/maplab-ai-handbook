# Remote Desktop Agent Bridge — A0 跨機器 Agent 監控技能書

版本：v1.0 | 建立：2026-03-27 | 維護者：A0 Cowork Dispatch Secretary

---

## 目的

A0 運行在 Mac mini（Cowork 模式），但部分 Agent（特別是 A4 Pipeline、A5 Master Data）的工作環境在 Windows 主機（DESKTOP-PAGEHOME）上。本技能書記錄如何透過 Chrome Remote Desktop 從 Mac mini 遠端監控和操作 Windows 上的 Agent。

---

## 物理架構

```
Mac mini (pagemacmini)                    Windows (DESKTOP-PAGEHOME)
├── A0 Cowork (我)                        ├── Chrome 視窗 1（螢幕 1）
├── A1 Claude Code (終端機)               │   ├── Google Sheets（A5 Master Data）
├── Telegram Bot daemon                   │   ├── Claude 側邊欄（Opus 4.6，扮演各角色）
└── GitHub repo (maplab-ai-handbook)      │   └── 各種工作 tab
                                          ├── Chrome 視窗 2（螢幕 2）
                                          │   ├── MAPLAB Agent Commander（Chrome Extension）
                                          │   ├── YouTube（背景音樂）
                                          │   └── 各種工作 tab
                                          └── 可能有 Google Colab（A4 Pipeline 執行環境）
```

---

## 連線步驟（已驗證 2026-03-27）

### Step 1. 開啟 Chrome Remote Desktop

在 Mac mini 的 Chrome MCP tab 裡導航到：
```
https://remotedesktop.google.com/access
```

### Step 2. 選擇目標電腦

帳號：pagewu1010@gmail.com
遠端裝置列表會顯示：
- **DESKTOP-PAGEHOME** — Windows 主機（🟢 線上 = 可連）
- AppliedeMacBook-ProPAGE — MacBook（通常離線）
- mina — 另一台（通常離線）

點擊 **DESKTOP-PAGEHOME**。

### Step 3. 輸入 PIN

PIN 碼：透過 Chrome MCP 的 form_input 填入 PIN 欄位，點擊「提交 PIN 碼並連線」按鈕。
（PIN 由 Owner 提供，不記錄在技能書中）

### Step 4. 等待連線

等待 3-5 秒，tab 標題會變成 "DESKTOP-PAGEHOME"，表示連線成功。

### Step 5. 辨識畫面

Windows 有雙螢幕，Chrome Remote Desktop 預設顯示全部。
可用 `Cmd+Option+M`（Mac）切換螢幕，或點右側 `>` 箭頭開啟工具列 → Display → 選擇 Display 1 / Display 2。

---

## Windows 上的 Agent 辨識指南

### 已知視窗配置（2026-03-27 確認）

| 位置 | 視窗 | 角色 | 辨識方式 |
|------|------|------|----------|
| 螢幕 1 左 | Google Sheets | A5 Master Data | tab 標題含 "MAPLAB"，有 Item/Specials/DropdownHelper 工作表 |
| 螢幕 1 中 | Claude 側邊欄 | 當前活躍角色 | Opus 4.6，看對話內容的「你是 MAPLAB Ax」判斷角色 |
| 螢幕 2 右 | MAPLAB Agent Commander | A1 控制台 | 深色面板，顯示 v5.0、任務列表、Startup Prompt 按鈕 |
| 螢幕 2 中 | YouTube | 背景 | 不是 Agent |
| 不確定位置 | Google Colab | A4 Pipeline | tab 標題含 "Colab"，notebook 名稱含 pipeline 或 vision |

### 辨識技巧

1. **看 Chrome tab 標題** — zoom 放大 tab bar 讀標題
2. **看 Claude 側邊欄的對話內容** — 會有「你是 MAPLAB Ax [部門名稱]」
3. **看 Agent Commander** — 右側深色面板顯示當前角色和任務
4. **看 Google Sheets 的工作表名稱** — 底部 tab（Item、Specials、Menu 等）

---

## 操作能力與限制

### 可以做的事
- 透過 Chrome MCP 在遠端桌面裡點擊（大面積元素）
- 截圖查看 Windows 上所有視窗的狀態
- 切換螢幕查看不同 Agent 的工作
- 查看 Google Colab 的執行狀態（A4 是否還在跑）

### 不能做的事
- 不能操作 Chrome Remote Desktop 以外的 popup 窗口（如 Google OAuth 帳戶選擇彈窗）
- 遠端操作有延遲（每個動作 1-3 秒）
- 如果 Windows Chrome 彈出新窗口（不是 tab），可能需要 Owner 手動處理
- 不能直接存取 Windows 檔案系統（需要透過 Chrome 或 Google Drive）
- **不能透過遠端桌面在 Claude 側邊欄輸入文字**（IME 衝突 + 鍵盤映射問題，字元丟失或亂碼）
  - 替代方案：A0 準備好指令文字 → Owner 手動貼到 Windows 的 Claude 側邊欄

---

## 常見場景

### 場景 1：確認 A4 Pipeline 是否還在跑
1. 連上 DESKTOP-PAGEHOME
2. 找 Google Colab tab（看 tab 標題）
3. 點進去看 cell 執行狀態（轉圈圈 = 在跑，停了 = 斷線）
4. 如果斷了，看最後的 output 判斷進度
5. 需要重啟 → 點 Runtime → Run all / Run from here

### 場景 2：查看某個 Agent 的工作狀態
1. 連上 DESKTOP-PAGEHOME
2. 找 Claude 側邊欄或 Agent Commander
3. zoom 截圖讀取對話內容 / 任務狀態
4. 回報給 Owner

### 場景 3：跟 Windows 上的 Agent 對話
1. 連上 DESKTOP-PAGEHOME
2. 找到 Claude 側邊欄
3. 點擊 "Reply to Claude" 輸入框
4. 打字送出訊息
5. 等待回覆，截圖讀取

### 場景 4：處理 OAuth / 權限彈窗
1. 如果是 Chrome tab 內的彈窗 → 可以直接點
2. 如果是獨立 popup 窗口 → 可能需要 Owner 手動處理
3. 如果是 Google 帳戶選擇 → 選 pagewu1010@gmail.com

---

## Chrome Remote Desktop 工具列

連線後，畫面右邊有個 `>` 小箭頭（可能需要 hover 才出現）：
- **Display** — 切換螢幕（Show all displays / Display 1 / Display 2）
- **Full screen** — 全螢幕模式（快捷鍵才完整）
- **Scale to fit** — 自動縮放適應視窗
- **Resize to fit** — 調整遠端解析度
- **Disconnect** — 斷開連線

快捷鍵：
- `Cmd+Option+M` — 切換螢幕
- `Ctrl+Alt+Shift+D` — 顯示設定

---

## A0 必拿理由

這是 A0 的核心能力之一。沒有這個技能，A0 無法：
- 監控 Windows 上跑的 Agent（A4 Colab、A5 Sheets）
- 確認 Agent 是否卡住或斷線
- 處理跨機器的 OAuth 授權問題
- 跟 Windows 上的 Claude 側邊欄 Agent 溝通

每次 A0 啟動且需要檢查 Windows 上的 Agent 狀態時，必拿此技能。

---

## 經驗紀錄

### 2026-03-27 首次連線
- Google 帳戶選擇彈窗（popup）會擋住連線流程，A0 無法操作 popup，需要 Owner 手動點
- Chrome Remote Desktop 的 PIN 輸入可以透過 Chrome MCP form_input 填入
- 雙螢幕在遠端桌面裡會壓縮成一個畫面，需要 zoom 才能看清楚小字
- 辨識 Agent 角色靠 Claude 側邊欄的對話內容和 Agent Commander 面板
- Windows 上有多個 Chrome 視窗各自扮演不同角色，需要仔細辨識 tab 標題

### 2026-03-27 遠端點擊精度問題
- Chrome Remote Desktop 雙螢幕模式下，畫面被壓縮到一個 tab 裡顯示，小按鈕（如彈窗的 Connect/Ignore）很難精確點中
- 解法：操作小按鈕前，先切到單螢幕模式（右側 > 箭頭 → Display → 選 Display 1 或 Display 2），讓畫面放大後再點
- 或使用 Cmd+Option+M 快捷鍵切換螢幕
- 大面積元素（如 tab 切換、大按鈕）在雙螢幕模式下可以正常點擊

### 2026-03-27 「Claude Desktop wants to connect」彈窗真相
- 這個彈窗**不是 A0 遠端連線觸發的**
- 真相：這是 **Claude Desktop 應用程式**（裝在 Windows 上）偵測到 Chrome 瀏覽器有 Claude 側邊欄擴充套件，問要不要把瀏覽器命名並連接到 Claude Desktop
- 在螢幕 1 看到**兩個**這樣的彈窗：左邊 Chrome 窗口（A2 SEO Agent）和右邊 Chrome 窗口（A7 客服 Agent）都各有一個
- 這跟 Google OAuth 授權是完全不同的事
- 點 Connect 後效果：讓 Claude Desktop 能管理該 Chrome 瀏覽器的 Claude 側邊欄 session
- 點 Ignore 後效果：只是暫時關閉彈窗，下次還會出現

### 2026-03-27 Windows 螢幕 1 完整辨識結果
左半 Chrome 窗口：
- Tab: Google Ads multi... | Commits page1010/mapla... | Analytics MAPLABKITCHEN
- WordPress 後台 maplabkitchen.com RankMath SEO 面板
- Claude 側邊欄 Opus 1.6 → **A2 SEO Agent**（讀 CURRENT_STATUS.md、AGENT_RULES.md）
- 書籤列: MAPLAB A1、A7、Check A2 team GitHub...

右半 Chrome 窗口：
- Tab: MAPLAB A7 custo... | line問答... | 各種客戶 tab
- Google Drive 資料夾（客戶報價 CSV 文件）
- Claude 側邊欄 Opus 4.6 → **A7 客服 Agent**
- 右下角有 Canva 圖示

### 2026-03-27 遠端打字失敗（Chrome 側邊欄輸入框）
- 透過 Chrome Remote Desktop（Mac → Windows）在 Claude 側邊欄的「Reply to Claude」輸入框打字，無論用 type、clipboard paste (ctrl+v)、短英文，都只進去幾個字或亂碼
- 根因：(1) Mac IME 與 Windows IME 衝突 (2) Chrome Remote Desktop 鍵盤映射在富文字輸入框有問題 (3) 剪貼簿同步有延遲且字元可能丟失
- **結論：遠端桌面無法打字到 Claude 側邊欄**
- **替代方案：A0 準備好指令文字 → Owner 手動貼到 Windows 的 Claude 側邊欄**

### 單螢幕模式操作結論
- 切到單螢幕後辨識能力大幅提升（可以看清 tab 標題、按鈕文字、SEO 數據）
- 但小彈窗按鈕（~50px 寬）仍然點不中，遠端桌面座標偏移約 5-15px
- 鍵盤 Tab+Enter 會被 Chrome 側邊欄攔截，不是送到彈窗
- **結論：遠端操作適合「看」（監控、辨識、截圖報告），「點小按鈕」仍有困難**
- 大面積操作（切 tab、點 Google Drive 文件、在輸入框打字）應該可行

---

## 適用角色

| 角色 | 使用場景 | 能力等級 |
|------|---------|---------|
| A0 Cowork | 監控全部 Agent 狀態、跨機器橋接 | 完整使用（必拿技能） |
| A1 Claude Code | 透過 Telegram bot 推送 Windows 上的 Agent 狀態 | 間接使用（A0 監控後透過 bot 通知） |
| A2 SEO Agent | 如果在 Mac mini 的 Claude tab 被召喚，可以查看 Windows 上自己的 SEO 工作狀態 | 不適用（A2 自己跑在 Windows 上） |
| A4 Pipeline Agent | 確認 Colab 是否在跑 | A0 代為監控 |
| A5 Master Data | 確認 Sheets 是否有更新 | A0 代為監控 |

注意：目前只有 A0 有實際能力操作遠端桌面（透過 Cowork 的 Chrome MCP）。
其他 Agent 如果需要知道 Windows 上的狀態，應該透過 A0 查詢後回報。

---

*建立者：A0 Cowork Dispatch Secretary | 2026-03-27 | 基於實際操作經驗撰寫*
