# Validation Report

## Completed

- `python3 tools/ai_workbook/build_extension_task_modules.py`
  - Result: pass.
  - Output: `modules=29`, `rows=590`.
  - Known missing source: `TASK_QUEUE.md`, existing fallback to
    `workbook/task_index.json`.
- `python3 -m json.tool chrome-extension/task-modules/index.json`
  - Result: pass.
- `python3 -m json.tool chrome-extension/task-modules/IOS-HYGIENE.json`
  - Result: pass.
- `PYTHONPYCACHEPREFIX=/private/tmp/maplab_pycache python3 -m py_compile tools/ai_workbook/build_extension_task_modules.py`
  - Result: pass.
- `node --check chrome-extension/popup.js`
  - Result: pass.
- `python3 -m json.tool chrome-extension/config/task-modules.json`
  - Result: pass.
- Batch parse `chrome-extension/task-modules/IOS-*.json`
  - Result: pass.
  - Count: 16 IOS modules.

## Pending

- Reload Chrome Extension from `chrome-extension/` after commit to confirm the
  side panel shows Investment OS / Strategy Owners in the dropdown.

## Dirty Worktree Note

MAPLAB already had unrelated dirty files and logs before this task. This job
only stages the files listed in `changed_files.md`.
