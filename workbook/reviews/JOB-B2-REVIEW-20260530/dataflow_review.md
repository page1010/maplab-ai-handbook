# JOB-B2-REVIEW-20260530 Dataflow Review

日期：2026-05-30
角色：B2 Investment OS Reviewer
範圍：Investment OS / MAPLAB 跨專案資料流、freshness、報告契約、owner-facing surface

## 已驗證事實

- `CURRENT_STATUS.md` 已把 Agent Office v0.5、Telegram + Mobile Dashboard UX V1、Hermes controlled native install / cold path、dynamic workflow / cloud currency rule 寫成現況。
- `CURRENT_STATUS.md` 同時明講 `OpenClaw pg macmini` 尚未完成 Telegram -> 遠端 Mac / Chrome / Finder / NotebookLM 的端到端驗收。
- `CURRENT_STATUS.md` 也明講 `gooaye_batches -> NotebookLM` 不能直接做 bulk，現在只適合小任務驗證。
- `CURRENT_STATUS.md` 裡的 `scripts/run_convergence_engine.py` / shadow review hook v1.1 仍有 runtime copy parity 問題，repo fix 已出、runtime 還沒完全跟上。
- `workbook/task_index.json` 仍有 30 個任務，分類明顯偏 legacy backlog：`QUOTE` 12、`SEO` 12、`OPS` 4，狀態也混有完成、待開始、進行中、阻塞、暫停。
- `pitfalls.md` 已反覆收錄「stale surface / parallel write / reviewer_error 仍需寫 ledger」這類教訓，表示系統的痛點不是沒有規則，而是還在清理邊界。

## 合理推論

- 核心資料流其實已經收斂出一條穩定主線：GitHub HEAD / current status / task card / review bundle / owner-visible surface。
- 目前不是「核心過度建置」，而是「邊緣路徑過度擴張」：多個半完成的路徑、面板、同步層、研究入口同時存在。
- 真正需要保留的是可回放、可驗證、可交班的 surfaces；需要暫停的是看起來很完整、但還不能端到端證明的 surface。

## Continue

- `Agent Office v0.5`：維持單一 switchboard，讓 Owner 找得到入口，不要再另起一個平行面板。
- `Telegram + Mobile Dashboard UX V1`：保留第一屏與手機入口，這是 Owner 真正會看的 surface。
- `B1-B4` 角色分工與 summon map：保留，但只保留已驗證、會接棒的最小集合。
- `dynamic workflow / cloud currency rule`：保留為真相規則，所有 cloud mirror 都應視為 GitHub HEAD 的派生件。

## Pause

- `OpenClaw pg macmini` 的全面代操想像：目前只能當 bounded smoke / bounded bridge，不能當完整 Owner 替身。
- `gooaye_batches -> NotebookLM` 的 bulk 路徑：現在仍是小任務驗證，不適合直接擴成批次流水線。
- 任何會新增第二個、第三個 owner-facing 面板的擴充：先停，不要把「看起來很完整」誤認成「真的可用」。
- 任何尚未驗證 runtime parity 的 repo fix 直接視為已上線：先 pause，等 runtime copy 跟上再放行。

## Refactor

- 把 `CURRENT_STATUS.md` 收斂成 active-now / parked / archive 三層，不要把歷史與現況混在同一段。
- 把 `workbook/task_index.json` 裡的 legacy quote / SEO backlog 區分成 active、paused、archive，避免 active queue 被舊工作淹沒。
- 把 cloud share/export / manual copy 明確標成 derived artifact，不再假設它們和 GitHub HEAD 同一層。
- 把 review bundle、task card、relation graph 變成固定交班鏈，避免口頭交辦取代檔案交班。

## 下一步

- B1：處理 runtime parity 與同步路徑，讓 repo fix 真的進到 runtime copy。
- B3：整理 legacy backlog 與 archive 面，將暫停項目移出 active queue。
- A1：若 task module markdown 有變更，重建 module，再讓 review bundle 回到可召喚狀態。
