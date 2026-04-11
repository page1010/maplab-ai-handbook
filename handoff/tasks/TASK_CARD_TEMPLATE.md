# Task Card: [TASK_ID]
> 複製此模板建立新任務卡。檔名格式：T-Ax-xxx.md

---

## 接續狀態

> **Agent 冷啟動時第一個看的區塊。每次 checkpoint 必須更新。**

- **狀態**: 🔲 待開始 / 🔄 進行中 / ⏸️ 阻塞中 / 💤 暫停 / ✅ 完成
- **最後活動**: YYYY-MM-DD commit_hash
- **接續點**: [一句話：做到哪，下一步做什麼]
- **阻塞**: 無 / [具體原因 + 誰能解除]

---

## Meta
- **Task ID**: T-Ax-xxx
- **任務名稱**: [一句話描述]
- **負責 Agent**: A?
- **建立日期**: YYYY-MM-DD

## Goal（目標）
[這個任務要達成什麼？成功的定義是什麼？]

## Preconditions（前置條件）
- [ ] [需要先完成的事項]
- [ ] [需要的資源或權限]

## Confirmed（已確認事項）
- [已經確定的事實、決策、規格]

## Plan（本輪計畫）
1. [第一步]
2. [第二步]
3. [第三步]

## Done（已完成）
- [完成的具體項目]

## Next（下一步）
- [接手者該做什麼]

## Blockers（阻塞點）
- [卡住的原因、等待的決策]

## Files Modified（修改的檔案）
- [檔案路徑 + 做了什麼]

## Risks（風險/待確認）
- [不確定的事項、需要 owner 決策的問題]

---

## Checkpoints（每 30 分鐘至少更新一次）

### Checkpoint 1 — [日期 時間]
```
- Read: [讀了什麼]
- Changed: [改了什麼]
- Confirmed: [確認了什麼]
- Next: [下一步]
- Blocker: [阻塞]
```

---

## 接續 Prompt（結束 session 前必填）

> **強制規則**：Agent 結束工作前必須更新「接續狀態」區塊 + 此段落。見 AGENT_RULES.md SECTION 2.1。
> 下一個接手的 agent 直接複製此段貼到 Claude tab 即可開工。

```
你是 MAPLAB [角色編號] [部門名稱]。
repo: https://github.com/page1010/maplab-ai-handbook
先讀 CURRENT_STATUS.md，再讀 handoff/tasks/[Task ID].md。

上次做到：[具體進度，數字化]
下一步：[明確的下一個動作]
Blocker：[如果有的話]
踩過的坑：[這次 session 學到的經驗]

讀完文件後輸出 Startup Check。必拿：skills/task-progress-guide.md
```

---

*模板版本：v1.2 | 建立：2026-03-18 | 更新：2026-04-11 | 變更：新增「接續狀態」區塊作為冷啟動入口*
