# CURRENT_STATUS.md — 唯一最新狀態入口

> **所有 Agent 開工前第一個讀的檔案。這裡的資訊優先於所有其他文件。**
> 若其他文件與本檔衝突，以本檔為準。

最後更新：2026-04-24 14:30（A1 午後巡查）｜完整歷史存於 `archive/CURRENT_STATUS_2026-04-11_full.md`

---

## 系統版本

- **Version**: v6.0
- **Phase**: Phase 6 — 觀測性 + 業務閉環 + 策略循環
- **Status**: Active
- **v6.0 設計文件**: `projects/v6-architecture.md`
- **Sheets Dashboard**: `1fn_woqYI_RY9ggGHVidB5SMygAzwe4CL_SOPLhe91Jg` → Task Board + Owner Actions 分頁

---

## 當前進行中任務

| Task ID | 任務 | 負責 Agent | 狀態 | Task Card |
|---------|------|-----------|------|-----------|
| T-A1-V6-P2 | T-A1-V6-P2 | A1 | 🔄 進行中（4 分頁架構 + DropdownHelper 驗證完成、REVISION_LOG 精簡完成。下一步：建虛擬測試案例 →） | handoff/tasks/T-A1-V6-P2.md |
| T-A1-V6-P3 | T-A1-V6-P3 | A1 | 🔲 待開始（尚未開始。等 T-A1-V6-P2 完成後啟動。） | handoff/tasks/T-A1-V6-P3.md |
| T-A1-V7 | 系統進化 — 單一真相源 + 自動同步 + 瘦身 + 自動技能生成 + 自動壓縮 | A1 | 🔄 進行中（Phase 4 完成（44ecc8d 2026-04-17）— 自動技能生成 + Extension CRITICAL 修復 + patrol/Extension 邏輯統一 + git-pull launchd exit 78 修正。下一步：Phase 5 自動壓縮。） | handoff/tasks/T-A1-V7.md |
| T-A2-002-foodsafety-seo-cleanup | T-A2-002 — 食安 + 法規 SEO 字眼清理 | A2 | ⏸️ 阻塞（Repo 端已清理完成；WordPress 端需 Owner 手動刪除/修改 5 篇文章的食安字眼） | handoff/tasks/T-A2-002-foodsafety-seo-cleanup.md |
| T-A2-003-weekly-wp-audit | T-A2-003: 每週全站 WP 內容稽核排程 | A2 | 🔲 待開始（腳本已建好（wp-audit.sh / wp-audit-cron.sh）。待 Owner 用 /schedule 建立） | handoff/tasks/T-A2-003-weekly-wp-audit.md |
| T-A2-004 | 首頁結構優化 — 配合品牌色票微調 + 轉換路徑整理 | A2 | 🔲 待開始（任務卡建立。A0 已完成對標分析和色票微調。） | handoff/tasks/T-A2-004.md |
| T-A2A3-001-B | SEO 場景頁面 + 內連結（從 T-A2A3-001 分拆） | A2/A3 | ⏸️ 阻塞（子任務 3+4 完成（3 個場景頁 + 56 篇內連結）；子任務 5 等 Google 重新索引（7-14 天）） | handoff/tasks/T-A2A3-001-B.md |
| T-A2A3-001 | SEO 關鍵字頁面補足 | A2/A3 | ⏸️ 阻塞（子任務 1-4 完成；子任務 5 等 Google 重新索引驗證排名變化） | handoff/tasks/T-A2A3-001.md |
| T-A3-002 | Meta 廣告「慶生周歲派對」受眾確認 + 優化 | A3 | ⏸️ 阻塞中（受眾輪廓分析完成（693筆 Orders）。待執行：嘉義加入廣告地區、興趣條件精簡、策略一冷受眾上線。） | handoff/tasks/T-A3-002.md |
| T-A4-001 | Phase 4 Gemini 照片分類（2022-2026） | A4 | 🔄 進行中（S11/2024 補跑執行中）（S12(2025) ✅ DONE 7,645/7,642（45張補完，2026-04-15 08:58 完成）。S11(） | handoff/tasks/T-A4-001.md |
| T-A4-002 | T-A4-002 | A4 | 🔄 進行中（Phase 1 規劃完成 d0b3238 04-18；4 Phase 架構：解壓→Gemini分類→Slide選圖→旅遊caption；⚠️ Colab 解壓實際執行需待 S11 completion 後啟動） | handoff/tasks/T-A4-002.md |
| T-A5-002 | QUOTE_DRAFT 報價單欄位增強 | A5 | 🔴 CRITICAL（~372h無commit，D15+） | handoff/tasks/T-A5-002.md |
| T-A5-004 | createSlides.gs — Slide 報價簡報自動生成 | A5 | 🔴 CRITICAL（~372h無commit，D15+） | handoff/tasks/T-A5-004.md |
| T-A5-005 | 報價狀態追蹤同步 + Dashboard | A5 | 🔴 CRITICAL（~372h無commit，D15+） | handoff/tasks/T-A5-005.md |
| T-A5-006 | T-A5-006 | A5 | 🔲 待開始（尚未開始。等 T-A5-005 完成後啟動。） | handoff/tasks/T-A5-006.md |
| T-A6-001 | A6 LINE 業務報價助手系統 | A6 | 🔄 進行中（04-18 EOD：GAS v8部署+addItem+模糊比對+多照片；10輪QA全PASS（含R9修B4後重測）；H1三層權限；B層自動存檔運行中。未完成：照片Phase2、LINE webhook Owner確認。⚠️ Task Card T-A6-001.md 嚴重過時（仍顯示04-01斷點）需A6更新。） | handoff/tasks/T-A6-001.md |
| T-A6-002 | LINE 對話訓練資料收集計畫 | A6 | 💤 暫停（原計畫拆 Sheet 做訓練資料，04-07 重新規劃方向。等 Owner 決定是否需要 LINE 訓練資料及取得方式。） | handoff/tasks/T-A6-002.md |
| T-A7-001 | FAQ 回覆模板庫 + 補問流程 + 客戶分類標籤 | A7 | 💤 暫停（Phase 2 v2.0 完成，等 Owner 確認政策 + A5 欄位補齊）（Q1-Q10 重構完成（真實 CSV 驅動），下一步是 Q7/Q10 政策確認 + Phase 3 上線測試） | handoff/tasks/T-A7-001.md |
| T-A7-002 | A7 部門 80/20 優先任務清單 | A7 | ⏸️ 阻塞中（任務 6（Q1-Q10 實裝）+ 任務 10（技能書 v2.0）已完成。Phase 3A 剩任務 4（地區判斷）、7（流） | handoff/tasks/T-A7-002.md |
| T-GBP-001 | T-GBP-001 | Owner | 🔲 待開始（尚未開始。等 Owner 準備新圖片。） | handoff/tasks/T-GBP-001.md |
---

## Blockers（只列未解決的）

| 對象 | 問題 | 行動 |
|------|------|------|
| A1 | T-A1-V6-P2: 等 A6 實際報價測試 | 見 Task Card |
| A1 | T-A1-V6-P3: 前置 T-A1-V6-P2 需先完成 | 見 Task Card |
| A2 | T-A2-002-foodsafety-seo-cleanup: 等 Owner 操作 WordPress 後台 | 見 Task Card |
| A2 | T-A2-003-weekly-wp-audit: 等 Owner 建立排程 | 見 Task Card |
| A2/A3 | ⚠️ A1巡查 2026-04-20 09:00：T-A2A3-001/001-B 索引觀察期已達 **15 天**（04-05起），持續超過 7-14 天驗證窗口。Owner 尚未查 GSC，排名變化未確認 | Owner 查 GSC（逾期）→ A2 更新 Task Card |
| A2/A3 | T-A2A3-001-B: 等 Google 重新索引，預計 04-11 後可驗證 | 見 Task Card |
| A2/A3 | T-A2A3-001: 等 Google 重新索引，預計 04-11 後可驗證 | 見 Task Card |
| A3 | T-A3-002: 執行需登入 Meta Ads Manager（等廣告週期 + Owner 操作） | 見 Task Card |
| A4 | T-A4-002: 前置 T-A4-001 需先完成 | 見 Task Card |
| A4 | ⚠️ A1巡查 2026-04-19 10:00：T-A4-001 S11 14ed423(04-18) 存檔82.2%+Colab重啟，仍在執行中，待completion commit | Owner確認S11最新Colab狀態→補completion commit→啟動S13(~4,424張) |
| A4 | ⚠️ A1巡查 2026-04-19 21:00：S11 晚間確認仍無 completion commit（Colab restart 後超過 24h），Owner 需再次確認 Colab 狀態 | Owner 確認 Colab |
| A4 | ⚠️ A1巡查 2026-04-20 09:00：S11 Colab restart（14ed423 04-18）後已超過 **48h** 仍無 completion commit。高度懷疑 Colab 已崩潰或卡住。Owner 需立即確認：若已崩潰 → 重跑 S11 最後批次 → completion commit → 啟動 S13（~4,424張） | Owner 緊急確認 Colab（高優先）|
| A5 | ⚠️ A1巡查 2026-04-20 09:00：T-A5-002/004/005 CRITICAL D12+ ~270h無commit（last: cfeebd1 2026-04-09）。連續 2 次巡查 Owner 決策無回應，系統風險持續累積 | Owner 決策（緊急，D12+）|
| A4 | ⚠️ A1巡查 2026-04-20 14:30：A4 有新活動（454e7dc 12:24，Drive資料夾結構腳本）但 S11 仍無 completion commit，兩者並行。S11 狀態仍不明，與 Drive 腳本是分開任務 | Owner 確認 S11 是否另行處理（與 Drive 腳本無關）|
| 全系統 | ⚠️ A1巡查 2026-04-20 14:30：GCP Gemini API 帳單事件（658120d 11:02）— AI agent 串 API 導致 $3K/月（事件日期 2026-04-18）。財務風險尚未處理 | Owner 緊急：確認帳單上限 + 關閉非必要 API 呼叫 + 核查觸發來源（A4 Colab job 嫌疑最高）|
| A5 | ⚠️ A1巡查 2026-04-20 14:30：T-A5-002/004/005 計數更新 → ~276h 無 commit（D12+），午後巡查確認無新活動，Owner 決策仍無回應 | Owner 決策（D12+，持續升級）|
| A4 | ⚠️ A1巡查 2026-04-19 14:00：T-A4-002 Task Card（d0b3238）誤標前置 T-A4-001 為 ✅ 完成，S11 實際仍執行中（82.2%）。Phase 1 Colab 解壓不得在 S11 completion 前啟動。A4 需更正 Task Card 前置條件。 | A4 更正 Task Card |
| 全系統 | ℹ️ A1巡查 2026-04-19 14:00：Owner 今日提交 fix(framework) v1.2+v1.3 共 3 commits（e8a2aa3/6801266/4958a89）— 規則衝突優先級 + 回應校正標準。各 Agent 下次 session 開始時注意 AGENT_RULES.md 是否有更新。 | 各 Agent 留意 |
| A5 | T-A5-002: 等 Owner 確認（品項名稱改法、重複品項、I 欄用途） | 見 Task Card |
| A5 | T-A5-006: 前置 T-A5-005 需先完成 | 見 Task Card |
| A6 | ⚠️ A1巡查 2026-04-19 10:00：T-A6-001 Task Card 嚴重過時（仍顯示04-01斷點）— 10輪QA全PASS，系統活躍。LINE Developers Console Webhook URL填入狀態待Owner確認（Channel 1654658337） | A6 session 開始即更新 Task Card；Owner確認webhook填入 |
| A6 | T-A6-002: 等 Owner 決定方向 | 見 Task Card |
| A7 | T-A7-001: Q7 試吃政策需 Owner 決定、Q10 取消/改期政策需 Owner 決定、A5 外送費級距未建立 | 見 Task Card |
| A7 | T-A7-002: 任務 1/2/3 需 LINE bot 後台權限；任務 9 需 Owner 政策決策（Q7 試吃 + Q10 取消改期）；任務 5/8 需 TimeTree 權限 | 見 Task Card |
| Owner | T-GBP-001: 等 Owner 準備新圖片 | 見 Task Card |
| 全系統 | ⚠️ A1巡查 2026-04-24 09:00：**全系統 96h 靜止**（最後 commit 23e6c4c 2026-04-20 14:30，距今 4 天無任何 commit）。所有 🔄 進行中任務均超過 48h 無更新。系統是否正常運作？Owner 確認 | Owner 確認各 Agent 狀態；A1/A4/A6 若有進度即補 commit |
| A4 | ⚠️ A1巡查 2026-04-24 09:00：**T-A4-001 S11 升級 🔴 CRITICAL**（14ed423 2026-04-18 Colab重啟後已 **144h/6天** 無 completion commit）。Colab 幾乎可確定已崩潰。S13（~4,424張）完全無法啟動，T-A4-002 Phase 1 解壓亦被阻塞 | Owner **緊急**：確認 Colab 是否崩潰 → 重跑 S11 最後批次 → completion commit → 啟動 S13 |
| A5 | ⚠️ A1巡查 2026-04-24 09:00：**T-A5-002/004/005 升級 D15+（~372h 無 commit，last: cfeebd1 2026-04-09）**。連續 5 次巡查 Owner 決策無回應。業務報價系統已近 2.5 週停滯，風險為全系統最高。 | Owner **最高優先決策**：指定 A5 session 優先處理或告知 T-A5 整體暫緩策略 |
| 全系統 | ⚠️ A1巡查 2026-04-24 09:00：**GCP Gemini API 帳單持續 6 天未處理**（658120d 2026-04-18，$3K/月）。若 A4 Colab job 重啟需確認 API 呼叫上限已設定，否則帳單事件將重演 | Owner 優先：確認 GCP Billing Alert 已啟用 + API quota 已設上限，再授權 A4 重啟 Colab |
| A2/A3 | ⚠️ A1巡查 2026-04-24 09:00：**T-A2A3-001/001-B GSC 索引觀察期已達 19 天**（04-05起），遠超 7-14 天驗證窗口。Owner 仍未查 GSC，排名驗證完全停滯 | Owner 查 GSC（嚴重逾期）→ A2 更新 Task Card |
---

## Source of Truth（有效文件清單）

> Agent 只需讀以下文件。其他文件僅供參考，不作為執行依據。

| 用途 | 檔案 | 說明 |
|------|------|------|
| 🎯 最新狀態（你在這裡） | CURRENT_STATUS.md | 唯一入口，最高優先 |
| 📋 任務池 | TASK_QUEUE.md | 所有待辦任務清單 |
| 📖 角色與規則 | AGENT_RULES.md v3.9 | 10 角色定義（A0-A8 + B1）+ 協作規則 + 存檔規則 |
| 🚀 開工 SOP | AGENT_STARTUP_PROTOCOL.md | 啟動流程 + Startup Check 輸出格式 |
| 📂 任務卡 | handoff/tasks/T-xxx.md | 你認領的任務的詳細狀態 |
| 🔧 技能路由 | skills/superpowers-guide.md | 開工前查路由表（27 本技能書）|
| 🎯 角色召喚 | AGENT_RECALL_PROMPTS.md | 各角色專屬 prompt + 斷點 + 可用工具 |
| 🗣️ 品牌語氣 | skills/brand-voice-guide.md | 對外文字必讀：禁用語、平台微調、受眾語氣 |

---

## 可用 MCP 工具（2026-03-26 接通）

> Agent 可直接使用以下工具讀寫外部服務，不需要開網頁手動操作。

| 工具 | 用途 | 給哪些角色 |
|------|------|-----------|
| NotebookLM | 文章→podcast 音檔（Audio Overview）| A8 |
| Gemini Flash | 照片分類/alt text/Shorts 腳本 | A4, A8 |
| Google Vids | 腳本+圖片→影片組裝 | A8 |
| YouTube Studio | 影片上傳/排程/SEO | A8 |
| Google Sheets | 讀寫試算表（品項/報價/追蹤表）| A5, A2, A3, 全員 |
| Google Drive | 檔案存取/上傳/管理 | A4, A6, 全員 |
| Google Analytics | 流量數據/報表 | A2, A3 |
| Google Search Console | 搜尋排名/關鍵字 | A2 |
| Google Ads | 廣告數據（唯讀）| A3 |
| Meta Ads | Facebook/IG 廣告數據+管理 | A3 |

OAuth token：`~/.claude/mcp-keys/google-token.json`（drive + spreadsheets scope）

---

## 知識地圖（資料在哪裡）

> 找不到資料？查這張表。

| 類別 | 路徑 | 內容 |
|------|------|------|
| 客戶/活動資料 | data/timetree_events_2022_2026.json | 746 筆外燴事件（含客戶名、日期、活動類型）|
| 品項資料 | data/item-master-cross-reference.md | 108 品項對照表（APP/DST/MAIN/BEV）|
| 品項頻率 | data/item-frequency-top50.md | 399 筆歷史訂單品項分析 |
| 品項去重 v2 | data/quote_items_deduped.json | 3,794 唯一品項 |
| 報價系統 | projects/maplab-master-data.md | A5 報價邏輯 + Sheets 結構 |
| SEO/廣告 | projects/seo-ads-agent.md | A2/A3 核心文件 + 轉換動作快照 |
| 照片管線 | projects/maplab-pipeline.md | A4 照片分類流程 + Gemini API |
| 客服系統 | projects/ai-reply-system.md | A7 回覆系統架構 |
| 廣告監控 | projects/maplab-ads-monitor.md | A3 ads_agent.py 技術文件 |
| 報價簡報 | projects/slides-quotation-system.md | A6 Google Slides 報價 |
| 網站優化 | projects/maplab-kitchen-web-optimization.md | WordPress 技術 |
| LINE 報價助手 | projects/line-quote-assistant.md | A6/A7 系統架構、三層資料模型 |
| A0 操作手冊 | docs/a0-dispatch-operations-manual.md | A0 調度操作手冊 |
| Drive 根目錄 | MAPLAB_DATA `19RKLsBfNKuoCHVPFzT9D7tJrAdkTSmpt` | 品項圖片: MAPLAB_Items_Photos `1Z62HUIiVutGNqLJMGyTfBCZ-D5g2vnOT`；主試算表: `1fn_woqYI_RY9ggGHVidB5SMygAzwe4CL_SOPLhe91Jg` |
| 交接紀錄 | handoff/tasks/T-xxx.md | 各任務斷點 + 接續 prompt |
| 歷史狀態 | archive/CURRENT_STATUS_2026-04-11_full.md | 2026-04-11 前完整巡查記錄 |
