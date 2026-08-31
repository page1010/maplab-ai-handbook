---
name: maplab-session-continuity
description: Resume or hand off interrupted MAPLAB work across Claude and Codex without duplicating artifacts. Use when a session disconnects, another agent has partial work, a Task Card may be stale, or shared dirty files make ownership unclear.
---

# MAPLAB session continuity

Resume the existing bounded action from durable evidence so prior work moves directly toward completion.

## Establish truth before editing

1. Read `CURRENT_STATUS.md`, `pitfalls.md`, the exact Task Card, its latest receipt, and its Resume Prompt.
2. Compare the Task Card with recent scoped commits, current dirty paths, and any relevant live surface. A backup proves recoverability, not completion.
3. Read the shared registry:

```bash
python3 /Users/pagemacmini/claude-daily-operations/ops/claude-daily-operations/work_claims.py list
```

If the task is registered and `ready`, claim it before changing files. An active claim by another agent reserves the overlapping artifacts for that agent. If the task is missing, verify the Task Card, name one next bounded action, and register it.

## Continue one bounded action

- Preserve unrelated dirty work and identify overlap before editing.
- Start from the last verified artifact or live readback; treat chat as a pointer to evidence.
- Treat stale questions already answered by the Owner as state drift; repair the Task Card instead of asking again.
- One claim advances one Task Card through one next bounded action.

## Leave a durable handoff

Before stopping:

1. Write a receipt with verified output, tests/readback, missing evidence, and one next bounded action.
2. Update the Task Card status and Resume Prompt. Update `CURRENT_STATUS.md` only when the scoped change does not overlap another agent's dirty edit.
3. Stage the exact files owned by this action. Push and merge remain explicit Owner-authorized release steps.
4. Checkpoint the shared claim with the existing receipt and one of `ready`, `owner_gate`, `blocked`, or `complete`. A `ready` checkpoint releases the task for the next healthy agent.

An expired claim is requeued by the 30-minute continuation heartbeat. A copied repo, browser tab, process exit, local test, or uncommitted artifact is not a handoff.
