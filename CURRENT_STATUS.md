# CURRENT_STATUS.md — 唯一最新狀態入口

> **所有 Agent 開工前第一個讀的檔案。這裡的資訊優先於所有其他文件。**
> 若其他文件與本檔衝突，以本檔為準。

最後更新：2026-04-02 深夜（巡檢版）｜ 更新者：A0 巡檢角色 — 系統巡檢完成：T-A5-001 card 補建 + 2 新 Skill（system-audit + session-lifecycle）+ A0 prompt 規則追加 + 舊檔歸檔。A1 晚間巡查同日：A3 🔴 CRITICAL ~110h+，A4 S11 ⚠️ WATCH，A7 🔴 CRITICAL ~72h+

---

## 系統版本

- **Version**: v6.0
- **Phase**: Phase 6 — 觀測性 + 業務閉環 + 策略循環
- **Status**: Active
- **v6.0 設計文件**: `projects/v6-architecture.md`（完整設計 + 三階段計畫 + Dashboard 召喚方式 + Sheets 速查）
- **v6.0 Session Handoff**: `handoff/sessions/2026-03-31-v6-phase1-phase2.md`
- **Sheets Dashboard**: `1fn_woqYI_RY9ggGHVidB5SMygAzwe4CL_SOPLhe91Jg` → Task Board + Owner Actions 分頁
- **Dashboard 召喚**：A0 Cowork 說「看板」→ Artifacts 渲染 ／ 直接開 Sheets ／ Telegram `/status`

## 當前進行中任務

| Task ID | 任務 | 負責 Agent | 狀態 | Task Card |
|---------|------|-----------|------|-----------| 
| T-A1-002 | Phase 4.1 系統治理升級 | A1 | ✅ 完成 | handoff/tasks/T-A1-002.md |
| T-A5-001 | Items 去重 + 全品項重新編碼 | A5 | ✅ 完成（APP050/DST041/MAIN009/BEV008=108，已排序+連號） | handoff/tasks/T-A5-001.md |
| T-A5-002 | QUOTE_DRAFT 報價單欄位增強 | A5 | 🔄 進行中（服務費可選✅/長桌費$350✅/車馬費下拉✅/DropdownHelper分類驗證✅，dbcf9d4；待確認剩餘增強項目）| handoff/tasks/T-A5-002.md |
| T-A5-003 | 熱客招待品項定義 | A5 | 🔲 待開始 | — |
| T-A4-001 | Phase 4 Gemini 照片分類 | A4 | 🔄 S5 ✅ DONE(8,559張), S6(2023) ✅ DONE（進度待確認），S11(2024) 🔄 執行中(2600/12213, de2cf2e 20:54), S5.5 GPS ✅ 決策確認no_gps(Takeout JSON未存Drive), Task Card建立(35acbbf) | projects/maplab-pipeline.md + handoff/tasks/T-A4-001.md |
| T-A2-001 | 文章精選圖片補齊（57篇→每篇獨立配圖） | A2 | ✅ 完成（57/57 獨立配圖，0 重複） | handoff/tasks/T-A2-001.md |
| T-A2A3-001 | SEO 關鍵字頁面補足 | A2 | ✅ 子任務1-4完成（子任務5等7-14天）| handoff/tasks/T-A2A3-001.md + T-A2A3-001-B.md |
| T-A3-001 | GTM LINE 按鈕追蹤修復（方案 B 已確認） | A3 | 🔄 進行中（GTM方案B規格已記錄 2aca2ae，待技術實作+測試）| — |
| T-A3-002 | Meta 廣告「慶生周歲派對」受眾確認 + 優化 | A3 | 🔄 確認中（已上線，受眾已記錄；廣告成效報告 v1.0 + 嘉義地區建議已產出 69b50ec） | handoff/tasks/T-A3-002.md |
| T-A6-001 | LINE 業務報價助手系統 | A6 | 🔄 進行中（v1.1 架構修正：三層資料/CONVERSATION_LOG/Sheet 3個新分頁，d9fba1a+3a2df7b） | projects/line-quote-assistant.md |
| T-A7-001 | FAQ 回覆模板庫 + 補問流程 + 客戶分類標籤 | A7 | 🔄 Phase 2 進展中（skills v2.0 8種對話模式 68df5d7 + reply-templates v1.0 d165d7d）| handoff/tasks/T-A7-001.md |
| T-A7-002 | 80/20 優先任務清單 + 執行路線圖 | A7 | 🔄 任務6+10完成（cf9f166），部分執行中 | — |
| T-A0-001 | Telegram bot 指令模式上線 | A1 | ✅ 完成（bot.py 為 A1 的 Telegram 前端，非 A0）| — |
| T-A0-002 | Notion 舊資料清理（保留架構，引導到 GitHub）| A0/A1 | ✅ 完成（3 個主要頁面加了 GitHub 引導警告） | — |

## Blockers（阻塞事項）

