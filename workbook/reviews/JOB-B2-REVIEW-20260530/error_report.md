# JOB-B2-REVIEW-20260530 Error Report

日期：2026-05-30
角色：B2 Investment OS Reviewer

## 已驗證事實

- repo fix 與 runtime copy parity 仍未完全一致，尤其是 convergence / shadow review 這條鏈。
- `OpenClaw pg macmini` 尚未端到端驗證，不應被視為完整替代 Owner 的 dispatch surface。
- `gooaye_batches -> NotebookLM` 仍只能做小任務，不應被推成 bulk pipeline。
- `workbook/task_index.json` 的 backlog 結構仍混有大量 legacy quote / SEO work，容易把 active queue 拉歪。
- `pitfalls.md` 已經記錄過 parallel write、stale surface、reviewer_error ledger 等問題，表示同類錯誤不是孤例。

## 錯誤清單

| ID | 觸發條件 | 根因 | 影響 | 判定 | 建議處置 |
|---|---|---|---|---|---|
| E-01 | repo 已修，但 runtime 仍跑舊 copy | scoped sync / parity 沒完成 | 下一次自然執行可能仍用舊行為 | Pause | 先同步 runtime copy，再做 checksum / smoke |
| E-02 | cloud mirror / share / export 看起來像新版，但和 HEAD 不一致 | 把派生件當真相源 | Owner 看到的不是最新版 | Refactor | GitHub HEAD 唯一真相，cloud 全部當派生件 |
| E-03 | 想把 OpenClaw 直接推成全能代操 | 還沒完成端到端驗證 | 假性成熟、風險外溢 | Pause | 僅保留 bounded smoke / bounded bridge |
| E-04 | 想把 NotebookLM / gooaye 批次化 | 小任務驗證尚未通過 | 低可觀測、低穩定的批次失控 | Pause | 先保留小任務驗證，不做 bulk |
| E-05 | backlog 仍被 legacy quote / SEO 任務稀釋 | active / paused / archive 未分層 | Attention 被舊任務消耗 | Refactor | 先整理 task_index 與 task card 分層 |
| E-06 | 複數寫入同一 ledger / command center board | 多 writer 並行寫同一板 | 記錄競態、狀態漂移 | Block | 單 writer、序列化寫入、每次只改一條主線 |

## 失敗條件

- 如果 runtime parity 已完成，E-01 會降級成已解。
- 如果 backlog 已拆成 active / paused / archive，E-05 會降級成治理完成。
- 如果 OpenClaw 端到端驗收成功，E-03 才能從 pause 轉 continue。

## 下一步

- 先解 E-01，這是最直接影響自然執行的問題。
- 再解 E-05，否則 review / task / status 會持續互相污染。
- E-03 / E-04 先維持 pause，不要用補功能來掩蓋驗證缺口。
