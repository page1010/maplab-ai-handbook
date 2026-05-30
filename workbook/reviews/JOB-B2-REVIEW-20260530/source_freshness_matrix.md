# JOB-B2-REVIEW-20260530 Source Freshness Matrix

日期：2026-05-30
角色：B2 Investment OS Reviewer

## 判讀原則

- Live runtime / owner-visible evidence > repo note > historical bundle > memory.
- GitHub HEAD / canonical repo 是雲端最新版的唯一真相源；share / export / mirror 都只能算派生件。
- `TASK_QUEUE.md` 若缺失，改看 `workbook/task_index.json`，不要把舊路徑硬當真。

## Freshness Matrix

| Source | Freshness | 用途 | 風險 | 結論 |
|---|---|---|---|---|
| `/Users/pagemacmini/Documents/New project/CURRENT_STATUS.md` | High，但含歷史段落 | Investment OS 現況、active / paused / blocker | 不能把歷史條目當 live fact | 可用，但要分段讀 |
| `/Users/pagemacmini/Documents/New project/pitfalls.md` | High for lessons, not facts | 重複錯誤與預防規則 | 容易被誤讀成現況 | 可作 guardrail，不作現況 |
| `/Users/pagemacmini/maplab-ai-handbook/CURRENT_STATUS.md` | High for MAPLAB governance | MAPLAB canonical state、role routing | 不代表 runtime 已同步 | 可用，但仍需 runtime / bundle 驗證 |
| `/Users/pagemacmini/maplab-ai-handbook/pitfalls.md` | High for governance memory | 已踩過的系統錯誤 | 若直接套用會忽略當前上下文 | 可用作規則，不可當 live fact |
| `/Users/pagemacmini/maplab-ai-handbook/workbook/task_index.json` | Medium-High | 任務池結構、active / blocked / paused 混雜程度 | 內容仍混有 legacy backlog | 可用來判讀過度建置程度 |
| `/Users/pagemacmini/maplab-ai-handbook/projects/b2-invest-os-reviewer.md` | High | B2 role contract | 幾乎無 | 可靠，作角色規格 |
| `/Users/pagemacmini/maplab-ai-handbook/projects/b4-invest-os-system-patrol.md` | High | continue / pause / refactor / archive 決策框架 | 無 | 可靠，作巡查規格 |
| `/Users/pagemacmini/maplab-ai-handbook/docs/openclaw/output-contract.md` | High | 交班輸出契約 | 無 | 可靠，作 bundle 格式依據 |
| `/Users/pagemacmini/maplab-ai-handbook/docs/openclaw/relation-graph.md` | High | relation graph / task-output linkage | 無 | 可靠，作繫結依據 |
| `/Users/pagemacmini/maplab-ai-handbook/docs/openclaw/security-boundaries.md` | High | 不越權、不碰 secrets、不亂寫外部系統 | 無 | 可靠，作風險邊界 |
| `TASK_QUEUE.md` | Missing | 舊任務入口 | 已被 workbook/task_index.json 取代 | 不可再當主入口 |

## 已驗證的新鮮度結論

- 對 Investment OS 來說，`CURRENT_STATUS.md` 是現況主檔，但它不是 runtime 本體。
- 對 MAPLAB 來說，`CURRENT_STATUS.md` + `task_index.json` + review bundle 是可交班的最小真相鏈。
- 對 overbuild 判斷來說，`task_index.json` 的 legacy 比例偏高，這是「邊緣擴張過多」的直接信號。

## 缺資料

- 未在本次 review 中驗證實際 runtime copy 的檔案雜湊，只能從 status note 判讀 parity 問題仍存在。
- 未進一步抽查所有 legacy quote / SEO 任務的個別內容，因此無法直接判定每一條都該 archive，只有整體結構已偏重的結論。
