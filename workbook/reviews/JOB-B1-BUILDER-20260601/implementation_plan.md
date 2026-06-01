# B1 Builder Implementation Plan — Investment OS Dashboard Freshness

## Task

Owner reported that the Investment OS Dashboard kept showing old data and lacked a real closed loop.

## Role Fit

This matches B1 Investment OS Builder because the task required repo/runtime wiring, dashboard surface repair, LaunchAgent schedule repair, validation artifacts, and cross-project handoff.

## Plan Executed

1. Read governance and role sources in MAPLAB and Investment OS.
2. Compare repo dashboard files against runtime dashboard files.
3. Inspect live dashboard ports, process ages, and LaunchAgent schedules.
4. Repair stale launcher behavior and incorrect Taiwan market weekday schedules.
5. Sync repaired files into the Investment OS runtime copy.
6. Reload dashboard and refresh missed runtime data jobs.
7. Run a real no-send browser-backed GPT refresh to update `research_model_outputs`.
8. Verify owner-facing surfaces on `18501`, `18502`, and `8501`.
9. Write back Investment OS status, pitfalls, validation bundle, and this MAPLAB B1 handoff bundle.

## Boundary

- No WordPress, Ads, Rank Math, publishing, broker order, or simulated order changes.
- No secrets or `.env` reads.
- Broker interaction was limited to existing Investment OS read-only snapshot refresh.
