# AI Workbook Core MVP v0.1

Purpose: local, model-agnostic task-closure engine for MAPLAB.

## Scope (Phase 1)
- Read GitHub truth-source files
- Parse task cards into structured index
- Build per-task context pack
- Generate microtask templates
- Build relation graph
- Produce photo classification plan (proposal only)

## Commands
```bash
python3 tools/ai_workbook/cli.py index
python3 tools/ai_workbook/cli.py context T-A6-001
python3 tools/ai_workbook/cli.py microtask T-A6-001 --goal "重啟 bot 後做實機對話測試與群組操作驗證"
python3 tools/ai_workbook/cli.py graph
python3 tools/ai_workbook/cli.py infer
python3 tools/ai_workbook/cli.py photo-plan
python3 tools/ai_workbook/cli.py asset-snapshot
python3 tools/ai_workbook/cli.py dashboard
```

## Runtime Policy
- Default: `ollama`
- Escalate to `gemini-2.5-flash-lite` when confidence < 0.78 or cross-file reasoning is needed
- If still unstable, manual A1 review required

## Environment
- Optional for Ollama: `OLLAMA_MODEL` (default `llama3.1:latest`)
- Optional for Gemini: `GEMINI_API_KEY` (free-tier compatible model: `gemini-2.5-flash-lite`)

## Writeback Boundaries
- Writes only to `workbook/*` outputs
- Does **not** auto-modify `CURRENT_STATUS.md` or task cards

## Clickable Entry
After running `dashboard`, open:

- `workbook/dashboard.html`

## A4 Photo Source
The A4 photo pipeline source of truth is:

- `MAPLAB_ASSET_LOG`
- Spreadsheet ID: `1nlxlMdaLdGEAmOjP70BYspRWqu_eYpsiRyZaujEZkYI`
- Sheet tab: `工作表1`
- Drive archive root: `MAPLAB_ASSETS`

`photo-plan` is only for local temporary photo folders. Use `asset-snapshot` for the real A4 Sheet state.