- ~~A5：甜點去重需使用者手動完成後才能重新編碼~~ ✅ resolved — T-A5-001 完成（108品項已排序+連號）
- A5：使用者需填 Items.D 欄 default_price
- ~~A4：Gemini API key leaked (b822f90) → 已更換新 key（記錄於 Notion）~~ ✅ resolved — API key 已更新。S6 Colab 仍待重啟（18.2%）
- A3：「慶生周歲派對」已上線（現有貼文），需確認受眾設定；GTM 方案 B 可認領
- ~~A2：T-A2-001 Google Drive 2025相簿僅約20張可用照片~~ ✅ resolved — 跨相簿找圖完成（2024/2023/2019/素材開幕），57篇全部獨立配圖

~~⚠️ A1巡查 2026-03-27 00:00：A7 狀態不一致~~ ✅ 已修復 — b53a1cc (15:20) A7 補交 SECTION 8 客戶對話流程圖 + 更新任務狀態，T-A7-001 已標記 ✅ Phase 1 完成。
⚠️ A1巡查 2026-03-27 15:45：~~A4 T-A4-001 持續無新 commit~~ ✅ 2026-03-28 A4 已恢復 commit。S5 DONE，S6 18.2%，S5.5 GPS 計畫中。
⚠️ A1巡查 2026-03-27 16:06：午後巡查確認 — A4 T-A4-001 仍無新 commit，距 e166169 現逾 31.5h（48h 閾值剩 ~16.5h）。A0/A2/A5/A7 本日均活躍無異常。A2 子任務2 Phase2 SEO Title 數字優化 36篇已完成（687316d）；A7 SECTION 8 已追加（b53a1cc）。
⚠️ A1巡查 2026-03-28：A4 T-A4-001 已超過 48h 閾值 — 距上次 A4 直接 commit (e166169, 2026-03-26) 現逾 48h，S5 仍卡在 93.5%。🔴 CRITICAL：需 Owner 立即重啟 Colab（lb99104@gmail.com）。A0 bot session resume 修復成功（EXP-S009，6b19f4f）。其餘 agent 無異常。
🚨 A1 記憶斷裂事件 2026-03-28：Owner 重開 session 幫 A1 拿 MCP 工具時，session 誤以 A0 模式啟動，A0 大改 skills/mcp-usage-guide.md（cd8a297），A1 完全失憶。此為 EXP-S010：A0/A1 session 混淆問題。根本原因：重開 Claude Code 時需確認進入 A1（CLAUDE.md 總管）模式，而非 bot 對話模式。下次重開：先確認 cwd 為 maplab-ai-handbook/，再貼 A1 recall prompt。
⚠️ A1巡查 2026-03-28 下午：A7 Phase 2 活動未登記 — commit aea3094（Phase 2 20筆CSV驗證+Q1-Q10重構 v2.0）+ f239b40（T-A7-002 80/20任務清單 10大任務+執行路線圖）已落地，但 CURRENT_STATUS 任務表仍顯示「Phase 1 完成，待新任務」。請 A7 補更新任務狀態。
⚠️ A1巡查 2026-03-28 下午：A4 S5.5 GPS 進度超前文件記錄 — commit b1be7c6 顯示 S5.5 GPS partial(1221/no_gps)，CURRENT_STATUS 任務表仍標示「S5.5 GPS planned」，已過時。
✅ A1巡查 2026-03-28 下午：A5 T-A5-002 進度超前已修正 — 任務表已更新（服務費可選/長桌費/車馬費下拉/DropdownHelper均已完成，dbcf9d4）。
⚠️ A1巡查 2026-03-28 晚間：A5 T-A5-002 Task Card 待 A5 更新 — handoff/tasks/T-A5-002.md 斷點尚未反映最新進度（服務費/車馬費/長桌費完成），請 A5 下次開工前補更新 Task Card。
⚠️ A1巡查 2026-03-29 午後巡查：A4 CRITICAL 第三天 — S6 Colab 距 b1be7c6 (2026-03-28) 已逾 36h，無 A4 新 commit。Owner 需立即重啟 Colab (lb99104@gmail.com)。
⚠️ A1巡查 2026-03-29 午後巡查：A5 Task Card 第三次連續警告 — handoff/tasks/T-A5-002.md 仍未反映服務費/車馬費/長桌費完成進度。A5 下次開工前第一件事：補更新 Task Card。
⚠️ A1巡查 2026-03-29 午後巡查：A7 今日無新 commit — T-A7-001 Phase 2 與 T-A7-002 均標為 🔄 進行中，但今日無 A7 活動記錄。若 A7 有執行未 commit，請補存檔。
⚠️ A1巡查 2026-03-29 午後巡查：新治理功能未入 A1 recall 斷點 — SECTION 7 全域檢查器 (faed6a9) + SECTION 8 權限治理 + 10 credential skills v3.5 (6e80723) 今日落地，已於本次巡查補寫入 RECALL_PROMPTS。
✅ A1巡查 2026-03-29 午後巡查：A3 T-A3-001 狀態更正 — 2aca2ae 確認 GTM方案B規格 (#14) + 受眾分析 (#15) 已記錄，任務表從「🔲 可認領」更新為「🔄 進行中」。
⚠️ A1巡查 2026-03-29 每日巡查：A4 CRITICAL 持續 — S6 Colab 距上次 A4 commit (b1be7c6, 2026-03-28) 已逾 24h，仍未重啟。Owner 需立即登入 lb99104@gmail.com Colab 重啟 pipeline。任務表已更正：T-A4-001 S5.5 GPS 從「planned」改為「partial(1221/no_gps)」；T-A7-001 更新為 Phase 2；T-A7-002 新增入任務表。A0 今日 03:25 有新 commit (#7 skip record + next-three-report)。A5 Task Card 仍未更新（連續兩次巡查標記）。

⚠️ A1巡查 2026-03-29 晚間巡查：A6 新任務補登記 — LINE 業務報價助手系統 v1.0+v1.1（d9fba1a, 3a2df7b）今日落地（18:37+19:28），已補入任務表 T-A6-001。架構：三層資料模型（LINE真實對話+A6協作對話，source欄區分）+ Sheets 3個分頁（SALES_INTAKE/REVISION_LOG/CONVERSATION_LOG）+ A6 SOP skill 建立。
⚠️ A1巡查 2026-03-29 晚間巡查：A4 CRITICAL 第四天 — 距 b1be7c6 (2026-03-28) 已逾 48h+，S6 Colab 仍未重啟。Owner 需立即登入 lb99104@gmail.com 重啟 pipeline（剩約 13,301 張，約 50h/Colab 標準速度）。
⚠️ A1巡查 2026-03-29 晚間巡查：A7 持續無活動第二次晚間標記 — T-A7-001 Phase 2 與 T-A7-002 均 🔄 進行中，今日仍無 A7 新 commit。若 A7 有執行請補存檔；若無計畫，請 Owner 確認 A7 是否暫停。
⚠️ A1巡查 2026-03-29 晚間巡查：A5 Task Card 第四次連續警告 — handoff/tasks/T-A5-002.md 仍未反映服務費/車馬費/長桌費完成進度。A5 下次開工第一件事：補更新 Task Card（已連續 4 次巡查標記，升級為 🔴）。
⚠️ A1巡查 2026-03-29 晚間巡查：SECTION 9 新治理功能已落地 — 0076a3a feat(governance): SECTION 9 API三層備援 + 身份確認 + CLAUDE.md指向器，已補入 A1 recall 斷點。A6 SOP skill (skills/a6-rapid-quote-sop.md) 同步建立。

✅ A1巡查 2026-03-31：A7 恢復活動 — 3 commits 落地：(1) 68df5d7 skills v2.0 Phase 2 重寫（8種對話模式+跨部門SOP+Q7/Q10業務人工決策）(2) d165d7d reply-templates v1.0 Mina 操作版模板庫 Q1-Q10 (3) cf9f166 T-A7-002 v1.1 任務6+10完成。之前連續兩晚無活動警告解除。
✅ A1巡查 2026-03-31：A4 Gemini API key 已更換 — 舊 key leaked (b822f90)，已 redact (fe49f3e)，新 key 記錄於 Notion。S6 Colab 重啟 blocker 解除，待 Owner 登入重啟。A4 Task Card 已建立 (35acbbf)。
⚠️ A1巡查 2026-03-31：A5 Task Card 第五次連續警告 🔴 — handoff/tasks/T-A5-002.md 仍未更新。已連續 5 次巡查標記。
⚠️ A1巡查 2026-03-31：品項去重 v2 資料落地 — de7837c 29,115筆→3,794唯一品項（50匹配Items/3,744未匹配/63未報價），data/quote_items_deduped.json。
⚠️ A1巡查 2026-03-31：A1 治理修復 — a130e03 身份確認修復 + f16b8ea start-a1.sh + d5ed475 A0混淆描述修復 + fe49f3e API key redact。

✅ A1巡查 2026-03-31 午後：A4 S6 Colab 重啟確認 — 326c6f0 (16:07) 確認 S6 已重啟執行 2023 batch；S5.5 GPS 決策 no_gps（Takeout JSON未存Drive，根本原因確認）。Owner Action Required 對應項目解除。
⚠️ A1巡查 2026-03-31 午後：A6 T-A6-001 接近 48h 閾值 — 上次 A6 commit 3a2df7b 為 2026-03-29 19:28，至今約 44.5h，距 48h 閾值約 3.5h。若今日無新 commit，請 Owner 確認 A6 是否有進度未存檔。
✅ A1巡查 2026-03-31 午後：A5 Task Card 第六次連續警告 🔴 → ✅ 已解除 — b6666bd + 21e366f 今晚落地（21:55+22:14），handoff/tasks/T-A5-002.md 已更新（Owner設計確認版+EXP-A5-001事件紀錄+使用情境補入）。連續 7 次巡查標記後終於解除。
⚠️ A1巡查 2026-03-31 午後：AGENT_RECALL_PROMPTS 斷點已同步更新 — A4 S6狀態從「stalled 18.2%」更新為「已重啟」；A6 角色表從「🔲 新建」更新為「🔄 進行中」。
⚠️ A1巡查 2026-03-31 22:16：A6 T-A6-001 超過 48h 閾值 🔴 — 上次 A6 commit 3a2df7b (2026-03-29 19:28) 距今已逾 50.8h，超過 48h 警戒線。LINE 業務報價助手系統 v1.1 架構已建立，但無後續進展 commit。Owner 需確認 A6 是否有進度未存檔，或確認目前 T-A6-001 阻塞原因。
⚠️ A1巡查 2026-04-01 09:00：A6 T-A6-001 🔴 CRITICAL 持續第三天 — 距 3a2df7b (2026-03-29 19:28) 已逾 74h+。前次 ccbb944 晚間巡查標記後仍無新 commit。Owner 需立即確認 A6 阻塞原因，或決定 T-A6-001 暫停。
⚠️ A1巡查 2026-04-01 09:00：A4 T-A4-001 ⚠️ WATCH — S6 Colab 重啟後 (326c6f0, 2026-03-31 16:07) 至今約 20h 無新 commit。未達 48h 閾值，但 Colab 斷線風險高。下次巡查（04-01 晚間）需確認 S6 進度。
⚠️ A1巡查 2026-04-01 09:00：A3 ⚠️ WATCH — T-A3-001 (GTM方案B待技術實作) + T-A3-002 (廣告確認中) 均 🔄，最近 24h 無 A3 新 commit。若有執行進度請補存檔；若等待外部條件（GTM權限/廣告成效週期），請在 Task Card 補記阻塞原因。

✅ A1巡查 2026-04-01 22:10：A6 T-A6-001 CRITICAL 解除 — 92513c8 docs(A6): 建立 T-A6-001 Task Card (19:07) 今日落地，A6 恢復活動。連續三天 🔴 警告正式解除。同日 82cd6eb 報價系統 v2 使用者回饋 + 1bbcd0f 報價單 makeCopy 修復，A5/A6 均有實質進展。
⚠️ A1巡查 2026-04-01 22:10：A4 T-A4-001 狀態不一致 — CURRENT_STATUS 顯示 S6(2023) 🔄 進行中，但今日 commits 顯示 S11(2024) 已執行（b82aeea 14:35 + de2cf2e 20:54，2600/12213 執行中 6h20m）。S6 完成狀態未記錄。已更新任務表，但需 A4 補充 S6 完成情況至 Task Card。
⚠️ A1巡查 2026-04-01 22:10：A3 持續無活動（第二次晚間標記）— T-A3-001 GTM方案B + T-A3-002 廣告成效 均 🔄，09:00 巡查後仍無 A3 新 commit。若等待外部條件請在 Task Card 補記原因。距 T-A3-001 最後記錄 (2aca2ae) 已逾 72h。
⚠️ A1巡查 2026-04-01 22:10：A7 ⚠️ WATCH — T-A7-001 Phase 2 + T-A7-002 均 🔄，今日無 A7 新 commit（上次活動 2026-03-31 cf9f166）。未達 48h，明日巡查需追蹤。

⚠️ A1巡查 2026-04-02 09:00：A7 超過 48h 閾值 🔴 CRITICAL — T-A7-001 Phase 2 + T-A7-002 均 🔄 進行中，上次活動 2026-03-31 cf9f166，距今已逾 58h。連續兩次 WATCH 後正式升級為 🔴。Owner 需確認 A7 是否有進度未存檔，或決定暫停等待外部條件。若 A7 有執行紀錄請立即補 commit。
⚠️ A1巡查 2026-04-02 09:00：A3 持續無活動第四天 🔴 CRITICAL — T-A3-001 GTM方案B + T-A3-002 廣告成效 均 🔄，最後 commit 2aca2ae 距今已逾 96h（約 2026-03-29 22:10 起）。連續多次 WATCH 正式升級為 🔴。Owner 需確認：(a) A3 是否有外部阻塞原因（GTM 權限待核准 / 廣告成效觀察期），若有請在 Task Card 補記；(b) 或明確指示 A3 任務暫停。
⚠️ A1巡查 2026-04-02 09:00：A4 S11(2024) ⚠️ WATCH — 最後 commit de2cf2e (2026-04-01 20:54) 距今約 12h，未達 48h 閾值。Colab 斷線風險持續存在，下次巡查（04-02 晚間）需確認 S11 進度 commit。
⚠️ A1巡查 2026-04-02 09:00：A6 T-A6-001 ⚠️ WATCH — CRITICAL 昨日解除（92513c8 Task Card 建立），最後 commit 約 14h 前，未達 48h。繼續監控後續 LINE 業務報價助手 v1.1 開發進展。

⚠️ A1巡查 2026-04-02 16:30 午後巡查：過去 8h 無任何 agent 新 commit — A7 🔴 CRITICAL 持續第 67h+（T-A7-001 Phase 2 + T-A7-002，上次活動 2026-03-31 cf9f166），A3 🔴 CRITICAL 持續第 105h+（T-A3-001 GTM方案B + T-A3-002，上次 2aca2ae ~2026-03-29 22:10）。A4 S11(2024) ⚠️ WATCH 升至 ~21h（de2cf2e 2026-04-01 20:54），距 48h 閾值剩約 27h，Owner 需於明日 09:00 前確認 S11 Colab 仍執行中。A6 T-A6-001 ⚠️ WATCH ~22h，正常範圍內。

⚠️ A1巡查 2026-04-02 晚間巡查：A0 今晚活躍 ✅（T-A5-004 Phase 1 完整收尾：Items照片提取16筆+URL修正+重新編號91格+items-management Skill+220個舊worktrees清理，5e6d3b4）；A3 🔴 CRITICAL 持續第5天 ~110h+（上次 2aca2ae ~2026-03-29，Owner 需確認外部阻塞原因或指示暫停）；A4 S11(2024) ⚠️ WATCH 升至 ~26h（de2cf2e 2026-04-01 20:54），距 48h 閾值剩 ~22h，需明日 09:00 前確認 Colab 仍執行中，否則升級 CRITICAL；A7 🔴 CRITICAL 持續第3天 ~72h+（T-A7-001 Phase 2 + T-A7-002，上次 cf9f166 2026-03-31）；A6 T-A6-001 ⚠️ WATCH ~28h（正常範圍）。A5 T-A5-004 Phase 1 完成，A5 無其他新活動（T-A5-002 等待 Owner 回饋正常）。

### 🔴 Owner Action Required

| 項目 | 說明 | 優先級 |
|------|------|--------|
| ~~A4 Colab S6 重啟~~ | ✅ 326c6f0 確認 S6 已重啟執行中（2026-03-31 16:07）| ✅ 已解除 |
| Items DST 成本補填 | 在 MAPLAB_外燴系統_v0.1 Items 表補填 21 筆 DST 品項成本（E 欄）| 高 |
| Extension v4.8 重裝 | Chrome 重新安裝 Extension v4.8（private repo 已改用 GitHub Contents API）| 中 |
| A0 User Preferences 貼入 | 在 A0 bot 貼入 User Preferences 設定（個性化回覆偏好）| 中 |

## 最新決策

- 2026-04-02（巡檢）：**系統巡檢 ✅** — (1) T-A5-001 task card 補建（handoff/tasks/T-A5-001.md）。(2) skills/system-audit/SKILL.md 建立（巡檢 SOP）。(3) skills/session-lifecycle/SKILL.md 建立（session 開始/結束規則）。(4) AGENT_RECALL_PROMPTS A0 段落追加三條操作規則（立即commit / ls確認 / CURRENT_STATUS是commit一部分）。(5) handoff/2026-03-14-master-data-agent.md 歸檔到 archive/。

- 2026-04-02（深夜）：**T-A5-004 Phase 1 完整收尾 ✅** — (1) Slide 照片提取：16 筆有效 URL 寫入 Items K 欄（scripts/extract_slide_photos_to_items.py，drive scope，模糊比對 ≥60）。(2) Items 照片 URL 修正：5 筆移轉 + 7 筆清除（誤配 score=4 清除）。(3) Items 重新編號：91 格，按 default_cost 升序排序，APP/DST/MAIN 各自連號。(4) item_id 引用掃描：QUOTE_DRAFT（9 筆 VLOOKUP by name，不受影響）、DropdownHelper（5 筆 FILTER by category，不受影響），無寫死舊 item_id 的 Sheet。(5) items-management Skill 建立（skills/items-management/SKILL.md），含 Input/Output 格式供 A6 呼叫。(6) 220 個舊 worktrees 清理。(7) AGENT_RECALL_PROMPTS A0 段落補充 Apps Script 自主操作教訓 + Worktree 結尾規則。

- 2026-04-02：**T-A5-004 Phase 1 Items K欄照片提取 ✅** — 用 Python + Google Slides API + Sheets API（scripts/extract_slide_photos_to_items.py），從文學館 Slide（16R9Ivi...）提取 Menu Showcase 品項照片 URL，模糊比對後寫入 16 筆到 Items K 欄。Slide API 不需 presentations scope，用 drive scope 即可。4 筆誤配已清除（score=4 threshold 過低）。AGENT_RECALL_PROMPTS A0 段落補充 Apps Script 自主操作教訓 + Worktree 結尾規則。

- 2026-04-01：**v6.0 Phase 3.1 Dashboard 自動更新 ✅** — crontab `*/30 * * * *` + `scripts/update-dashboard.py` 已就位（ef2c21b），每 30 分鐘自動同步 CURRENT_STATUS + git log 至 Sheets DASHBOARD 分頁。Phase 3 自動化+策略循環正式啟動。

- 2026-03-31：**v6.0 Phase 2 業務閉環 MVP 落地** — (1) QUOTE_WORKBENCH 分頁建立（14欄：case_id→terms_type）(2) 4組下拉驗證：SALES_INTAKE status+event_type、REVISION_LOG change_type+reason_tag (3) Phase 2 四個分頁全部就緒：SALES_INTAKE/REVISION_LOG/CONVERSATION_LOG（已存在）+ QUOTE_WORKBENCH（新建）。下一步：Owner/業務填測試資料 → A6 報價測試。
- 2026-03-31：**v6.0 Phase 1 觀測性建設落地** — (1) Sheets Dashboard 建立（Task Board 12筆任務 + Owner Actions 5筆）(2) AGENT_RECALL_PROMPTS 更新：A1 加 Sheets 巡查同步、A0 加 Artifacts 看板渲染 (3) 設計文件：projects/v6-architecture.md。v6.0 三階段：Phase 1 觀測性 / Phase 2 業務閉環 MVP / Phase 3 自動化+策略循環。
- 2026-03-31：A4 Gemini API key 更換完成（舊 key leaked → redact → 新 key 記錄於 Notion），S6 Colab 重啟 blocker 解除
- 2026-03-31：A7 Phase 2 實質進展 — reply-templates v1.0（Mina 操作版）+ skills v2.0（8種對話模式）+ T-A7-002 任務6+10完成
- 2026-03-31：品項去重 v2 資料落地（de7837c，29,115筆→3,794唯一品項）

- 2026-03-29：報價單歷史分析整理完成 — 產出 data/quote-terms-reference.md（個人/企業/特規三區條款）+ data/quote-items-unmatched.md（932份報價 × Items主表比對：30品項已匹配、7品項未納入Items表供Owner參考）

- 2026-03-28：QUOTE_DRAFT 報價單修復完成（VLOOKUP 統一讀 E 欄成本、業務報價 I 欄、成本小計 H 欄、D6-D8 APP 下拉、D13 DST 下拉、E32 業務報價總額、H33 毛利率）
- 2026-03-28：Items backup 覆蓋 Items + QUOTE_V2_FUTURE 刪除
- 2026-03-28：Google Sheets MCP OAuth token 恢復成功（google-token.json 建立）
- 2026-03-28：Extension v4.8 修復（private repo 改用 GitHub Contents API）
- 2026-03-28：歷史訂單分析完成（2026 真實 6 筆、2025 為合成資料）
- 2026-03-28：車馬費分析（新化 18.4km/30min=$720、歸仁 14.8km/35min=$780，邏輯為人力時間成本 200×4=$800）
- 2026-03-28：A2 T-A2A3-001-B 同事接手完成 — (1) 確認同事無commit記錄，A2接手 (2) 子任務3 LP 3頁建立（Post 1584/1587/1588, Draft） (3) 子任務4 內連結56/57篇完成 (4) 首頁排名確認：GSC avg position 8.0未下降 (5) 子任務5等7-14天。
2026-03-28：A5 Sheets 清理 — Owner 確認三個決策：(1) GFT001-005 不保留（Owner 未加）(2) Items_backup 完全覆蓋 Items（115行/1063 cells 已驗證一致）(3) QUOTE_V2_FUTURE 工作表刪除 ✅ 全部完成。

2026-03-28（深夜）：EXP-S010 — A1/A0 session 混淆 — Owner 重開 session 拿 MCP，誤入 A0 模式，A0 大改 skills/。教訓：重開後先確認角色再操作。A1 記憶此次恢復靠 CURRENT_STATUS.md + git log 重建。
2026-03-28：A4 S5(2022) 確認完成（8,559張：日常5,243/外燴1,221/旅遊2,073）；S6(2023) 跑到 2,950/16,251=18.2% 時 Colab 斷線；領取 S5.5 GPS 日常細分任務（5,243張日常照 → home/shop/other/no_gps，純 Haversine 計算零成本）。ASSET_LOG 驗證：11,509 資料行。

- 2026-03-28：A2 T-A2A3-001 斷點補齊完成 — Task Card 子任務2狀態從🔄更新為✅（Phase1 Title/Desc/Alt+Phase2數字優化36篇+2-A內連結16篇全部確認完成）。子任務3 Landing Page（週歲/婚禮/企業）為下一步。（commit: c17f0e5）
2026-03-28：bot.py session resume 修復成功（claude -p -c flag），有記憶+MCP+bash+Max免費
- 2026-03-27 深夜：bot.py 記憶斷裂根因確認（claude -p one-shot = 無記憶），修復方向：回到 Anthropic SDK + OAuth token + conversation_history；A0/A1 並列架構 v3.2 由 A1 自主建立；CLAUDE.md 已同步 RECALL_PROMPTS；experience-log 新增 F007-F009 + S007-S008

- 2026-03-27：T-A0-002 完成（Agent 角色表、GitHub 進度報告、Pipeline 專案頁面加了 GitHub 引導）；A0 每小時 GitHub 同步巡查排程已設定
- 2026-03-27：A2 T-A2A3-001 子任務2 Phase 2完成 — SEO Title 數字優化 36篇（Title Readability 全綠），分數抽檢 Post 253(50→51) Post 564(81→84 Good) Post 1246(54→55) Post 1227(69)。API 可修正項目已全部完成（FK in Title/Desc/Alt + Number in Title），剩餘分數需 Elementor 編輯或 ToC 插件。
- 2026-03-27：A0 總調度秘書角色建立（Cowork Dispatch Secretary），定位為跨系統橋接層；Telegram bot daemon 上線（launchd 自啟，免費指令讀檔模式，9 個指令）；Notion 定位降級為可視化報告介面，不再作為 Agent 狀態來源

- 2026-03-27：A2 SEO Title 數字優化完成 + Google Ads 搜尋字詞分析 — (1) 36篇SEO Title加入數字（Title Readability全綠，分數+1~3）(2) API可修正項目全部完成（Title/Desc/Alt/數字）(3) Google Ads 485個搜尋字詞分析，識別3個排除關鍵字建議 (4) seo-ads-agent v2.5（§17 Phase2 + §18搜尋字詞分析）(5) Elementor限制下分數天花板約51-84/100

- 2026-03-26：A2 T-A2A3-001 子任務1+2完成 — (1) FK修正11篇(57/57全匹配) (2) SEO Title 27篇+Meta Desc 35篇+Alt Text 51篇修正(分數~54-76) (3) 任務分拆：子任務3+4+5→T-A2A3-001-B由同事接手 (4) seo-ads-agent v2.4(§17執行紀錄+SEO Performance更新) (5) Elementor限制文件化：RM無法讀取Elementor內容，分數天花板約54-76

- 2026-03-26：A2 Google Ads 轉換動作設定確認 — Owner 完成 PMax 轉換目標設定（廣告活動專屬：外連點擊），22 個轉換動作已記錄至 seo-ads-agent.md §16。主要轉換：LINE 事件(21次) + LINE 領取菜單(33次)。「網站左下角 fb massage」按鈕已從網站移除，建議停用該轉換動作。下一步：T-A2A3-001 SEO 關鍵字頁面補足。
- 2026-03-26：A2 T-A2-001 完成 — 文章精選圖片補齊 57/57（0 重複）。跨 5 個 Google Drive 相簿（2025/2024/2023/map2019/素材開幕）上傳 47 張獨立圖片至 WordPress，全部含 SEO 命名 + alt text。已標記 5 篇圖文相符待抽查文章（Post 1027/1168/1244/253/1231）。
- 2026-03-25：A1 系統重組 — 角色拆分（A2/A3獨立、新增A6/A8）、AGENT_RULES v3.0、AGENT_RECALL_PROMPTS.md 建立、Extension v4.3（角色選擇器）、SECTION 2.1 強制存檔規則（30min checkpoint + 接續 prompt）、錯誤 006 記錄
- 2026-03-25：Extension v3.0 設計完成 — commit history 面板 + checkpoint 偵測 + 48h overdue 警示 + GitHub Actions 每日巡查 workflow 待部署
- 2026-03-24：A2 T-A2-001 文章精選圖片補齊 — Phase 2 進度報告。(1) 全 57 篇文章已有 featured_media（Phase 1 完成）。(2) 目前 22 篇擁有獨立唯一圖片，35 篇仍共用 8 張重複圖片待替換。(3) 已從 Google Drive「2025 年的相片」上傳 13 張獨立圖片至 WordPress（media 1510-1512, 1515-1520, 1523-1525, 1528, 1531-1533），均含 SEO 命名 + 中文 alt text。(4) 圖片篩選標準：食物特寫/場景佈置/無人場景優先，排除人臉與非MAPLAB品牌logo與酒類廣告。(5) 已發現 Google Drive 2025相簿可用圖源有限（約20張合格），需討論是否開放其他相簿或圖源。(6) 下一步：繼續瀏覽 Google Drive 找剩餘獨立圖片，逐篇替換 35 篇重複配圖。
- 2026-03-24：[crash-recovery 補登] A2 Session — SEO 基礎建設 + Google Drive→WordPress 雲端圖片上傳突破。(1) SEO 技能書建立。(2) 雲端圖片上傳：Clipboard API 跨 Tab 傳圖法，gdrive-to-wordpress-upload-guide v1.0。(3) 技能書更新。(4) T-GBP-001 已建立。
- 2026-03-24：A5 T-A5-001 完成 — Items 去重 + 全品項重新編碼（108品項，4類別排序連號）
- 2026-03-23：A4 Phase 4 v4.0 — S1-S4 done, S5 2022 batch 35% via REST API
- 2026-03-23：Owner 狀態更新 — T-A3-001 方案 B 確認、T-A4-001 照片清洗中不急、T-A3-002 已上線 Meta 廣告
- 2026-03-23：A1 收尾 — CHANGELOG v3.9 + handoff-to-A5.md + PROTOCOL/task-progress-guide/AGENT_RULES 優化
- 2026-03-23：A1 系統治理 — PROTOCOL v1.5 + AGENT_RULES v2.2 + task-progress-guide v1.1 + superpowers v1.6
- 2026-03-23：A1 跨部門溝通 — TimeTree 事件資料增強 v2.0（746 筆外燴事件含客戶名）
- 2026-03-20：A4 Photo scan 完成 + Gemini API Key 設定完成
- 2026-03-20：T-A1-002 結案（全部 7 子任務完成）
- 2026-03-19：系統巡查修復 + Phase 4.2 全系統文件對齊完成
- 2026-03-18：A2+A3 合併 + 新增技能書 + Phase 4 第一階段完成

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
| 📊 詳細狀態（參考） | CURRENT_EXECUTION_BOARD.md | 各 Agent 詳細狀態，非強制讀取 |

## 知識地圖（資料在哪裡）

> 找不到資料？查這張表。

| 類別 | 路徑 | 內容 |
|------|------|------|
| 客戶/活動資料 | data/timetree_events_2022_2026.json | 746 筆外燴事件（含客戶名、日期、活動類型）|
| 品項資料 | data/item-master-cross-reference.md | 108 品項對照表（APP/DST/MAIN/BEV）|
| 品項頻率 | data/item-frequency-top50.md | 399 筆歷史訂單品項分析 |
| 品項去重 v2 | data/quote_items_deduped.json | 3,794 唯一品項（50匹配/3,744未匹配/63未報價）|
| 報價系統 | projects/maplab-master-data.md | A5 報價邏輯 + Sheets 結構 |
| SEO/廣告 | projects/seo-ads-agent.md | A2/A3 核心文件 + 轉換動作快照 |
| 照片管線 | projects/maplab-pipeline.md | A4 照片分類流程 + Gemini API |
| 客服系統 | projects/ai-reply-system.md | A7 回覆系統架構 |
| 廣告監控 | projects/maplab-ads-monitor.md | A3 ads_agent.py 技術文件 |
| 報價簡報 | projects/slides-quotation-system.md | A6 Google Slides 報價 |
| 網站優化 | projects/maplab-kitchen-web-optimization.md | WordPress 技術 |
| 交接紀錄 | handoff/tasks/T-xxx.md | 各任務斷點 + 接續 prompt |
| 交接模板 | handoff/tasks/TASK_CARD_TEMPLATE.md | 新任務卡模板 |
| 經驗紀錄 | skills/experience-log.md | 12 條成功/失敗經驗 |
| 錯誤紀錄 | AGENT_RULES.md SECTION 3 | 6 條系統錯誤 + 解法 |

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

## 已完成（不要再做）

- ✅ Phase 1-3 全部完成
- ✅ SYSTEM_MAP / WORKFLOW_MAP / PROTOCOL / BOARD 治理文件
- ✅ 26 本技能書（含 5 本新角色技能書 A3/A4/A5/A6/A7 + GPS 細分指南）
- ✅ A2+A3 合併（後於 03-25 拆回獨立部門，A1-A8 八角色架構）
- ✅ 所有已知 Issues #004-#009 已修復
- ✅ A5 Items 品項從 300 筆精簡至 ~139 筆
- ✅ A5 QUOTE_DRAFT 極簡版 MVP
- ✅ A5 TimeTree 2025 全年密集日清單
- ✅ A1 PROTOCOL v1.4 + AGENT_RULES v2.1 + task-progress-guide + 系統行為強化
- ✅ A1 TimeTree 事件 v2.0（746 events, 2022-2025）
- ✅ T-A2-001 文章精選圖片補齊（57/57 獨立配圖，Google Drive 跨相簿 → WordPress，SEO 命名 + alt text）
- ✅ Phase 4 第一階段：治理重構
- ✅ Phase 4.2：全系統文件對齊
- ✅ T-A1-002 Phase 4.1 系統治理升級全部完成
- ✅ AGENT_RULES v2.0（SECTION 0 修復 + SECTION 5 Repo 管控/Notion 禁令）
- ✅ 系統巡查：關鍵 20% 問題修復
- ✅ A4 TimeTree lookup committed（PR #9, 361 dates）
- ✅ A4 Photo scan 60,584 files + Gemini API Key 設定驗證完成
- ✅ T-A5-001 Items 去重 + 全品項重新編碼完成（108品項）

- ✅ AGENT_RULES v3.0 角色重組（A1=Claude Code, A2/A3 拆開, 新增 A6/A8）
- ✅ AGENT_RECALL_PROMPTS.md 建立（8 角色完整召喚 prompt + 斷點 + 可用工具）
- ✅ Chrome Extension v4.6（角色選擇器 + 高對比 UI + auto-save token）
- ✅ SECTION 2.1 強制存檔規則（30min checkpoint + 接續 prompt）
- ✅ 3 個定時巡查排程（08:00/16:00/22:00）
- ✅ Mac mini 每小時自動 git pull
- ✅ MCP 工具接通：Google Sheets/Drive/Analytics/Search Console/Ads + Meta Ads
- ✅ GCP 專案 MAPLAB-AI 建立 + 18 個 API 啟用
- ✅ Anthropic Skills 市場加入

> 這份文件必須保持簡短。詳細資訊請查對應的 Task Card 或 BOARD。
