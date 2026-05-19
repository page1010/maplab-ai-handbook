# CURRENT_STATUS.md — 唯一最新狀態入口

> **所有 Agent 開工前第一個讀的檔案。這裡的資訊優先於所有其他文件。**
> 若其他文件與本檔衝突，以本檔為準。

最後更新：2026-05-19 A1 B1 cross-project governance prompt + pause（B1 從 InnerFlowLab 內容發文改為暫停中的跨專案治理顧問）｜完整歷史存於 `archive/CURRENT_STATUS_2026-04-11_full.md`

---

## 系統版本

- **Version**: v6.0
- **Phase**: Phase 6 — 觀測性 + 業務閉環 + 策略循環
- **Status**: Active
- **v6.0 設計文件**: `projects/v6-architecture.md`
- **Sheets Dashboard**: `1fn_woqYI_RY9ggGHVidB5SMygAzwe4CL_SOPLhe91Jg` → Task Board + Owner Actions 分頁

---

## 最新事實核對

- 2026-05-11：正式 repo = `/Users/pagemacmini/maplab-ai-handbook`；`/Users/pagemacmini/Downloads/maplab-ai-handbook-main` 為非 git 下載副本，只能作遷移/歷史參考，不得作為正式工作目錄。
- 2026-05-11：Drive API 確認 `MAPLAB_ASSETS` active folder = `1yVggYKiTkBJe4kd8CPoM3U75km0nVuNy`，parent = `MAPLAB`；舊 ID `1L0udpuXLy3vEbHmzBbaLqNVDut2FFpCe` API 回 404。
- 2026-05-11：Sheets API 確認 `MAPLAB_ASSET_LOG` = `1nlxlMdaLdGEAmOjP70BYspRWqu_eYpsiRyZaujEZkYI`，tab `工作表1`，rowCount `36923`。
- 2026-05-11：WordPress public REST 現況仍為 6 pages / 57 posts；A2/A3 local workbench planned slugs 不可直接視為 live URLs。
- 2026-05-19：A6 Case Store v0 接線 — LINE inbound 仍以 Sheet `CONVERSATION_LOG` 為原始證據；新增 `bot_a6/case_store.py` 只讀 Sheet、寫本機 SQLite 案件索引，A6 Telegram 新增 `/linecases`、`/case`、`/casequote`，路徑圖補回 `projects/line-quote-assistant.md`。
- 2026-05-19：B1 已由 InnerFlowLab 內容發文角色改為「暫停中的跨專案治理顧問」；Chrome Extension B1 module 將指向 `projects/b1-cross-project-governance-advisor.md`，review bundle 在 `workbook/reviews/JOB-B1-CROSS-PROJECT-20260519/`。原 Substack / innerflowlab.com / 多平台發文自動化暫停，不得未經 Owner/A1 恢復就執行。
- 2026-05-11：GitHub sync audit 啟動 — 以 `origin/main` 為備份基準，將 durable docs/scripts/task cards/review index 補齊入庫；`.env`、logs、runtime history、raw A6 review bundles 暫不盲目 commit，先建立 sanitized/index 流程。

---

## 當前進行中任務

