# Review Request

status: waiting_for_review

## What Changed

Chrome Agent Commander is now a runtime handoff panel:

- Reads dynamic role task modules from GitHub raw.
- Shows role simulation, read-first sources, affected systems, and output contract.
- Produces handoff prompts for Gemini, Codex, OpenClaw, and legacy Claude tab.
- Keeps Claude tab injection as legacy only.

## Verification Summary

- Local extension path confirmed as the canonical repo.
- Static JS/JSON checks passed.
- Computer Use verified A2 module召喚 in Chrome.
- Fixed duplicated `v` display.
- Converted historical missing `TASK_QUEUE.md` into a fallback source relation.

## Reviewer Notes

Post-push Computer Use refresh confirmed `TASK_QUEUE.md` now displays as a fallback source instead of a hard missing source because the extension reads the updated module JSON from GitHub raw main.
