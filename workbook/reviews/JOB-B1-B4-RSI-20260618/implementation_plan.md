# Implementation Plan — B1-B4 Recursive Self-Improvement v0

日期：2026-06-18
角色：B1 Investment OS Builder

## Owner Request

Owner 要求把 B1-B4 「抓起來修」，不要只停在召喚型角色；希望它們進入 Recursive Self-Improvement（RSI），能看出每次迭代是否變強。

本輪依 Owner 校正，RSI 定義為 `Recursive Self-Improvement`。分數只是儀表板，不是 RSI 本體，也不是投資市場指標。

## Scope

- 新增 B1-B4 Recursive Self-Improvement 規格文件。
- 新增 file-backed scorer，從現有 runtime receipts 建 baseline。
- 更新 B1-B4 shared role system、B2/B3/B4 role docs、B1-B4 recall prompts、task card。
- 留下 baseline report 與下一輪 handoff。

## Non-Scope

- 不下單、不建立模擬單、不讀 broker state。
- 不讀 secrets、`.env`、API keys、cookies。
- 不修改 Investment OS runtime repo，v0 只讀 runtime receipts。
- 不把 local model raw finding 當正式結論。

## Design

B1-B4 的成長 loop：

1. B4 detect：讀 nightwatch、background job state、shadow findings、owner-facing receipts。
2. B2 classify/review：把 raw finding 分類成可驗證狀態。
3. B1 repair：只修最高槓桿、scope 清楚、可驗證的紅燈。
4. B3 archive：保存分數、修復、resume prompt、pitfall decision。
5. Next run compare：下一輪 scorer 必須看見分數提升、紅燈減少，或明確 pause/refactor。

## Acceptance Criteria

- `python3 -m py_compile tools/invest_os/b_role_recursive_self_improvement.py` passes.
- Scorer writes JSON and Markdown baseline.
- Baseline states the current score and why it is low.
- B2/B3/B4 docs define their Recursive Self-Improvement responsibilities.
- Task card resume prompt tells the next agent exactly how to continue.
