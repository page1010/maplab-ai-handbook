# CURRENT_STATUS.md — 唯一最新狀態入口

> **所有 Agent 開工前第一個讀的檔案。這裡的資訊優先於所有其他文件。**
> 若其他文件與本檔衝突，以本檔為準。

最後更新：2026-04-14 14:00（A1 午後巡查）｜完整歷史存於 `archive/CURRENT_STATUS_2026-04-11_full.md`

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
| T-A5-002 | QUOTE_DRAFT 報價單欄位增強 | A5 | 🔴 CRITICAL（~119h無commit，等Owner確認剩餘增強項目） | handoff/tasks/T-A5-002.md |
| T-A5-003 | 熱客招待品項定義 | A5 | 🔲 待開始 | — |
| T-A5-004 | generateProposal_v2.gs Slide 簡報 | A5/A6 | 🔄 進行中（GAS v4已部署，e2e round5 passed；待：結尾頁/無圖垂直置中） | handoff/tasks/T-A5-004.md |
| T-A5-005 | onEdit追蹤同步+Dashboard | A5 | 🔲 待啟動 | handoff/tasks/T-A5-005.md |
| T-A4-001 | Phase 4 Gemini 照片分類 | A4 | 🔴 CRITICAL（最後commit 04-10 08:31 5787f3e，逾~101h；S12執行狀態未知，需Owner確認Colab是否斷線） | projects/maplab-pipeline.md + handoff/tasks/T-A4-001.md |
| T-A2A3-001 | SEO 關鍵字頁面補足 | A2 | 🔄 子任務1-4完成，子任務5等7-14天 | handoff/tasks/T-A2A3-001.md + T-A2A3-001-B.md |
| T-A3-001 | GTM LINE 按鈕追蹤修復（方案 B） | A3 | 🔴 CRITICAL（~383h無commit，GTM方案B規格已記錄，待技術實作） | — |
| T-A3-002 | Meta 廣告「慶生周歲派對」受眾確認 | A3 | 🔴 CRITICAL（~383h無commit，廣告成效報告v1.0已產出） | handoff/tasks/T-A3-002.md |
| T-A6-001 | Telegram 報價助手系統 | A6 | 🔄 進行中（GAS doPost Web App v12已上線，訓練架構Steps 1-4完成，e2e round5 passed） | projects/line-quote-assistant.md |
| T-A6-002 | LINE 對話訓練資料收集 | A6 | 🔲 暫停（LINE webhook無業務回覆，待Owner決定新方向） | handoff/tasks/T-A6-002.md |
| T-A7-001 | FAQ 回覆模板庫 + 補問流程 | A7 | 🔴 CRITICAL（~335h無commit，skills v2.0/reply-templates v1.0已產出） | handoff/tasks/T-A7-001.md |
| T-A7-002 | 80/20 優先任務清單 + 執行路線圖 | A7 | 🔴 CRITICAL（~335h無commit，任務6+10完成） | — |
| T-A1-V6-P2 | v6.0 Phase 2 業務閉環 MVP | A1 | 🔄 進行中 | handoff/tasks/T-A1-V6-P2.md |
| T-A1-V6-P3 | v6.0 Phase 3 自動化+策略循環 | A1 | 🔲 待開始（前置: T-A1-V6-P2） | handoff/tasks/T-A1-V6-P3.md |
| T-A4-002 | pagewu1010 帳號 187GB Takeout 處理 | A4 | 🔲 待開始（前置: T-A4-001 完成） | handoff/tasks/T-A4-002.md |
| T-A5-006 | OrderLines 2025 手動重建 | A5 | 🔲 待開始（前置: T-A5-005 完成） | handoff/tasks/T-A5-006.md |
| T-GBP-001 | Google 商家檔案「週歲派對」產品圖片更換 | Owner | 🔲 待開始 | handoff/tasks/T-GBP-001.md |

---

## Blockers（只列未解決的）

