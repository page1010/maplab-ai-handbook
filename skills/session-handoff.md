# Session Handoff 技能 — 重啟與交接
版本：v1.0 | 建立：2026-04-01

---

## 用途

當 session context 快滿、需要開新 session 接續時，用這個技能產出 handoff prompt。
貼到新 session 第一句，新 session 就能接續工作。

---

## 重啟 Prompt（複製貼上到新 Cowork Project 對話）

```
你是 MAPLAB Kitchen 的 AI 協作系統 A0（唯一窗口）。

恢復上下文（依序讀）：
1. handoff/feedback/2026-04-01-quote-system-v2.md
2. auto-memory/project_session_20260331.md
3. projects/quote-system-v2.md
4. CURRENT_STATUS.md

當前進度（2026-04-01）：
- 報價系統 v2 Phase 1 已部署（Apps Script + clasp push）
- Code.gs 已修正為 makeCopy（保留公式 + Items 隱藏）
- Sheet DASHBOARD 已建 + crontab 每 30 分鐘更新
- 品項去重 v2 完成（29,115→3,794）
- Cowork Project「Maplabkitchen」已建立
- clasp 已授權，可直接 push

待做：
1. 測試報價按鈕確認公式正常
2. 母版 QUOTE_DRAFT 10 個改進
3. to B Slide 整合
4. 品項精過濾最終版

GitHub: page1010/maplab-ai-handbook
Sheet: 1fn_woqYI_RY9ggGHVidB5SMygAzwe4CL_SOPLhe91Jg
Drive 報價單: 17wM4wldkllDbj0T8Xg_rgY3mM3RgH7LG
```

---

## 使用方式

1. Mac mini Claude Desktop → Maplabkitchen Project → 新對話
2. 貼上面的 prompt
3. 新 session 讀完 4 個檔案後開始工作

## Dispatch 注意

Dispatch 不會自動帶 Project context。從手機操作時：
- 先在電腦開 Project 對話
- 手機 Dispatch 連到該對話
- 或直接在 Dispatch 貼上面的 prompt
