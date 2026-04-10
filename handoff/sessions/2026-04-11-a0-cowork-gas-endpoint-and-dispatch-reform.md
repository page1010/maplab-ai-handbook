# A0 Cowork Session — 2026-04-11
# 主題：A6 GAS Endpoint 建立 + A0 調度系統性改革

> 檔名說明：gas-endpoint = 技術產出，dispatch-reform = 系統改進（本 session 真正的高價值產出）

## 故事線（前因後果）

### 起點：Owner 啟動 A0，要求接續 A6 測試
- A6 Telegram bot 剛恢復（04-09 整天掛，Claude Code CLI 額度耗盡）
- Owner 已測完第一組場景（李晴宜週歲 20人 $15K），回覆品質 OK，毛利率 79.7%
- 問題：createQuote 無法自動觸發（A6 跑在 terminal，不能點 Sheet 按鈕）

### 第一階段：A0 連續犯錯（3 輪 Owner 糾正）

**錯誤 1 — 從 code 推論系統行為**
- A0 讀 bot_a6.py 看到 `claude -p` → 斷定「A6 只是文字生成機器、毛利率是幻覺」
- Owner 糾正：「這一定是錯的，你看前幾個 session 紀錄好嗎」
- 修正：翻 session log 發現 Owner 上個 session 已確認「回覆的不錯」

**錯誤 2 — 把 LINE 和 Telegram 搞混**
- A0 提議修改 LineWebhook.gs 加報價路由
- Owner 糾正：「line? a6 在 telegram 上，有很多是有人做錯在詳查一下」
- 修正：LINE OA（客戶對話存檔）和 A6 Telegram（業務報價助手）完全獨立

**錯誤 3 — 不理解使用者視角**
- A0 開了 8 個 worktree 各自從零分析，Owner 完全看不到
- Owner 最終自己說出核心問題：「A6 運行在 claude code 終端機上，他無法點擊按鈕」

**根本原因：A0 沒有 Owner 的使用者視角，從 code 結構推論系統行為**

### 第二階段：系統性反思（本 session 最高價值）

Owner 提出三個系統層改進：

1. **架構圖要從使用者視角畫** — 三入口（Chrome/Telegram/Cowork）× 多角色，不是從 code 檔案結構畫
2. **委派前「快速開會」協議** — 7 問題 pre-check（我們是誰/前面做了什麼/接下來做什麼/為什麼/系統意義/更快的路/從哪繼續）
3. **A6 訓練三問題方法論推廣** — 教操作路徑不教理論

### 第三階段：方案二實作
- Owner 確認方案二（GAS 加 HTTP endpoint，不動 LineWebhook.gs）
- 建立 ApiEndpoint.gs（doPost 路由 createQuote/createSlide）
- .claspignore 排除 LineWebhook.gs
- bot_a6.py 加 _trigger_gas_quote() + _extract_form_data()
- clasp push 成功 → GAS 部署 Web App v1
- curl 測試通過：Q20260411053724 建立成功
- Chrome 眼見為憑：SALES_INTAKE 第 19 行確認
- bot_a6 重啟，帶 GAS_QUOTE_URL

## 本 session 產出清單

### 已 commit 到 main：
- [x] `scripts/apps-script/ApiEndpoint.gs` — GAS HTTP endpoint
- [x] `scripts/apps-script/.claspignore` — 排除 LineWebhook.gs
- [x] `bot_a6/bot_a6.py` — 加 HTTP call 邏輯
- [x] `bot_a6/.env.example` — 加 GAS_QUOTE_URL
- [x] `recalls/A6_recall_compact.md` — 加自動產報價單說明
- [x] `docs/a0-dispatch-operations-manual.md` — A0 調度操作手冊（架構圖 + 委派協議 + 踩坑記錄）
- [x] clasp push + GAS Web App v1 部署
- [x] bot_a6/.env 加 GAS_QUOTE_URL（不 commit，.gitignore 保護）

### 寫進 auto-memory：
- [x] `feedback_verify_before_analyze.md` — 先查 session log 再讀 code
- [x] `feedback_a0_dispatch_protocol.md` — 委派前開會對齊 + 三問題推廣 + 使用者架構圖

### ⚠️ 出現在對話但未做 / 未 commit：
- [ ] **Telegram e2e 測試** — GAS endpoint 通了，但還沒用 Telegram 真的發報價指令測完整流程
- [ ] **SALES_INTAKE 測試資料清理** — Q20260411053724 是 curl 測試，需要刪除或標記
- [ ] **QA-1 ~ QA-7 場景測試** — 全未執行
- [ ] **舊 bot/ DEPRECATED 清理** — PID 827 仍在跑，launchd 未 unload
- [ ] **架構圖存進 repo** — 目前只在 auto-memory 和 dispatch-manual 裡，沒有獨立的 docs/system-architecture.md
- [ ] **A6 recall 裡 formData JSON block 格式** — 需要確認 Claude 是否穩定輸出正確格式
- [ ] **handleQuoteRequest_ 缺三個新欄位** — depositAmount / dietaryNotes / floorFeeMode（verified-e2e tag 之後新增的）

## 接手者指南

**從哪裡開始：**
1. 讀本文件了解前因後果
2. 讀 `docs/a0-dispatch-operations-manual.md` 了解使用者視角架構
3. 最優先：用 Telegram 發報價指令做完整 e2e 測試

**關鍵檔案：**
- `scripts/apps-script/ApiEndpoint.gs` — 新建的 HTTP endpoint
- `bot_a6/bot_a6.py` — 加了 _trigger_gas_quote()
- `bot_a6/.env` — GAS_QUOTE_URL 已填入
- GAS Web App URL: `https://script.google.com/macros/s/AKfycbwUZ0JDyCYd8aucbOvwX0Oworjz11Iizy0QUx-1Go4pkxccb2Q6IYvTbaG34GVUNBdF/exec`

**已知風險：**
- A6 的 Claude 回覆不一定穩定輸出 JSON block → _extract_form_data() 可能抓不到 → fallback 到純文字回覆
- handleQuoteRequest_ 缺 depositAmount/dietaryNotes/floorFeeMode → 新欄位用預設值

**復原方案（如果出問題）：**
- GAS 部署可直接刪除（管理部署作業 → 刪除）
- bot_a6/.env 清空 GAS_QUOTE_URL → bot 自動 fallback 舊行為
- git revert + clasp push 回推
