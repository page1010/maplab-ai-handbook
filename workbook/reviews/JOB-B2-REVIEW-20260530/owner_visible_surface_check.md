# JOB-B2-REVIEW-20260530 Owner Visible Surface Check

日期：2026-05-30
角色：B2 Investment OS Reviewer

## 檢查準則

- Owner 第一屏要能看懂、能動作、能追溯。
- 真正的 owner-facing surface 只保留少數固定入口，不要讓 worker surface 假裝成主人入口。
- 若 surface 還沒完成端到端驗證，就不要把它當作「已可用」。

## Surface Matrix

| Surface | Owner 可見性 | 第一屏可讀 | Freshness | 是否適合繼續 | 註記 |
|---|---|---:|---:|---|---|
| Telegram 手機入口 | Yes | Yes | High | Continue | 這是最重要的 owner-facing bell |
| Dashboard | Yes | Yes | High | Continue | 作為可掃描的日常視圖，保留 |
| Agent Office switchboard | Yes | Yes | High | Continue | 只保留單一入口，不再分裂成多個平行面板 |
| Review bundle / task card | Yes, 但偏治理層 | Yes | High | Continue | 這是交班證據，不是行動主畫面 |
| `OpenClaw pg macmini` | 部分可見 | 未完全證明 | Medium | Pause | 不能假設已可替代 Owner 代操 |
| `gooaye_batches -> NotebookLM` bulk path | 否 | 否 | Low-Medium | Pause | 先小任務驗證，不進 bulk |
| 新增的臨時 panel / side surface | 可能可見 | 不一定 | 不穩定 | Refactor | 容易讓 Owner 看到多個版本的自己 |

## 已驗證事實

- `CURRENT_STATUS.md` 已把 Agent Office、Telegram、Dashboard、Hermes 等入口列為現行路線。
- `CURRENT_STATUS.md` 也同時承認 OpenClaw 與 NotebookLM bulk 路徑還沒完成端到端驗證。
- `workbook/task_index.json` 的 backlog 結構顯示系統還有不少舊路徑與舊題材，Owner surface 不能再無限加。

## 建議

- 保留三個核心 owner-facing surface：Telegram、Dashboard、Agent Office。
- 把 review bundle / task card 當作治理與交班 surface，而不是日常操作 surface。
- 其他 worker surface 先維持 worker-only，直到驗證完成再升格。
