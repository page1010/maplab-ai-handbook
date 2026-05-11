# GitHub Sync Audit — 2026-05-11

Owner instruction: keep local work aligned with GitHub so the repo remains the backup and truth source.

## Remote State

- Repository: `page1010/maplab-ai-handbook`
- Local branch: `main`
- Remote branch: `origin/main`
- Verified synced head before this audit: `aa46c75`

## What Was Checked

- `git fetch origin`
- local `git status`
- local file inventory vs `origin/main`
- sensitive string scan over candidate files
- Python syntax check for new executable files

## Candidate Classification

### Commit to GitHub

These are durable source, governance, or review-index artifacts and should be backed up:

- `bot_a6/openclaw_dispatch.py`
- `docs/a4/README.md`
- `docs/a4/workflow.md`
- `docs/governance/verification-bundles.md`
- `docs/openclaw/*.md`
- `docs/system-evolution-stories/*.md`
- `handoff/tasks/T-B1-001.md`
- `local-control-plane/config/verification_bundles.json`
- `projects/codex-self-improving-core.md`
- `scripts/move_a4_assets_from_sheet.py`
- `tools/ai_workbook/openclaw_adapter.py`
- `workbook/outputs/2026-05-05/T-A4-photo-move/checkpoint.json`
- `workbook/outputs/2026-05-05/T-A4-photo-move/report.json`
- `workbook/reviews/README.md`
- `workbook/reviews/a6_local_bundle_index_2026-05-11.json`

### Hold Locally

These are runtime logs, secrets, or raw conversational bundles and should not be blindly committed:

- `.env` files
- bot logs
- `logs/*.log`
- `conv_history*.json`
- raw `workbook/reviews/JOB-A6-*` bundles until sanitized

## Sensitive Scan Result

Scan did not find obvious raw tokens in the commit candidates.

Expected false positives:

- Python code references `refresh_token` / `client_secret` field names while reading local OAuth token files.
- docs mention `client_secret` as a setup concept.

## Review Bundle Handling

Raw A6 review bundles are valuable but contain full prompts, terminal logs, and large model outputs.
Instead of committing them blindly, this audit adds a local bundle index:

`workbook/reviews/a6_local_bundle_index_2026-05-11.json`

Next step is to create sanitized summaries for the raw bundles before backing them up.

## Rule Going Forward

GitHub should hold durable source, docs, configs, task cards, sanitized evidence, and review indexes.
GitHub should not hold raw secrets, runtime logs, or unsanitized conversation dumps.
