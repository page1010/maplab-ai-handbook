# Task Card: T-A1-V6-P2

---

## 接續狀態

> **Agent 冷啟動時第一個看的區塊。每次 checkpoint 必須更新。**

- **狀態**: 🔄 進行中
- **最後活動**: 2026-04-11 b502417
- **接續點**: 4 分頁架構 + DropdownHelper 驗證完成、REVISION_LOG 精簡完成。下一步：建虛擬測試案例 → A6 跑報價流程 → 驗證寫入。
- **阻塞**: 等 A6 實際報價測試

---

## Meta
- **Task ID**: T-A1-V6-P2
- **任務名稱**: v6.0 Phase 2 業務閉環 MVP（4 Sheets 分頁 + A6 報價測試）
- **負責 Agent**: A1
- **建立日期**: 2026-04-08
- **最後更新**: 2026-04-11（A1 格式統一）

## Goal（目標）
建立業務閉環的資料基礎：4 個 Sheets 分頁就位（SALES_INTAKE / CONVERSATION_LOG / REVISION_LOG / Orders）、下拉驗證完成、A6 報價測試跑通。

## Preconditions（前置條件）
- [x] Phase 1 完成（Sheets Dashboard + RECALL_PROMPTS 就位）

## Confirmed（已確認事項）
- 4 分頁已建立（SALES_INTAKE, CONVERSATION_LOG, REVISION_LOG, Orders, OrderLines, OrderCharges）
- DropdownHelper 下拉驗證完成
- REVISION_LOG 已精簡（2026-04-08：移除 change_type，加 quote_version，section/reason_tag 改 dropdown）

## Plan（本輪計畫）
1. 建立測試用虛擬案例資料（SALES_INTAKE + CONVERSATION_LOG）
2. A6 跑一次完整報價流程，確認資料寫入正確
3. 修正報價後確認 REVISION_LOG 填寫流程順暢

## Done（已完成）
- 4 分頁架構建立 + DropdownHelper 驗證
- REVISION_LOG 欄位精簡
- Specials 虛擬範例（SP000）

## Next（下一步）
- 建虛擬測試案例 → A6 跑報價流程 → 驗證寫入
- 完成後進入 Phase 3

## Blockers（阻塞點）
- 等 A6 實際報價測試

## Files Modified（修改的檔案）
- Sheets: SALES_INTAKE / CONVERSATION_LOG / REVISION_LOG / Orders / DropdownHelper
- CURRENT_STATUS.md

---

## 接續 Prompt

```
你是 MAPLAB A1 系統總管。
repo: https://github.com/page1010/maplab-ai-handbook
先讀 CURRENT_STATUS.md，再讀 handoff/tasks/T-A1-V6-P2.md。

上次做到：4分頁+下拉驗證完成，REVISION_LOG 已精簡
下一步：建虛擬測試案例 → A6 報價測試 → 確認資料寫入
Blocker：等 A6 測試

讀完文件後輸出 Startup Check。必拿：skills/task-progress-guide.md
```
