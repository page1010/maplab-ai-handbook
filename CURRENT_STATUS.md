# CURRENT_STATUS.md — 唯一最新狀態入口

> **所有 Agent 開工前第一個讀的檔案。這裡的資訊優先於所有其他文件。**
> 若其他文件與本檔衝突，以本檔為準。

最後更新：2026-03-20 | 更新者：A4

---

## 系統版本

- **Version**: v3.6
- **Phase**: 系統巡查完成 ✅ 關鍵問題已修復
- **Status**: Active

## 當前進行中任務

| Task ID | 任務 | 負責 Agent | 狀態 | Task Card |
|---------|------|-----------|------|-----------| 
| T-A5-001 | Items 甜點去重 + 全品項重新編碼 | A5 | ⏸️ 等使用者手動去重 | handoff/tasks/T-A5-001.md |
| T-A5-002 | QUOTE_DRAFT 報價單欄位增強 | A5 | 🔲 待開始 | handoff/tasks/T-A5-002.md |
| T-A5-003 | 熱客招待品項定義 | A5 | 🔲 待開始 | — |
| T-A4-001 | Phase 4 vision.py Gemini 分析 | A4 | 🔶 TimeTree done, 需 Gemini API Key | — |
| T-A2A3-001 | SEO 關鍵字頁面補足 | A2/A3 | 🔲 待開始 | — |
| T-A3-001 | GTM LINE 按鈕追蹤修復 | A3 | ⏸️ 等使用者執行 | — |

## Blockers（阻塞事項）

- A5：甜點去重需使用者手動完成後才能重新編碼
- A5：使用者需填 Items.D 欄 default_price
- A4：需 Gemini API Key（Phase 3.5 done, TimeTree lookup committed, Vertex AI 404）→ 請到 aistudio.google.com/apikey 建立
- A3：等使用者完成 Canva C款素材 / 暫停空殼活動 / 確認 A組

## 最新決策

- 2026-03-19：系統巡查修復 — AGENT_RULES v1.9（召喚 Prompt + Git 規則）+ REPO_SYNC_RULES v1.0 + master-data v1.5 + ads-monitor v1.2
- 2026-03-19：Phase 4.2 全系統文件對齊完成（README v2.4 / SYSTEM_MAP v2.1 / WORKFLOW_MAP v2.2 / BOARD v2.2 / CHANGELOG v3.5）
- 2026-03-18：A2+A3 合併為 SEO & Ads Team（AGENT_RULES v1.8）
- 2026-03-18：新增 sheets-data-cleaning-guide + photo-pipeline-toolkit-guide
- 2026-03-18：Phase 4 第一階段完成 — CURRENT_STATUS + TASK_QUEUE + Task Card 模板 + PROTOCOL v1.2

## Source of Truth（有效文件清單）

> Agent 只需讀以下文件。其他文件僅供參考，不作為執行依據。

| 用途 | 檔案 | 說明 |
|------|------|------|
| 🎯 最新狀態（你在這裡）| CURRENT_STATUS.md | 唯一入口，最高優先 |
| 📋 任務池 | TASK_QUEUE.md | 所有待辦任務清單 |
| 📖 角色與規則 | AGENT_RULES.md | 你是誰、能做什麼、不能做什麼 |
| 🚀 開工 SOP | AGENT_STARTUP_PROTOCOL.md | 啟動流程 + Startup Check 輸出格式 |
| 📂 任務卡 | handoff/tasks/T-xxx.md | 你認領的任務的詳細狀態 |
| 🔧 技能書 | skills/superpowers-guide.md | 開工前查路由表 |
| 📊 詳細狀態（參考）| CURRENT_EXECUTION_BOARD.md | 各 Agent 詳細狀態，非強制讀取 |

## 已完成（不要再做）

- ✅ Phase 1-3 全部完成
- ✅ SYSTEM_MAP / WORKFLOW_MAP / PROTOCOL / BOARD 治理文件
- ✅ 14 本技能書
- ✅ A2+A3 合併
- ✅ 所有已知 Issues #004-#009 已修復
- ✅ A5 Items 品項從 300 筆精簡至 ~139 筆
- ✅ A5 QUOTE_DRAFT 極簡版 MVP
- ✅ A5 TimeTree 2025 全年密集日清單
- ✅ Phase 4 第一階段：治理重構（CURRENT_STATUS + TASK_QUEUE + Task Card + PROTOCOL v1.2）
- ✅ Phase 4.2：全系統文件對齊
- ✅ 系統巡查：關鍵 20% 問題修復（AGENT_RULES 召喚/Git 規則、REPO_SYNC_RULES 重寫、master-data/ads-monitor 過時修正）（README v2.4 + SYSTEM_MAP v2.1 + WORKFLOW_MAP v2.2 + BOARD v2.2 + CHANGELOG v3.5）

---

*這份文件必須保持簡短。詳細資訊請查對應的 Task Card 或 BOARD。*
