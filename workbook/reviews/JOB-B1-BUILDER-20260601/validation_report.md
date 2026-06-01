# Validation Report

## Investment OS Runtime Freshness

Verified runtime DB freshness after repair:

- `chip_market_daily`: `2026-06-01`
- `market_chip_daily`: `2026-06-01`
- `positions`: `2026-06-01T13:04:15.982987+00:00`
- `account_snapshots`: `2026-06-01T13:04:14.205000+00:00`
- `stock_future_opening_playbooks`: `2026-06-01`
- `market_rule_snapshots`: `2026-06-01`
- `research_model_outputs`: `2026-06-01`

## Dashboard Surface Readback

- `18501`: Browser readback shows `行情日 2026-06-01`, `AI研究日 2026-06-01`, `Agent板 06/01 21:08`, stale top-strip dates `0`.
- `18502`: headless readback shows same fresh badges, stale top-strip dates `0`.
- `8501`: headless readback shows same fresh badges, stale top-strip dates `0`.

Screenshots are stored in Investment OS:

- `reviews/DASHBOARD-RUNTIME-FRESHNESS-20260601/dashboard_18501_final.png`
- `reviews/DASHBOARD-RUNTIME-FRESHNESS-20260601/dashboard_18502_final.png`
- `reviews/DASHBOARD-RUNTIME-FRESHNESS-20260601/dashboard_8501_final.png`

## Test Commands

```bash
rtk proxy bash -n scripts/launch_dashboard.sh
rtk proxy plutil -lint launchd/com.investmentos.dashboard.plist launchd/com.investmentos.dashboard-mobile.plist launchd/com.investmentos.dashboard-local.plist
rtk proxy .venv/bin/python -m py_compile app/dashboard/streamlit_app.py scripts/run_invest_os_background_job.py scripts/run_stock_chip_refresh.py scripts/run_live_position_session_refresh.py scripts/agent_command_center.py
rtk proxy .venv/bin/python -m pytest -q tests/test_launchd_schedules.py tests/test_background_job_runner.py tests/test_market_data_refresh_runner.py tests/test_agent_command_center.py
```

Result: `23 passed in 0.33s`.

## Safety Result

- No secrets read.
- No order or broker state mutation.
- No Telegram send.
- No WordPress/Ads/Rank Math changes.
