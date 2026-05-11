# MAPLAB OpenClaw Output Contract

This document defines how local OpenClaw work should be written so the next agent can continue it.

## Required artifact shape

Every meaningful task should produce one primary artifact and one handoff record.

### Primary artifact

Examples:

- a draft article
- a photo sorting plan
- a research brief
- a task summary
- a verification result

### Handoff record

The handoff record should say:

- what was done
- what was produced
- who will use it
- what to do next
- what is still blocked

## Mandatory fields

Every output should make these fields obvious:

- `consumer`
- `next_action`
- `write_back`
- `related_tasks`
- `risk_level`

If the task is multi-step, also include:

- `stage`
- `stage_result`
- `open_questions`

## Closed-loop output examples

### Ads / content

Should include:

- WordPress draft
- SEO title
- meta description
- slug
- image suggestions
- alt text
- Meta ad copy
- material usage notes
- review notes

### Stock

Should include:

- research brief
- risk list
- watchlist
- next verification questions

### Engineering / review

Should include:

- issue diagnosis
- fix proposal
- verification checklist
- risk notes
- evidence path

## Review bundle requirement

If the output came from a local worker, the run is not complete until the bundle exists in:

`workbook/reviews/JOB-xxx/`

The bundle should be enough for A1 and Owner to review without reopening the original conversation.

## Writeback rule

Do not overwrite truth sources directly unless the workflow explicitly allows it.

Preferred writeback order:

1. draft or output artifact
2. review bundle
3. task card update
4. changelog or status update, if appropriate
