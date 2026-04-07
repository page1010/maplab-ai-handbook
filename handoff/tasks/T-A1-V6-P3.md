# Task Card: T-A1-V6-P3

---

## Meta
- **Task ID**: T-A1-V6-P3
- **任務名稱**: v6.0 Phase 3 自動化+策略循環（LINE webhook + A6 獨立 bot + strategy-cycle-guide）
- **負責 Agent**: A1
- **建立日期**: 2026-04-08
- **最後更新**: 2026-04-08
- **狀態**: 🔲 待開始

## Goal（目標）
自動化閉環：LINE webhook 自動觸發 A6、A6 獨立 bot 穩定運行、strategy-cycle-guide 讓 Owner 每月回顧有結構。

## Preconditions（前置條件）
- [ ] T-A1-V6-P2 完成（業務閉環 MVP 驗證通過）

## Confirmed（已確認事項）
- A6 bot 已上線（launchd 開機自啟），基礎設施就緒
- LINE Bot Webhook 技能書已建立（skills/）

## Plan（本輪計畫）
1. LINE webhook → A6 bot 自動觸發流程測試
2. strategy-cycle-guide 文件建立（每月策略回顧 SOP）
3. A6 獨立 bot 穩定性驗證（48h 運行確認）

## Done（已完成）
- （尚未開始）

## Next（下一步）
- 等 Phase 2 完成後認領

## Blockers（阻塞點）
- 前置：T-A1-V6-P2 完成

## Files Modified（修改的檔案）
- （尚未開始）

---

## 接續 Prompt

```
你是 MAPLAB A1 系統總管。
repo: https://github.com/page1010/maplab-ai-handbook
先讀 CURRENT_STATUS.md，再讀 handoff/tasks/T-A1-V6-P3.md。

上次做到：尚未開始（等 Phase 2 完成）
下一步：確認 Phase 2 完成 → 規劃 LINE webhook 自動觸發流程
Blocker：T-A1-V6-P2 需先完成

讀完文件後輸出 Startup Check。必拿：skills/task-progress-guide.md
```
