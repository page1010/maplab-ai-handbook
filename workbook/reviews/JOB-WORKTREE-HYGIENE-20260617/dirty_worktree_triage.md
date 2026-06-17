# Dirty Worktree Triage

Date: 2026-06-17
Role: Codex / A1-style system hygiene
Scope: current `/Users/pagemacmini/maplab-ai-handbook` working tree

## User Goal Checked First

The Owner request is not "make git clean by throwing things away." The goal is:

1. identify what user need each change was trying to satisfy,
2. keep and strengthen usable work,
3. mark unusable or superseded work as archived/superseded,
4. stop the system from repeatedly generating the same dirty-worktree problem.

This matches `docs/company-values.md` section 6.

## Why This Keeps Happening

1. Runtime logs were tracked source files. `scripts/cleanup-worktrees.sh` appended every 30 minutes to `logs/worktree-cleanup.log`, and launchd wrote to `logs/worktree-cleanup-launchd.log`. `scripts/patrol-scheduled.sh` appended to `logs/patrol-scheduled.log`. Because these files were tracked, normal scheduled governance created dirty git state.
2. Cleanup automation only cleaned extra `.claude/worktrees`. It explicitly skips dirty worktrees and never triages the main worktree. It prevents one class of stale worktree, not current-repo artifact drift.
3. `scripts/checkpoint.sh` still has a branch path that runs `git add -A`. If the tree already contains unrelated changes, a checkpoint can accidentally mix feature work, generated logs, and runtime files.
4. Several agents write generated artifacts directly into repo folders: `workbook/reviews`, `workbook/hermes/patrol/latest.*`, `workbook/task_modules/*`, `logs/*`, Python `__pycache__`, and A6 conversation/photo state. Some are durable artifacts; others are runtime dumps. The policy was written, but not enforced.
5. IOS-HYGIENE exists as a role owner for dirty worktree and keep/drop decisions, but the role is not invoked as a mandatory session-close gate.

## Actions Taken This Turn

Runtime noise now stops being version truth:

- `.gitignore` now ignores runtime logs, `logs/runtime/`, Python cache, A6 photo intake, and local photo DBs.
- `scripts/cleanup-worktrees.sh` now writes its log to `logs/runtime/worktree-cleanup.log`.
- `scripts/com.maplab.cleanup-worktrees.plist` now sends launchd stdout/stderr to `logs/runtime/worktree-cleanup-launchd.log`.
- `scripts/patrol-scheduled.sh` now writes `patrol-scheduled.log` under `logs/runtime/`.
- `scripts/open_agent_runtime_panel.sh` reads the new patrol log path and falls back to the old path.
- Previously tracked runtime files were removed from the git index with `git rm --cached` and left on disk.
- A8 superseded local runs are marked in `workbook/reviews/JOB-A8-FOLDER-TO-SHORTS-20260617/SUPERSEDED_RUNS.md` and job-local `.gitignore`.

Validation performed:

- `bash -n scripts/cleanup-worktrees.sh scripts/patrol-scheduled.sh scripts/open_agent_runtime_panel.sh`
- `python3` py_compile for A6/A5 quote engine, role-module builder, and Lottie validator
- `node --check chrome-extension/popup.js`
- `node --check local-control-plane/panel.js`
- `node --check local-control-plane/hermes_status.js`
- Lottie smoke validator returned `ok=true`
- A6 quote deterministic fallback returned `action=createQuoteVariants`
- A6 route check passed when using `bot/venv/bin/python`
- JSON parse check passed for task modules, Hermes status, and relation graph files

## Current Keep / Drop Classification

### Keep and commit after focused review

- A6/A5 local quote fallback:
  - User need: competitor menu screenshot or OCR -> MAPLAB similar items -> cost * 5 -> Sheet payload.
  - Evidence: Python compile passed; deterministic fallback produced `createQuoteVariants`; route check passed in venv.
  - Caveat: `bot_a6/conv_history_a6.json` is runtime history and should not be committed.

- Lottie skill and validator:
  - User need: define a reusable skill for Lottie / motion JSON generation with validation.
  - Evidence: `tools/lottie_validate.py` compiles; smoke file validates `ok=true`.

- Photo sourcing and WordPress article standard skills:
  - User need: A2/A4 article image sourcing and WP edit rules.
  - Evidence: documents are coherent; no live WP write was performed in this turn.

### Keep as WIP, repair before commit

- Extension role modules with Hermes target:
  - User need: Chrome Extension is the role-summon channel; Hermes/OpenClaw need to be available as handoff targets.
  - Evidence: JSON parse passed; popup JS syntax passed.
  - Problem: generated docs/task card text regressed to `Gemini / Codex / OpenClaw` while the generated JSON adds `hermes`. Repair generator copy before committing.

- Hermes patrol reaction/panel:
  - User need: daily patrol should become a reaction loop, not repeated Telegram delivery.
  - Evidence: panel JS syntax passed; packet files are structured JSON/MD.
  - Problem: current generated packet says Hermes status is `unknown` even though later live Hermes checks existed. Regenerate from current truth before committing.

- IOS-KOL industry brief bundle:
  - User need: preserve multi-layer KOL / industry brief outputs.
  - Evidence: generated scripts/docs/rendered files exist.
  - Problem: needs a content/owner-facing review before commit because it contains many deliverables.

### Superseded / local-only

- A8 local fallback/video runs before v5:
  - User need: train local model as fallback that can produce real MP4, not only JSON.
  - Current usable artifact: `local_model_video_v5/` already committed.
  - Disposition: earlier `local_model_fallback_v2-v5` and `local_model_video_v1-v4` are local-only superseded evidence and are ignored by job-local `.gitignore`.

- Logs, pycache, A6 conversation history, A6 intake photos, local photo DBs:
  - User need: runtime operation, debugging, or private local state.
  - Disposition: local-only; removed from git tracking or ignored. They are not source truth.

## Required Next Gate

Before the next broad commit, run IOS-HYGIENE as a required gate:

1. `git status --porcelain=v1`
2. group files by user goal,
3. for each group record keep / WIP / superseded / local-only,
4. run the smallest validation,
5. commit only one coherent group at a time with the keep/drop note in the commit body.

Do not use `git add -A` while unrelated WIP is present.
