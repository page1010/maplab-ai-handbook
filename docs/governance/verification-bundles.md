# Verification Bundles

This document defines the fixed evidence contract for Codex self-verification and external review.

## Roles

- Codex: execute the task, verify the visible result, and emit the evidence bundle.
- A1 / governance: review the bundle, compare expected vs observed state, and decide whether the task is truly closed.
- Owner: approve business-side closure or request another iteration.

## Why this exists

The goal is not "Codex saw the screen".
The goal is "Codex produced evidence that the work is closed, reproducible, and reviewable."

Every completed task must leave a bundle that answers:

1. What was changed?
2. What was observed?
3. What proof exists?
4. What writeback happened?
5. What remains open, if anything?

## Required bundle files

Each job should write into:

`workbook/reviews/JOB-YYYY-MM-DD-XXX/`

Recommended contents:

- `execution_log.json`
- `output_manifest.json`
- `verification_log.json`
- `sheet_diff.json`
- `audit_log.json`
- `review_request.md`
- `diff.md`
- `screenshots/`

## Fixed verification sets

### Dashboard task

Use this checklist when the task is about the Flow Dashboard:

1. `npm run dev` starts successfully.
2. Dashboard renders task or flow nodes.
3. Clicking a task node opens a detail panel with data.
4. Link targets open GitHub, local file, or Google Sheet correctly.
5. Agent and status filters react.
6. `T-A6-001` is visible in the graph.
7. Save a screenshot to `workbook/reviews/JOB-xxx/screenshots/dashboard.png`.

### Sheet Writer task

Use this checklist when the task writes to Google Sheets:

1. `quote_intake.json` passes validation.
2. The correct sheet tab receives the append.
3. The response includes `row_number` and `range`.
4. The row is visible in Google Sheets.
5. Save `audit_log.json`.
6. Save `sheet_diff.json`.
7. Save a screenshot to `workbook/reviews/JOB-xxx/screenshots/sheet_row.png`.

### WordPress / SEO task

Use this checklist when the task writes or prepares WordPress content:

1. The draft exists in WordPress.
2. `title`, `slug`, and `meta description` are correct.
3. H1 / H2 structure is correct.
4. Internal links are present.
5. Nothing is published unless the Owner explicitly approved it.
6. Save a screenshot of the draft state.

## Verification log schema

Recommended shape:

```json
{
  "job_id": "JOB-2026-05-05-001",
  "verified_by": "Codex Computer Use",
  "verified_at": "2026-05-05T20:30:00+08:00",
  "verification_targets": [
    {
      "type": "dashboard",
      "expected": "T-A6-001 appears as a task node",
      "observed": "T-A6-001 task node visible with status active",
      "screenshot": "screenshots/dashboard_ta6001.png",
      "result": "pass"
    }
  ],
  "overall_result": "pass"
}
```

## Review rule

If the bundle does not contain the evidence files, screenshots, and writeback diff, the task is not closed.
