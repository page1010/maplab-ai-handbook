# A1 → A0 Briefing
> 最後更新：2026-04-18 by A0（session 完整存檔後更新）

## Owner 最新校正（2026-04-17~18）
- 缺資訊不要卡報價：影響毛利率的必問，不影響的填「待確認」先出
- 測試必須標記 [QA-TEST]，操作必須即時記錄
- A6 claude -p 幻覺 GAS 掛了 → 教訓：不要推測系統狀態，只回報實際錯誤
- A0/A1 需要雙向 briefing + 抽考機制
- 新增品項和修改/刪除要分開（H1 三層權限）
- item 照片可以多於一張（photo_urls 陣列）
- **2026-04-18 系統性校正**：A0 犯了跟 A6 一樣的錯 — 推測而不驗證、被動等指令。核心原則：A0 要求任何 Agent 遵守的規則，A0 自己先遵守。行為框架已落地 recalls/A0_recall.md（主動推進 / 不確定先查 / 規則一致性）。

## 系統狀態（2026-04-19 EOD）
- A6 bot 運行中（B層對話自動存檔進行中）
- GAS v8 已部署（addItem + createQuote + createSlide + 模糊比對 + 多照片）
- Google OAuth token 有效（patrol.sh 已加自動偵測）
- A6 QA 10 輪全 PASS（含 R9 修 B4 後重測）
- worktree cleanup 自動化已上線（launchd 每 30 分鐘）
- LINE Developers Console Webhook URL 填入狀態：待 Owner 確認

## 已完成（本次 Session）
- A6 故障診斷 + 修復（OAuth / claude -p 幻覺 / Python 備援）
- addItem 功能全鏈路（GAS v8 → bot → Sheet）
- 多照片支援（photo_urls）
- H1 三層權限（新增✅/修改❌/刪除❌）
- 10 輪 QA 全 PASS
- A0/A1 briefing protocol 設計
- A0 強制記錄規則落地

## 未完成（下一個 Session 接手）
- A0/A1 briefing 機制第一次實際運行驗證
- A6 照片 Phase 2（Telegram→命名→壓縮→Drive→Slide 一條龍）
- Items 表 QA 測試資料清理（[QA-TEST] 11 筆）
- A4 S11 進度確認（Colab 疑斷線）
- T-A4-002 Phase 1：pagewu1010 Takeout 解壓待 Owner 手動啟動
  - Notebook：MAPLAB_pagewu_takeout_unzip（pagewu1010 Drive）
  - 5 個 ZIP 共 187GB，目標 Takeout_extracted/
  - Cell 2 縮排已知問題（Chrome MCP Monaco API setValue 限制），需 Owner 手動修正後執行

## 關鍵 Commits（2026-04-17~18）
- e0dc015: A0 強制記錄規則
- cc5b925: A6 recall 缺資訊處理原則
- 3746ec9: patrol.sh token 自動偵測
- 66cf0cf: 對話紀錄 + methodology 整合
- 71fa1a8: A0/A1 briefing protocol
- 3933b9e: briefing 落地到 recall
- 35af21a: H1 三層權限
- 2beac99: repo GAS addItem 同步 + 多照片
- b042d93: bot action 分流
- ae6381e: recall addItem 直接輸出指示（修 B4）
- GAS v6→v8: addItem + 模糊比對 + 多照片（已部署）
