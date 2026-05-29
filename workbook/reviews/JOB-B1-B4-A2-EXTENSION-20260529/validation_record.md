# Validation Record

日期：2026-05-29

## Commands

```bash
python3 -m py_compile tools/ai_workbook/build_extension_task_modules.py tools/ai_workbook/relation_graph.py
node --check chrome-extension/popup.js
for f in chrome-extension/task-modules/index.json chrome-extension/task-modules/A2.json chrome-extension/task-modules/B1.json chrome-extension/task-modules/B2.json chrome-extension/task-modules/B3.json chrome-extension/task-modules/B4.json chrome-extension/config/task-modules.json workbook/task_modules/role_module_relation_graph.json; do python3 -m json.tool "$f" >/dev/null || exit 1; done
python3 tools/ai_workbook/build_extension_task_modules.py
git diff --check -- <scoped changed files>
python3 -m json.tool chrome-extension/manifest.json >/dev/null
realpath /Users/pagemacmini/Desktop/chrome-extension
```

## Results

- `py_compile`: pass.
- `node --check chrome-extension/popup.js`: pass.
- JSON validation for A2, B1-B4, index, config, relation graph: pass.
- Module generator: pass; generated 13 modules and 334 relationship rows.
- Expected missing source: `TASK_QUEUE.md`; generator falls back to `workbook/task_index.json`.
- Scoped `git diff --check`: pass.
- v5.6.0 follow-up validation: `node --check`, `py_compile`, manifest JSON, task module JSON, config JSON, relation graph JSON, and scoped `git diff --check` all pass.
- Desktop live extension path now resolves to `/Users/pagemacmini/maplab-ai-handbook/chrome-extension`; stale v4.7.0 folder was preserved as `/Users/pagemacmini/Desktop/chrome-extension.stale-v4.7-20260529-212125`.
- Chrome Extensions page shows MAPLAB Agent Commander `5.6.0` enabled with id `ifpmihhbfhpbcippnhdnjdecbgkmbgmf`; old `4.7.0` entry remains disabled and was not removed.
- Live popup smoke: `chrome-extension://ifpmihhbfhpbcippnhdnjdecbgkmbgmf/popup.html` shows `召喚任務`, `自動選角`, version `v5.6.0`, and `模組 13 已載入`.
- Live routing smoke: task `巡查 Investment OS 現在是否過度建置，列出該繼續、暫停、重構的項目。` suggested B4 and generated B4 handoff with `本次召喚任務`.
- Recall fallback smoke: B4 handoff includes the B4 recall summary from packaged module fallback instead of showing GitHub raw 404.

## Module Evidence

`chrome-extension/task-modules/index.json` includes:

- A2 `Ads SEO WordPress Patrol`
- B1 `Investment OS Builder`
- B2 `Investment OS Reviewer`
- B3 `Investment OS Archivist`
- B4 `Investment OS System Patrol`

## Note

Full `git diff --check` over the whole worktree still reports pre-existing trailing whitespace in dirty `logs/*` files. Those files were outside this task scope and were not modified or staged.