| Task ID | 任務 | 負責 Agent | 狀態 | Task Card |
|---------|------|-----------|------|----------|
| T-A1-V6-P2 | T-A1-V6-P2 | A1 | 🔄 進行中（4 分頁架構 + DropdownHelper 驗證完成、REVISION_LOG 精簡完成。下一步：建虛擬測試案例 →） | handoff/tasks/T-A1-V6-P2.md |
| T-A1-V6-P3 | T-A1-V6-P3 | A1 | 🔲 待開始（尚未開始。等 T-A1-V6-P2 完成後啟動。） | handoff/tasks/T-A1-V6-P3.md |
| T-A1-V7 | 系統進化 — 單一真相源 + 自動同步 + 瘦身 + 自動技能生成 + 自動壓縮 | A1 | 🔄 進行中（Phase 1-4 全部完成 + 6 個修復項全部完成。剩 Phase 5（自動壓縮 ReMe）為加分項。） | handoff/tasks/T-A1-V7.md |
| T-A2-002-foodsafety-seo-cleanup | T-A2-002 — 食安 + 法規 SEO 字眼清理 | A2 | ⏸️ 阻塞（Repo 端已清理完成；WordPress 端需 Owner 手動刪除/修改 5 篇文章的食安字眼） | handoff/tasks/T-A2-002-foodsafety-seo-cleanup.md |
| T-A2-003-weekly-wp-audit | T-A2-003: 每週全站 WP 內容稽核排程 | A2 | 🔲 待開始（腳本已建好（wp-audit.sh / wp-audit-cron.sh）。待 Owner 用 /schedule 建立） | handoff/tasks/T-A2-003-weekly-wp-audit.md |
| T-A2-004 | 首頁結構優化 — 配合品牌色票微調 + 轉換路徑整理 | A2 | 🔲 待開始（任務卡建立。A0 已完成對標分析和色票微調。） | handoff/tasks/T-A2-004.md |
| T-A2-005-local-seo-factory | MAPLAB SEO Factory 地端閉環（Pillar First） | A2（A1治理支援） | 🔄 進行中（7-stage pipeline + schema + weekly batch 建置完成；dry-run 3/3 pass。下一步：WP `--publish` 實測 + 真實 signals 導入） | handoff/tasks/T-A2-005-local-seo-factory.md |
| T-A2A3-001-B | SEO 場景頁面 + 內連結（從 T-A2A3-001 分拆） | A2/A3 | ⏸️ 阻塞（子任務 3+4 完成（3 個場景頁 + 56 篇內連結）；子任務 5 等 Google 重新索引（7-14 天）） | handoff/tasks/T-A2A3-001-B.md |
| T-A2A3-001 | SEO 關鍵字頁面補足 | A2/A3 | ⏸️ 阻塞（子任務 1-4 完成；子任務 5 等 Google 重新索引驗證排名變化） | handoff/tasks/T-A2A3-001.md |
| T-A3-002 | Meta 廣告「慶生周歲派對」受眾確認 + 優化 | A3 | ⏸️ 阻塞中（受眾輪廓分析完成（693筆 Orders）。待執行：嘉義加入廣告地區、興趣條件精簡、策略一冷受眾上線。） | handoff/tasks/T-A3-002.md |
| T-A4-001 | Phase 4 Gemini 照片分類（2022-2026） | A4 | 🔴 CRITICAL（S11(2024) 🔴 14ed423 04-18 Colab重啟→**~312h/13天**無completion commit（Colab確認崩潰；GCP帳單13天未處理🔴）；S12(2025) ✅ DONE 7,645/7,642；等Owner處理S11） | handoff/tasks/T-A4-001.md |
| T-A4-002 | pagewu1010 帳號 Takeout 解壓 + Gemini Flash 照片資產整合 | A4 | 🔄 進行中（ASSET_LOG分佈統計確認(36,922張)：外燴55%/旅遊20%/日常20%/error5%；Phase 1.5規劃完成；GCP Gemini API已停用；預算警報已建立；照片分類腳本已建待執行） | handoff/tasks/T-A4-002.md |
| T-A5-002 | QUOTE_DRAFT 報價單欄位增強 | A5 | 🔴 CRITICAL（~528h無commit，D22）| handoff/tasks/T-A5-002.md |
| T-A5-004 | createSlides.gs — Slide 報價簡報自動生成 | A5 | 🔴 CRITICAL（~528h無commit，D22）| handoff/tasks/T-A5-004.md |
| T-A5-005 | 報價狀態追蹤同步 + Dashboard | A5 | 🔴 CRITICAL（~528h無commit，D22）| handoff/tasks/T-A5-005.md |
| T-A5-006 | T-A5-006 | A5 | 🔲 待開始（尚未開始。等 T-A5-005 完成後啟動。） | handoff/tasks/T-A5-006.md |
| T-A6-001 | A6 LINE 業務報價助手系統 | A6 | 🔄 進行中（Case Store v0 已接現有 CONVERSATION_LOG；A6 Telegram 新增 /linecases /case /casequote。下一步：Owner/Mina 手機實測三個指令） | handoff/tasks/T-A6-001.md |
| T-A6-002 | LINE 對話訓練資料收集計畫 | A6 | 💤 暫停（原計畫拆 Sheet 做訓練資料，04-07 重新規劃方向。等 Owner 決定是否需要 LINE 訓練資料及取得方式。） | handoff/tasks/T-A6-002.md |
| T-A7-001 | FAQ 回覆模板庫 + 補問流程 + 客戶分類標籤 | A7 | 💤 暫停（Phase 2 v2.0 完成，等 Owner 確認政策 + A5 欄位補齊）（Q1-Q10 重構完成（真實 CSV 驅動），下一步是 Q7/Q10 政策確認 + Phase 3 上線測試） | handoff/tasks/T-A7-001.md |
| T-A7-002 | A7 部門 80/20 優先任務清單 | A7 | ⏸️ 阻塞中（任務 6（Q1-Q10 實裝）+ 任務 10（技能書 v2.0）已完成。Phase 3A 剩任務 4（地區判斷）、7（流） | handoff/tasks/T-A7-002.md |
| T-B1-001 | B1 Cross-Project Governance Advisor Prompt + Project Pause | B1/A1 | 💤 暫停（prompt ready；InnerFlowLab 內容發文專案暫停。跨專案治理 review 需 Owner/A1 明確召喚。） | handoff/tasks/T-B1-001.md |
| T-GBP-001 | T-GBP-001 | Owner | 🔲 待開始（尚未開始。等 Owner 準備新圖片。） | handoff/tasks/T-GBP-001.md |
---

