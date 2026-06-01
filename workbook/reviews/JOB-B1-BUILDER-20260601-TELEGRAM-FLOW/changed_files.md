# Changed Files

## Investment OS Repo

- `/Users/pagemacmini/Documents/New project/scripts/run_convergence_engine.py`
  - Added `build_convergence_telegram_card`.
  - Reused matrix summary helpers for report and phone card.
  - Kept full matrix, Trump/GPT prompt paths, and shadow-training details in the
    file-backed report/review surfaces.
  - Changed Telegram send for `--source all` to send the short card instead of
    the full markdown report.

- `/Users/pagemacmini/Documents/New project/tests/test_convergence_engine.py`
  - Added regression coverage that the Telegram card is short, research-only,
    file-backed, and does not include full matrix or prompt-path handles.

- `/Users/pagemacmini/Documents/New project/CURRENT_STATUS.md`
  - Added 2026-06-01 21:12 live-result note for the Convergence Telegram
    short-card fix and safety/validation state.

- `/Users/pagemacmini/Documents/New project/tasks/TELEGRAM_SEND_PATH_CONTROL_PLANE_20260529.md`
  - Added the Telegram Web readback observation and the B1 implementation result.
  - Preserved global P0 gateway metadata/allowlist as still open.

- `/Users/pagemacmini/Documents/New project/tasks/CONVERGENCE_SHADOW_TRAINING_TELEGRAM_20260528.md`
  - Added the regression fix, validation, and next live-readback requirement.

- `/Users/pagemacmini/.local/share/investmentos-telegram-operator/scripts/run_convergence_engine.py`
  - Scoped runtime sync after verifying the runtime diff matched the repo change.

## MAPLAB Handbook Repo

- `/Users/pagemacmini/maplab-ai-handbook/workbook/reviews/JOB-B1-BUILDER-20260601-TELEGRAM-FLOW/implementation_plan.md`
- `/Users/pagemacmini/maplab-ai-handbook/workbook/reviews/JOB-B1-BUILDER-20260601-TELEGRAM-FLOW/changed_files.md`
- `/Users/pagemacmini/maplab-ai-handbook/workbook/reviews/JOB-B1-BUILDER-20260601-TELEGRAM-FLOW/validation_report.md`
- `/Users/pagemacmini/maplab-ai-handbook/workbook/reviews/JOB-B1-BUILDER-20260601-TELEGRAM-FLOW/builder_handoff.md`
- `/Users/pagemacmini/maplab-ai-handbook/workbook/reviews/JOB-B1-BUILDER-20260601-TELEGRAM-FLOW/review_request.md`

## Existing Dirty Files

Both repos had unrelated pre-existing dirty/untracked files. This pass did not
revert or modify unrelated runtime logs, A6 files, or historical review bundles.

