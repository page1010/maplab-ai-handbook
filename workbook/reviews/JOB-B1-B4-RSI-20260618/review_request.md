# Review Request — B1-B4 Recursive Self-Improvement v0

## Request

Review whether the new B1-B4 Recursive Self-Improvement loop creates a useful direction for gradual growth:

- Does it prevent raw local-model output from becoming formal fact?
- Does it force B2/B3/B4 to leave current receipts?
- Does it give B1 a clear boundary: fix confirmed red items, not add automation blindly?
- Does the baseline report make the next iteration measurable?

## Evidence

- `projects/invest-os-b-role-recursive-self-improvement.md`
- `tools/invest_os/b_role_recursive_self_improvement.py`
- `workbook/reviews/JOB-B1-B4-RSI-20260618/b_role_recursive_self_improvement.md`
- `workbook/reviews/JOB-B1-B4-RSI-20260618/b_role_recursive_self_improvement.json`

## Acceptance

Accept v0 if:

- The scorer is safe, file-backed, and does not touch broker/secrets.
- The role docs make B2/B3/B4 responsibilities explicit.
- The next run can compare against this baseline.

Reject or revise v0 if:

- The score encourages adding more automation before B2/B4 classification.
- The score over-penalizes harmless canaries or under-penalizes owner-visible drift.
- The output is not understandable from the first screen.
