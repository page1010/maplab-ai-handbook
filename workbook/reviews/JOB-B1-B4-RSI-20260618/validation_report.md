# Validation Report — B1-B4 Recursive Self-Improvement v0

## Commands

```bash
python3 -m py_compile tools/invest_os/b_role_recursive_self_improvement.py
python3 tools/invest_os/b_role_recursive_self_improvement.py --repo-root /Users/pagemacmini/maplab-ai-handbook --output-dir workbook/reviews/JOB-B1-B4-RSI-20260618
python3 -m json.tool workbook/reviews/JOB-B1-B4-RSI-20260618/b_role_recursive_self_improvement.json
```

## Result

- Python compile: pass.
- Scorer run: pass.
- JSON validation: pass.

## Baseline

- Overall score: `44`
- Band: `broken`
- Trend: `baseline`
- Role scores:
  - B1: `90`
  - B2: `56`
  - B3: `65`
  - B4: `65`

## Main Penalties

- Nightwatch red alert: Hermes 投資問題包過期 `730h`.
- Background job state: `live-position-session-refresh` failed with SQLite `database is locked`.
- Local-model shadow review: `82` concerns in the last 24h, currently untriaged by B2.
- B2/B3/B4 review bundles are about `440h` old.

## Interpretation

This is not a failure verdict on the role system. It is the first baseline. The next iteration must improve one of these:

- Fewer nightwatch red alerts.
- Fewer untriaged shadow concerns.
- Fresh B2/B3/B4 receipts.
- Clear B4 pause/refactor decision if the loop should not continue.

## Known Limits

- v0 is file-backed only and does not call `launchctl`.
- v0 does not write into `/Users/pagemacmini/Documents/New project`.
- v0 ignores smoke/canary jobs such as `timeout-smoke` so they do not pollute B1 repair priority.