| 對象 | 問題 | 行動 |
|------|------|------|
| A3 | T-A3-001 + T-A3-002 連續14天無commit（~342h+） | **Owner 需執行：標記 ⏸️ 暫停**，等GTM權限/廣告觀察期就緒再重啟 |
| A7 | T-A7-001 + T-A7-002 連續12天無commit（~294h+） | **Owner 需決定：暫停 或 確認外部阻塞原因** |
| A5 | T-A5-002 已逾48h閾值（~78h無commit） | Owner 確認：(a)有未commit進度，或(b)等待Owner回饋確認增強項目（記錄即可） |
| A4 | T-A4-001 ~60h無commit（最後04-10 08:31） | **Owner 需確認：S12 Colab 是否仍執行中，或已斷線需重啟** |
| A5 | A30/A31 條款位置：應在 C37+ 框線內，但目前寫 A 欄框線外，客人看不到 | 下次 A5 session 修正 |
| Owner | Items DST 成本補填（21筆 E 欄） | 手動填入 MAPLAB_外燴系統_v0.1 Items 表 |
| Owner | Token 輪換：A6 bot token 待確認；Claude API token 待確認 | 舊token已從git history清除，需撤銷作廢 |
| Owner | LINE Webhook URL 是否已填入 LINE Developers Console？ | 確認 GAS doPost URL 已設定 |

> ⚠️ A1巡查 2026-04-12 08:42：T-A4-001 48h閾值已過（04-12 08:31），距最後commit(04-10 5787f3e)已逾48h，Colab S12執行狀態未確認，自動升級🔴CRITICAL。A3 ~330h無commit，A7 ~282h無commit，A5-002 ~66h無commit，均維持CRITICAL。
> ⚠️ A1巡查 2026-04-12 21:00（晚間）：過去8h零新commit。所有CRITICAL任務時鐘持續累計：A4 ~60h（Colab狀態仍未確認）、A5-002 ~78h、A7 ~294h、A3 ~342h。今日唯一活動為docs commit（user-scenarios.md，10:02 +0800），無業務Agent進展。四項CRITICAL待Owner行動，建議優先處理A4 Colab確認及A3/A7暫停決策。
> ⚠️ A1巡查 2026-04-14 14:00（午後）：距上次巡查（04-12 21:00）已逾~41h，全系統零新commit。所有CRITICAL時鐘繼續累計：A4 ~101h（Colab S12狀態持續未確認，已超4天）、A5-002 ~119h（已超5天）、A7 ~335h（約14天）、A3 ~383h（約16天）。全系統連續~41h無任何業務活動，屬異常靜止期。【強烈建議Owner】：(1) 立即確認 A4 Colab S12 是否仍在執行，或已斷線需重啟；(2) 決策 A3/A7 暫停或重啟；(3) 確認 A5-002 Owner 回饋是否已提供。
> ⚠️ A1巡查 2026-04-14 14:00（git構造異常）：偵測到兩條分歧的 git 歷史。origin/main 停在 04-10 `5787f3e`（50 commits），本機 detached HEAD 有獨立的 51 commits（04-10至04-14的所有巡查記錄）。兩條歷史無共同祖先，無法 fast-forward push。本次巡查 commit 已 push 到 `patrol/a1-2026-04-14` branch。【Owner 需決策】：確認 detached HEAD 的歷史是否為正確主線 → 若是，執行 `git push --force-with-lease origin HEAD:main` 將 detached HEAD 設為新 main。

---

## Source of Truth（有效文件清單）

> Agent 只需讀以下文件。其他文件僅供參考，不作為執行依據。

| 用途 | 檔案 | 說明 |
|------|------|------|
| 🎯 最新狀態（你在這裡） | CURRENT_STATUS.md | 唯一入口，最高優先 |
| 📋 任務池 | TASK_QUEUE.md | 所有待辦任務清單 |
| 📖 角色與規則 | AGENT_RULES.md v3.1 | 9 角色定義（含 A0）+ 協作規則 + 存檔規則 |
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
