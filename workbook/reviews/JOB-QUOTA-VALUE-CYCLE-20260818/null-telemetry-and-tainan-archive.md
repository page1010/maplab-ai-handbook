# Quota Value Cycle — Null Telemetry Repair and Tainan Archive

## What

- Updated `collect_rate_limits` so an explicit `rate_limits: null` row is
  treated as absent telemetry and cannot crash the quota gate.
- Added a regression proving a nullable row is skipped and a later valid Codex
  snapshot remains usable.
- Added a regression proving `archived_candidates` are outside the eligible
  job pool.
- Moved `tainan-playable-slice-v0` from active candidates into a reversible
  `owner_sealed` archive entry.

## So What

The Investment OS quota sprint can now read fresh quota telemetry instead of
failing before job selection. The sealed Tainan project is no longer a
selectable quota job, including for a future `--project all` plan.

## Verification

- `/usr/bin/python3 local_model_evolution/tests/test_quota_value_cycle.py`:
  `10/10` passed.
- Live `snapshot`: available, `26%` used, `74%` remaining, reset
  `2026-08-20T12:00:41+08:00`.
- Live `plan --project investment-os`: healthy `blocked` with
  `outside_activation_window` at approximately `45.8` hours before reset; it
  no longer crashes.
- Live `plan --project tainan-game`: healthy `blocked` at the same time gate;
  unit coverage proves the archived candidate is outside selection.

## Now What

When the existing 36-hour activation window opens, select the highest-value
Investment OS candidate and close one material implementation／test／receipt
loop. Keep Tainan sealed until explicit Owner unseal.
