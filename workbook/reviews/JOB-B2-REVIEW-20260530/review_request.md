# JOB-B2-REVIEW-20260530 Review Request

日期：2026-05-30
角色：B2 Investment OS Reviewer
目標：巡查 Investment OS 是否過度建置，並把項目分成 continue / pause / refactor

## Startup Check

我是 B2 Investment OS Reviewer，現在在 `/Users/pagemacmini/maplab-ai-handbook` 執行 review。
我先讀了 `CURRENT_STATUS.md`、`pitfalls.md`、B2/B4 角色文件、OpenClaw output contract、relation graph 與 security boundaries，並對照了 `workbook/task_index.json`。
這次產出會影響 B1 實作、B3 存檔、A1 task module 重建，以及 Owner 看到的 Telegram / Dashboard / Agent Office surface。
輸出會寫到 `workbook/reviews/JOB-B2-REVIEW-20260530/`。
高風險動作需要 Owner / A1 批准的部分：runtime copy 同步、bulk NotebookLM、擴大 OpenClaw 代操、刪除或大幅挪動既有 runtime logs / 外部系統設定。

## 已驗證事實

- 核心 owner-facing surface 已存在：Telegram、Dashboard、Agent Office。
- `OpenClaw pg macmini` 尚未完成端到端驗證，不能升格成完全替代 Owner 的面板。
- `gooaye_batches -> NotebookLM` 仍只能做小任務，不應直接批次化。
- `task_index.json` 還有大量 legacy quote / SEO 任務，active queue 的結構偏雜。
- repo fix 與 runtime copy parity 仍有缺口，這是目前最直接的風險點之一。

## 合理推論

- Investment OS 的核心不是過度建置，而是邊緣實驗太多、收斂太慢。
- 只要 canonical truth chain 不收斂，雲端副本、共享頁、摘要頁就會一直有 stale 風險。
- 現在最需要的不是再做更完整的 surface，而是把既有 surface 變得更小、更穩、更可交班。

## 建議決策

### Continue

- Telegram 手機入口
- Dashboard
- Agent Office switchboard
- B1-B4 角色分工與 summon map
- GitHub HEAD 作唯一真相源的 cloud currency rule

### Pause

- `OpenClaw pg macmini` 全面代操
- `gooaye_batches -> NotebookLM` bulk route
- 任何未完成 runtime parity 的新功能宣告
- 新增更多 owner-facing panels

### Refactor

- `CURRENT_STATUS.md` 改成 active / parked / archive 三層
- `task_index.json` 依 active / paused / archive 清理
- cloud mirror / share / export 全部改成 derived artifact 語言
- review bundle / task card / relation graph 形成固定交班鏈

## 驗證記錄

- 已檢查 relation graph 是否包含本次 task / review bundle / five outputs。
- 已確認 review bundle 目錄已建立於 `workbook/reviews/JOB-B2-REVIEW-20260530/`。
- 本次未碰 runtime logs，不做未列入 scope 的外部系統修改。

## 交辦

- 請 B1 先處理 runtime parity 與同步鏈，讓 repo fix 真的進到 runtime copy。
- 請 B3 將 legacy backlog 依 active / paused / archive 分層，避免 review / task / status 互相污染。
- 若 A1 發現 task module markdown 有更新，再跑 module rebuild，避免 module 與文件不同步。
