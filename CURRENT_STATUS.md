# CURRENT_STATUS.md — 唯一最新狀態入口

> **所有 Agent 開工前第一個讀的檔案。這裡的資訊優先於所有其他文件。**
> 若其他文件與本檔衝突，以本檔為準。

最後更新：2026-04-25（A1巡查 — B1首次活躍4 commits(workflow v1.0+skill book+session log)；A4 S11 ~170h/7天；A5 D16+~397h）｜完整歷史存於 `archive/CURRENT_STATUS_2026-04-11_full.md`

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
| T-A1-V7 | 系統進化 — 單一真相源 + 自動同步 + 瘦身 + 自動技能生成 + 自動壓縮 | A1 | 🔄 進行中（Phase 1-4 全部完成 + 6 個修復項全部完成。剩 Phase 5（自動壓縮 ReMe）為加分項。） | handoff/tasks/T-A1-V7.md |
| T-A2-002-foodsafety-seo-cleanup | T-A2-002 — 食安 + 法規 SEO 字眼清理 | A2 | ⏸️ 阻塞（Repo 端已清理完成；WordPress 端需 Owner 手動刪除/修改 5 篇文章的食安字眼） | handoff/tasks/T-A2-002-foodsafety-seo-cleanup.md |
| T-A2-003-weekly-wp-audit | T-A2-003: 每週全站 WP 內容稽核排程 | A2 | 🔲 待開始（腳本已建好（wp-audit.sh / wp-audit-cron.sh）。待 Owner 用 /schedule 建立） | handoff/tasks/T-A2-003-weekly-wp-audit.md |
| T-A2-004 | 首頁結構優化 — 配合品牌色票微調 + 轉換路徑整理 | A2 | 🔲 待開始（任務卡建立。A0 已完成對標分析和色票微調。） | handoff/tasks/T-A2-004.md |
| T-A2A3-001-B | SEO 場景頁面 + 內連結（從 T-A2A3-001 分拆） | A2/A3 | ⏸️ 阻塞（子任務 3+4 完成（3 個場景頁 + 56 篇內連結）；子任務 5 等 Google 重新索引（7-14 天）） | handoff/tasks/T-A2A3-001-B.md |
| T-A2A3-001 | SEO 關鍵字頁面補足 | A2/A3 | ⏸️ 阻塞（子任務 1-4 完成；子任務 5 等 Google 重新索引驗證排名變化） | handoff/tasks/T-A2A3-001.md |
| T-A3-002 | Meta 廣告「慶生周歲派對」受眾確認 + 優化 | A3 | ⏸️ 阻塞中（受眾輪廓分析完成（693筆 Orders）。待執行：嘉義加入廣告地區、興趣條件精簡、策略一冷受眾上線。） | handoff/tasks/T-A3-002.md |
| T-A4-001 | Phase 4 Gemini 照片分類（2022-2026） | A4 | 🔴 CRITICAL（S11(2024) 🔴 14ed423 04-18 Colab重啟→**~170h/7天**無completion commit（Colab確認崩潰）；S12(2025) ✅ DONE 7,645/7,642；等Owner處理S11） | handoff/tasks/T-A4-001.md |
| T-A4-002 | pagewu1010 帳號 Takeout 解壓 + Gemini Flash 照片資產整合 | A4 | 🔄 進行中（ASSET_LOG分佈統計確認(36,922張)：外燴55%/旅遊20%/日常20%/error5%；Phase 1.5規劃完成；GCP Gemini API已停用；預算警報已建立；照片分類腳本已建待執行） | handoff/tasks/T-A4-002.md |
| T-A5-002 | QUOTE_DRAFT 報價單欄位增強 | A5 | 🔴 CRITICAL（~397h無commit，D16+） | handoff/tasks/T-A5-002.md |
| T-A5-004 | createSlides.gs — Slide 報價簡報自動生成 | A5 | 🔴 CRITICAL（~397h無commit，D16+） | handoff/tasks/T-A5-004.md |
| T-A5-005 | 報價狀態追蹤同步 + Dashboard | A5 | 🔴 CRITICAL（~397h無commit，D16+） | handoff/tasks/T-A5-005.md |
| T-A5-006 | T-A5-006 | A5 | 🔲 待開始（尚未開始。等 T-A5-005 完成後啟動。） | handoff/tasks/T-A5-006.md |
| T-A6-001 | A6 LINE 業務報價助手系統 | A6 | ⏸️ 阻塞中（Sheet 三分頁架構完成、LINE Bot Webhook 技能書完成、GAS doPost 已部署。差最後一步：LI） | handoff/tasks/T-A6-001.md |
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
| A2/A3 | T-A2A3-001-B: 等 Google 重新索引，預計 04-11 後可驗證 | 見 Task Card |
| A2/A3 | T-A2A3-001: 等 Google 重新索引，預計 04-11 後可驗證 | 見 Task Card |
| A3 | T-A3-002: 執行需登入 Meta Ads Manager（等廣告週期 + Owner 操作） | 見 Task Card |
| A4 | T-A4-002: 前置 T-A4-001 S11 尚未完成，Phase 1 Colab 解壓不得在 S11 completion 前啟動 | Owner確認S11最新Colab狀態→補completion commit |
| A4 | ⚠️ A1巡查 2026-04-25：T-A4-001 S11 ~170h/7天無completion commit（Colab確認崩潰）；GCP帳單$3K/月已7天未處理 | Owner立即：①確認S11 Colab狀態→補completion commit；②確認GCP帳單上限 |
| A5 | ⚠️ A1巡查 2026-04-25：T-A5-002/004/005 CRITICAL D16+ ~397h無commit（last: cfeebd1 2026-04-09）。連續8+巡查Owner無決策回應 | Owner 決策：是否重啟A5 |
| - | ℹ️ A1巡查 2026-04-25：B1首次活躍（4 commits: sessions/B1/2026-04-24-session-01.md + workflows/B1-content-workflow-v1.md + skills/substack-api.md）— RECALL_PROMPTS已更新B1狀態 | B1需建立正式Task Card |
| 全系統 | ℹ️ A1巡查 2026-04-19 14:00：Owner 今日提交 fix(framework) v1.2+v1.3 共 3 commits（e8a2aa3/6801266/4958a89）— 規則衝突優先級 + 回應校正標準。各 Agent 下次 session 開始時注意 AGENT_RULES.md 是否有更新。 | 各 Agent 留意 |
| A5 | T-A5-002: 等 Owner 確認（品項名稱改法、重複品項、I 欄用途） | 見 Task Card |
| A5 | T-A5-006: 前置 T-A5-005 需先完成 | 見 Task Card |
| A6 | T-A6-001: 需 Owner 在 LINE Developers Console 填入 Webhook URL（Channel 1654658337） | 見 Task Card |
| A6 | T-A6-002: 等 Owner 決定方向 | 見 Task Card |
| A7 | T-A7-001: Q7 試吃政策需 Owner 決定、Q10 取消/改期政策需 Owner 決定、A5 外送費級距未建立 | 見 Task Card |
| A7 | T-A7-002: 任務 1/2/3 需 LINE bot 後台權限；任務 9 需 Owner 政策決策（Q7 試吃 + Q10 取消改期）；任務 5/8 需 TimeTree 權限 | 見 Task Card |
| Owner | T-GBP-001: 等 Owner 準備新圖片 | 見 Task Card |
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
