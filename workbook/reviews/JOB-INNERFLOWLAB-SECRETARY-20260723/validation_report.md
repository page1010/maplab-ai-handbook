# Validation Report

## Local

- `python3 -m unittest -v tests/test_dynamic_role_modules.py tests/test_innerflowlab_personal_secretary_snapshot.py`
  — 7 tests passed.
- `python3 -m py_compile tools/ai_workbook/build_extension_task_modules.py tools/innerflowlab_personal_secretary_snapshot.py`
  — passed.
- Codex artifact-tool rebuilt `role_module_relationships.xlsx` from the
  canonical CSV: 678 relationship rows, 4 summary formulas, and 1 filterable
  relationship table. Summary render passed visual inspection.
- Excel summary formulas returned 678 relationship rows, 3 intentionally
  missing restricted/runtime sources, 316 high-risk rows, and 16 restricted
  references with no formula error.
- `zsh -n` for both sync scripts — passed.
- `plutil -lint launchd/com.maplab.innerflowlab-personal-secretary-sync.plist`
  — passed.
- Missing-Keychain and non-canonical installer drills — both fail closed with
  exit 78.
- `git diff --check` — passed.
- Dynamic module catalog: 32 modules, including B5; snapshot: 31 portal roles
  and 16 IOS functions.

## Live WordPress

- Logged-in UI: generated at `2026-07-23T13:19:34+08:00`, 31 roles, 16
  functions, IOS-ALPHA visible.
- Role cards: 1 running, 30 standby, 0 warning; stale-hash alert absent.
- Anonymous page request: HTTP 302 to `/wp-login.php`.
- Private page headers: `X-Robots-Tag: noindex, nofollow, noarchive` and
  `Cache-Control: no-store, private`.
- Anonymous `GET /wp-json/innerflowlab-secretary/v1/snapshot`: HTTP 401.
- Eye proof: `portal-summary-v05.png` and `portal-ios-alpha-ready-v05.png`.

## IOS-ALPHA evidence

- `com.investmentos.convergence-engine`: last exit 0.
- `com.investmentos.market-event-watch`: last exit 0.
- Runtime `data/convergence_phone.md`: updated 2026-07-23 13:03 +0800.
- Runtime `data/convergence_shadow_training.jsonl`: present and current.
- Runtime `reports/shadow/local_model_findings.jsonl`: present and current.
- Repo/runtime convergence and background-job runner SHA-256: exact match.
- Verdict: IOS-ALPHA is READY; the current cycle produced no valid
  cross-source signal, which correctly means observe rather than trade.
