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

After this bundle is pushed to GitHub, refresh the side panel once. `TASK_QUEUE.md` should display as fallback instead of a hard missing source because the extension reads module JSON from GitHub raw main.