## Blockers（只列未解決的）

| 對象 | 問題 | 行動 |
|------|------|------|
| A1 | T-A1-V6-P2: 等 A6 實際報價測試 | 見 Task Card |
| A1 | T-A1-V6-P3: 前置 T-A1-V6-P2 需先完成 | 見 Task Card |
| A2 | T-A2-002-foodsafety-seo-cleanup: 等 Owner 操作 WordPress 後台 | 見 Task Card |
| A2 | T-A2-003-weekly-wp-audit: 等 Owner 建立排程 | 見 Task Card |
| A2 | T-A2-005-local-seo-factory: 等 Owner 提供 WordPress Application Password（先以 dry-run 運行） | 見 Task Card |
| A2/A3 | T-A2A3-001-B: 等 Google 重新索引，預計 04-11 後可驗證 | 見 Task Card |
| A2/A3 | T-A2A3-001: 等 Google 重新索引，預計 04-11 後可驗證 | 見 Task Card |
| A3 | T-A3-002: 執行需登入 Meta Ads Manager（等廣告週期 + Owner 操作） | 見 Task Card |
| A4 | T-A4-002: 前置 T-A4-001 S11 尚未完成，Phase 1 Colab 解壓不得在 S11 completion 前啟動 | Owner確認S11最新Colab狀態→補completion commit |
| A4 | ⚠️ A1巡查 2026-05-01午後：T-A4-001 S11 ~320h/~13.3天無completion commit（Colab崩潰）；GCP帳單$3K/月已14天未處理🔴 | Owner立即：①確認S11 Colab狀態→補completion commit；②確認GCP帳單上限 |
| A5 | ⚠️ A1巡查 2026-05-01午後：T-A5-002/004/005 CRITICAL D22/~536h無commit（last: cfeebd1 2026-04-09）。連續10+巡查Owner無決策回應 | Owner 決策：是否重啟A5 |
| 全系統 | ⚠️ A1巡查 2026-05-01午後：全系統靜止168h+（7天，上次non-patrol commit B1 2026-04-24）。8h零新commit；A2/A3/A6/A7/A8/B1均無新活動 | Owner確認各Agent狀態；B1需建立正式Task Card |
| A4/A5/全系統 | ⚠️ A1巡查 2026-05-09 14:00午後：8h零新commit（全系統靜止~125h/~5.2天，last non-patrol 6f98c5d/5ae9c79 05-04）；A4 S11 ~509h/~21.2天Colab崩潰🔴；A5 D30/~725h無commit🔴；GCP帳單~22.2天未處理🔴；A2/A6 ~125h無commit（T-A2-005/T-A6-001 🔄>48h警告持續）；A3/A7/A8/B1仍無活動；T-B1-001 Task Card仍未建立（~15天）；LINE webhook仍等Owner確認（Channel 1654658337）；所有前次警告持續未解 | Owner緊急決策：①確認A4 S11 Colab狀態；②確認GCP帳單上限；③決定是否重啟A5；④確認LINE webhook URL；⑤確認B1 Task Card是否建立 |
| A4/A5/全系統 | ⚠️ A1巡查 2026-05-09 09:00每日：0非巡查commit（全系統靜止~120h/~5天，last non-patrol 6f98c5d/5ae9c79 05-04）；A4 S11 ~504h/~21天Colab崩潰🔴；A5 D30/~720h無commit🔴；GCP帳單~22天未處理🔴；A2 ~120h無commit（T-A2-005 🔄>48h持續）；A6 ~120h無commit（T-A6-001 🔄>48h持續）；A3/A7/A8/B1仍無活動；T-B1-001 Task Card仍未建立（~15天）；LINE webhook仍等Owner確認（Channel 1654658337）；所有前次警告持續未解 | Owner緊急決策：①確認A4 S11 Colab狀態；②確認GCP帳單上限；③決定是否重啟A5；④確認LINE webhook URL；⑤確認B1 Task Card是否建立 |
| A4/A5/全系統 | ⚠️ A1巡查 2026-05-08 21:00晚間：8h零新commit；全系統靜止~108h（last non-patrol 5ae9c79 05-04）；A4 S11 ~492h/~20.5天Colab崩潰🔴；A5 D29/~708h無commit🔴；GCP帳單~21.0天未處理🔴；A2/A6 ~108h無commit（T-A2-005/T-A6-001 🔄>48h警告持續）；A3/A7/A8/B1仍無活動；T-B1-001 Task Card仍未建立（~14天）；LINE webhook仍等Owner確認（Channel 1654658337）；所有前次警告持續未解 | Owner緊急決策：①確認A4 S11 Colab狀態；②確認GCP帳單上限；③決定是否重啟A5；④確認LINE webhook URL；⑤確認B1 Task Card是否建立 |
| A4/A5/全系統 | ⚠️ A1巡查 2026-05-08 14:00午後：8h零新commit（全系統靜止~101h，last non-patrol 5ae9c79 05-04）；A4 S11 ~485h/~20.2天Colab崩潰🔴；A5 D29/~701h無commit🔴；GCP帳單~20.7天未處理🔴；A2/A6 ~101h無commit（T-A2-005/T-A6-001 🔄>48h警告持續）；A3/A7/A8/B1仍無活動；T-B1-001 Task Card仍未建立（~14天）；LINE webhook仍等Owner確認（Channel 1654658337）；所有前次警告持續未解 | Owner緊急決策：①確認A4 S11 Colab狀態；②確認GCP帳單上限；③決定是否重啟A5；④確認LINE webhook URL；⑤確認B1 Task Card是否建立 |
| A4/A5/全系統 | ⚠️ A1巡查 2026-05-08 09:00每日：0非巡查commit（全系統靜止~96h，last non-patrol 5ae9c79 05-04）；A4 S11 ~480h/~20天Colab崩潰🔴；A5 D29/~696h無commit🔴；GCP帳單~20.5天未處理🔴；A2 ~96h無commit（T-A2-005 🔄>48h持續）；A6 ~96h無commit（T-A6-001 🔄>48h持續）；A3/A7/A8/B1仍無活動；T-B1-001 Task Card仍未建立（~14天）；LINE webhook仍等Owner確認（Channel 1654658337）；所有前次警告持續未解 | Owner緊急決策：①確認A4 S11 Colab狀態；②確認GCP帳單上限；③決定是否重啟A5；④確認LINE webhook URL；⑤確認B1 Task Card是否建立 |
| A4/A5/全系統 | ⚠️ A1巡查 2026-05-07 21:00晚間：8h零新commit；全系統靜止72h+（繼續自05-04）；A4 S11 ~472h/~19.7天Colab崩潰🔴；A5 D28/~672h無commit🔴；GCP帳單~20天未處理🔴；A2/A6上次活動05-04（72h無新commit，>48h🔄警告）；A3/A7/A8/B1仍無活動；T-B1-001 Task Card仍未建立（>13天）；LINE webhook仍等Owner確認（Channel 1654658337） | Owner 緊急決策：①確認A4 S11 Colab狀態；②確認GCP帳單上限；③決定是否重啟A5；④確認LINE webhook URL；⑤確認B1 Task Card是否建立 |
| A4/A5/A6 | ⚠️ A1巡查 2026-05-04 21:00晚間：A2 🟢 6f98c5d（keyword-matrix strategy rules 注入 SEO Factory）；A6 🟢 5ae9c79（ollama chat/seo modes + menu）打破A6長期靜止；A4 S11 ~400h/~16.7天Colab崩潰🔴；A5 D25/~616h無commit🔴；GCP帳單~17.3天未處理🔴；A3/A7/A8/B1無新活動；LINE webhook仍等Owner確認（Channel 1654658337）；T-A6-001狀態從⏸️更新為🔄 | Owner 緊急決策：①確認A4 S11 Colab狀態；②確認GCP帳單上限；③決定是否重啟A5；④確認LINE webhook URL |
| A4/A5 | ⚠️ A1巡查 2026-05-04 17:00午後：A2 🟢 2新commit（ba4fac6+59f06ce T-A2-005 SEO Factory + ollama live test）打破全系統靜止（~240h）；A4 S11 ~392h/~16.3天Colab崩潰🔴；A5 D25/~608h無commit🔴；GCP帳單~17天未處理🔴；A3/A6/A7/A8/B1仍無活動；GSC索引觀察29天+逾期 | Owner 緊急決策：①確認A4 S11 Colab狀態；②確認GCP帳單上限；③決定是否重啟A5 |
| A4/A5/全系統 | ⚠️ A1巡查 2026-05-02 14:00午後：8h零新commit（全系統192h+/8天靜止持續）；A4 S11 ~344h/~14.3天Colab崩潰🔴；A5 D23/~560h無commit🔴；GCP帳單15天未處理🔴 — 所有前次警告仍未解除 | Owner 緊急決策（同前次 Blocker 行動項） |
| A4/A5/全系統 | ⚠️ A1巡查 2026-05-01 22:00晚間：8h零新commit（全系統176h+/7.3天靜止持續）；A4 S11 ~328h/~13.7天Colab崩潰🔴；A5 D22/~544h無commit🔴；GCP帳單14天未處理🔴 — 所有午後警告仍未解除 | Owner 緊急決策（同午後 Blocker 行動項） |
| A2/A3 | ℹ️ A1巡查 2026-04-30：T-A2A3-001/001-B Google重新索引等待期已逾26天（預計7-14天，早已超過），可進入排名驗證階段 | Owner登入GSC確認索引+排名變化 |
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
|------|------|----------|
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
| B1 跨專案治理顧問 | projects/b1-cross-project-governance-advisor.md | B1 暫停狀態、跨專案治理 prompt、Investment OS 對照建議 |
| A0 操作手冊 | docs/a0-dispatch-operations-manual.md | A0 調度操作手冊 |
| Drive 根目錄 | MAPLAB_DATA `19RKLsBfNKuoCHVPFzT9D7tJrAdkTSmpt` | 品項圖片: MAPLAB_Items_Photos `1Z62HUIiVutGNqLJMGyTfBCZ-D5g2vnOT`；主試算表: `1fn_woqYI_RY9ggGHVidB5SMygAzwe4CL_SOPLhe91Jg` |
| 交接紀錄 | handoff/tasks/T-xxx.md | 各任務斷點 + 接續 prompt |
| 歷史狀態 | archive/CURRENT_STATUS_2026-04-11_full.md | 2026-04-11 前完整巡查記錄 |
