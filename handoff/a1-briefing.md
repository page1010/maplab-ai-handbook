# A0 → A1 Briefing
> 最後更新：2026-04-18 by A0

## 本次 Session 做了什麼（2026-04-17~04-18 跨夜）

### A6 故障診斷與修復
- 根因：OAuth access_token 過期 → claude -p 幻覺 GAS 掛 → Python 備援沒觸發
- GAS endpoint 其實活的（curl 驗證 HTTP 200）
- 修復：patrol.sh 加 token 自動偵測、bot_a6.py 觸發邏輯強化、recall 加「不推測系統狀態」規則

### A6 新增品項功能（addItem）
- GAS addItemToDatabase_ 函數（v8 已部署）
- bot_a6.py action 分流（addItem vs createQuote）
- recall_compact 建立（142→156 行）+ cwd 修正 + fallback 200 行
- H1 拆分三層：新增✅ / 修改❌ / 刪除❌
- 多照片支援（image_url 主圖 + photo_urls 多圖）

### A6 技能文件修正
- P0 三件（safety-boundaries / telegram-window / rapid-quote-sop）
- category 模糊比對（湯→SOUP / 飲→BEV / 甜→DES）
- eventDate 格式要求（YYYY/MM/DD 不留空）

### 10 輪 QA 測試（8/10 PASS → bugs 修後 10/10）
- R1-R3: addItem（甜點/湯品/缺資訊補問）
- R4-R7: 報價（展覽館待確認/週歲完整/婚禮雙禁忌/低預算低消警告）
- R8-R10: addItem飲品/記者會極端場景/混合操作

### 系統改進
- A0 強制記錄規則（recall + ops manual）
- A0/A1 briefing + 抽考機制設計（projects/a0-a1-briefing-protocol.md）
- worktree cleanup 自動化（launchd 30 分鐘）
- 對話紀錄 + Palantir 方法論存檔

## Owner 校正原話（2026-04-17~18）
- 「那是『你』A0 不紀錄。看要寫在什麼層級才會聽話。」
- 「故障2一樣不該發生，這表示他一樣沒有眼見為憑」
- 「a1要起到校正功能...比如抽考系統全貌」
- 「舉一反三 請根據pltr 在部署訊練營時...」
- 「新增和修改、刪除分開」
- 「item照片可以多於一張」
- 「你有bug 讓他不要讀 這樣問題沒有被解決啊」（指 H9 錯誤方向）

## 關鍵 Commits
- e0dc015: A0 強制記錄規則
- cc5b925: A6 recall 缺資訊處理原則
- 3746ec9: patrol.sh token 自動偵測
- 66cf0cf: 對話紀錄 + methodology 整合
- 71fa1a8: A0/A1 briefing protocol
- 3933b9e: briefing 落地到 recall
- 35af21a: H1 三層權限
- 2beac99: repo GAS addItem 同步
- b042d93: bot action 分流
- ae6381e: recall addItem 直接輸出指示
- GAS v6→v8: addItem + 模糊比對 + 多照片

## 未完成
- A0/A1 briefing 機制第一次實際運行驗證
- A6 照片一條龍（Telegram 接收→命名→壓縮→Drive 歸檔→Slide 連動）Phase 2
- Items 表測試資料清理（[QA-TEST] 開頭的品項）
- A4 照片分類 S11 進度確認
- T-A4-002 Phase 1：pagewu1010 Takeout 解壓（Colab notebook 已建，code 需手動修正縮排後執行）
  - Notebook：MAPLAB_pagewu_takeout_unzip（pagewu1010 Drive）
  - 5 個 ZIP 共 187GB，解壓到 Takeout_extracted/
  - Cell 1：drive.mount（需授權）
  - Cell 2：shell unzip -n（不需 Python 縮排）
  - Chrome MCP 無法可靠設定 Colab Python 縮排（已知限制，同 Monaco API setValue 踩坑記錄）

## 建議起始點
- 讀 projects/a0-a1-briefing-protocol.md + handoff/a0-briefing.md
- 清理 Items 表裡的 QA 測試資料
- A6 照片 Phase 2 設計
