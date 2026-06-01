# Review Request

## Requested Reviewer

B2 Reviewer or B4 System Patrol.

## Review Scope

Please review the Investment OS Dashboard freshness repair for:

- Correctness of LaunchAgent weekday mapping.
- Whether launchd-backed `18502` and `8501` should remain permanent owner-facing surfaces.
- Whether Dashboard command-board source priority should stay canonical repo first.
- Whether `stock-chip-refresh` should be patched later so its embedded live-readonly substep loads runtime env like the dedicated live-position wrapper.

## Evidence To Read

- Investment OS: `reviews/DASHBOARD-RUNTIME-FRESHNESS-20260601/validation_report.md`
- Investment OS: `pitfalls.md` error 169
- Investment OS: `tests/test_launchd_schedules.py`
- MAPLAB: `workbook/reviews/JOB-B1-BUILDER-20260601/validation_report.md`

## Safety Notes

This work did not read secrets, send Telegram, publish content, or touch broker orders.
