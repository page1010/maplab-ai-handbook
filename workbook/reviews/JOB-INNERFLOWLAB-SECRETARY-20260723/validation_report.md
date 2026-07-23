# Validation Report

## Local

- `python3 -m unittest -v tests/test_innerflowlab_personal_secretary_snapshot.py`
  — 5 tests passed.
- `python3 -m py_compile tools/innerflowlab_personal_secretary_snapshot.py`
  — passed.
- `git diff --check` — passed.
- Snapshot: 31 roles and 16 IOS functions.

## Live WordPress

- Logged-in UI: generated at `2026-07-23T13:07:22+08:00`, 31 roles, 16
  functions, IOS-ALPHA visible.
- Role cards: stale task-module hashes render as standby plus context
  maintenance evidence; they no longer render as runtime warning.
- Anonymous page request: HTTP 302 to `/wp-login.php`.
- Private page headers: `X-Robots-Tag: noindex, nofollow, noarchive` and
  `Cache-Control: no-store, private`.
- Anonymous `GET /wp-json/innerflowlab-secretary/v1/snapshot`: HTTP 401.
- Eye proof: `portal-ios-alpha-v03.png`.

## IOS-ALPHA evidence

- `com.investmentos.convergence-engine`: last exit 0.
- `com.investmentos.market-event-watch`: last exit 0.
- `data/convergence_phone.md`: 36 days stale at export time.
- `data/convergence_shadow_training.jsonl`: missing.
- Verdict: code and scheduled entry points are available; the data product
  must remain degraded until a fresh verified run completes.
