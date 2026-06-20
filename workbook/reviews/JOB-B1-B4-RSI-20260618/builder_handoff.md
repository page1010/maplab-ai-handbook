# Builder Handoff — B1-B4 Recursive Self-Improvement v0

## Current State

B1-B4 now have a Recursive Self-Improvement v0 loop:

- Spec: `projects/invest-os-b-role-recursive-self-improvement.md`
- Scorer: `tools/invest_os/b_role_recursive_self_improvement.py`
- Baseline: `workbook/reviews/JOB-B1-B4-RSI-20260618/b_role_recursive_self_improvement.md`

Baseline score is `44` (`broken`). The score dropped because the scorer read the latest runtime state: `live-position-session-refresh` is now failed, B2/B3/B4 receipts are stale, and raw local-model concerns are not being triaged into decisions.

## Next Work

1. B2 should open a review bundle and classify the latest `convergence-engine` shadow concerns:
   - `accepted_issue`
   - `false_positive`
   - `needs_more_evidence`
   - `handed_to_b1`
   - `archived_by_b3`
2. B3 should archive this Recursive Self-Improvement baseline and make it a trend checkpoint.
3. B4 should decide whether Hermes 投資問題包 should continue, pause, refactor, or archive.
4. B1 should only implement after B2/B4 identify a concrete fix target.
5. Rerun scorer after the above; improvement requires score up, red items down, or a documented pause/refactor decision.

## Resume Prompt

我是 B1/Codex，接手 B1-B4 Recursive Self-Improvement loop。請先讀 `CURRENT_STATUS.md`、`pitfalls.md`、`projects/invest-os-b-role-system.md`、`projects/invest-os-b-role-recursive-self-improvement.md`、`handoff/tasks/T-B1-B4-investment-os-role-split.md`、`workbook/reviews/JOB-B1-B4-RSI-20260618/b_role_recursive_self_improvement.md`。本輪 baseline score 是 `44`，主要弱點是 Hermes 投資問題包過期、`live-position-session-refresh` database locked 失敗、82 筆 convergence-engine shadow concern 未分類、B2/B3/B4 receipts 過舊。下一步不要先加功能；先讓 B2 分類 raw finding、B3 保存 baseline、B4 決定 continue/pause/refactor，再由 B1 修被確認的最高槓桿紅燈。
