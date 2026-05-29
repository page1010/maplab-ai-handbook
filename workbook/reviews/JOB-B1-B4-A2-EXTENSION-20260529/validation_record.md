# Validation Record

日期：2026-05-29

## Commands

```bash
python3 -m py_compile tools/ai_workbook/build_extension_task_modules.py tools/ai_workbook/relation_graph.py
node --check chrome-extension/popup.js
for f in chrome-extension/task-modules/index.json chrome-extension/task-modules/A2.json chrome-extension/task-modules/B1.json chrome-extension/task-modules/B2.json chrome-extension/task-modules/B3.json chrome-extension/task-modules/B4.json chrome-extension/config/task-modules.json workbook/task_modules/role_module_relation_graph.json; do python3 -m json.tool "$f" >/dev/null || exit 1; done
python3 tools/ai_workbook/build_extension_task_modules.py
git diff --check -- <scoped changed files>
```

## Results

- `py_compile`: pass.
- `node --check chrome-extension/popup.js`: pass.
- JSON validation for A2, B1-B4, index, config, relation graph: pass.
- Module generator: pass; generated 13 modules and 334 relationship rows.
- Expected missing source: `TASK_QUEUE.md`; generator falls back to `workbook/task_index.json`.
- Scoped `git diff --check`: pass.

## Module Evidence

`chrome-extension/task-modules/index.json` includes:

- A2 `Ads SEO WordPress Patrol`
- B1 `Investment OS Builder`
- B2 `Investment OS Reviewer`
- B3 `Investment OS Archivist`
- B4 `Investment OS System Patrol`

## Note

Full `git diff --check` over the whole worktree still reports pre-existing trailing whitespace in dirty `logs/*` files. Those files were outside this task scope and were not modified or staged.
