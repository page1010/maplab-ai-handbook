# A6 LINE OA Settings Snapshot — Validation Receipt

- Date: 2026-10-02 Asia/Taipei
- Status: `VERIFIED_LOCAL_DB_IMPORTED / LINE_UNCHANGED / AUTO_SEND_DISABLED`
- Source: Owner-authenticated Chrome LINE Chat settings, read-only observation
- Destination: `data/case-store/a6_case_store.sqlite3` (gitignored, mode `0600`)
- Payload digest: `1fc1eeacdd4465e053356325839a8f9a001e9e3362cf235b35f9a8345fe8a871`

## VERIFIED

- LINE tag page showed `16/300`; page 1 had 10 rows and page 2 had 6 rows.
- LINE saved-reply page showed `全部(28)`; three pages yielded 10 + 10 + 8 rows.
- Import result: snapshot `1`, tags `16`, saved replies `28`.
- Policy readback: `auto_send_count=0`, `human_review_count=28`, `financial_count=4`.
- Database file mode readback: `0600`.
- Chrome returned to the original chat URL after extraction; browser clipboard was restored.
- LINE create/edit/delete/send/enable actions: `0`.
- `python3 -m unittest tests.test_hermes_sheets_assistant tests.test_line_oa_settings_import`: `17 passed`.
- `python3 -m compileall -q bot_a6/case_store.py scripts/import_line_oa_settings.py tests/test_line_oa_settings_import.py`: pass.

## POLICY CLASSIFICATION

- `usage_scenario` is the Owner-authored LINE preset title, not a model-invented scenario.
- Every saved reply is `HISTORICAL_REFERENCE_REQUIRES_MINA_REVIEW`.
- No saved reply is eligible for automatic customer sending.
- Exact preset bodies, financial details, customer data, and chat content are excluded from this receipt and all tracked files.

## DRIFT / MISSING

- The snapshot is point-in-time evidence from 2026-10-02; later LINE changes do not update it automatically.
- Hermes runtime does not automatically retrieve or send these presets.
- Historical copy may conflict with the current one-question, neutral Sheets-intake contract; no per-template rewrite was authorized in this task.

## NEXT

No further action for this task. A future authorized iteration may add an offline catalog search plus contract-diff report, while keeping `allowed_for_auto_send=0` and private content local.

## Resume Prompt

Read `CURRENT_STATUS.md`, `pitfalls.md`, `handoff/tasks/T-A6-LINE-OA-SETTINGS-SNAPSHOT-001.md`, `docs/data-locations.md`, and `config/hermes-line-sheets-assistant-v1.json`. Treat the 16 tags and 28 saved replies as a local historical snapshot only. Do not expose raw bodies, financial details, or customer data; do not modify LINE or send any reply. If Owner requests follow-up, first run offline retrieval and contract-diff tests, then produce a new receipt.
