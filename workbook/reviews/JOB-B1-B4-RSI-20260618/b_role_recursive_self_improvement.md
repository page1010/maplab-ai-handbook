# B1-B4 Recursive Self-Improvement

- Generated: `2026-06-18T16:25:42.471809+08:00`
- Overall score: `44`
- Band: `broken`
- Trend: `baseline`
- Previous score: `None`

> RSI here means Recursive Self-Improvement. The score is an instrument panel, not a market signal.

## Role Scores

| Role | Score |
|------|-------|
| B1 | 90 |
| B2 | 56 |
| B3 | 65 |
| B4 | 65 |

## Penalties

| Reason | Points | Count/Age |
|--------|--------|-----------|
| nightwatch_red_alerts | 12 | 1 |
| failed_or_timeout_background_jobs | 8 | 1 |
| untriaged_shadow_concerns_24h | 12 | 82 |
| b2_receipt_stale_or_missing | 8 | 439.96247900722227 |
| b3_receipt_stale_or_missing | 8 | 439.9624788025 |
| b4_receipt_stale_or_missing | 8 | 439.9624775344445 |

## Nightwatch Red Lines

- | Hermes 投資問題包 | 🔴 過期 | 730h 前(上限 200h)｜invest_question_pack_2026-05-18.md |
- - **Hermes 投資問題包**：730h 前(上限 200h)｜invest_question_pack_2026-05-18.md

## Failed Or Timeout Jobs

- `live-position-session-refresh`: failed — live_position_session_refresh failed: accounts=3 positions=1 position_snapshot=2026-06-18T05:50:40.343712+00:00 reason=sync_account_live_readonly=sqlite3.OperationalError: database is locked log=/Users/pagemacmini/.local/share/investmentos-

## Latest Shadow Concern

2026-06-18T16:18:12+08:00 / convergence-engine / concern: The matrix_rows array is empty, which indicates a lack of data to populate the table. This could be due to an error in the input or a deliberate decision not to include any data.

## Next Actions

- B4: treat nightwatch red lines as patrol inputs, not owner-facing conclusions.
- B2: triage latest shadow concerns into accepted_issue / false_positive / needs_more_evidence.
- B1: start with `live-position-session-refresh` because it is currently failed/timeout in background job state.
- B1: repair the highest-impact failed background job before adding new automation.
- B3: archive this run with a resume prompt and write pitfalls only if the same miss repeats.
- B4: rerun the scorer after fixes; require score improvement or fewer red items before calling the loop stronger.
