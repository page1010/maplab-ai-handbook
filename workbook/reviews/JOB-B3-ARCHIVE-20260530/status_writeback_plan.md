# Status Writeback Plan

## Truth Surfaces To Update

| Surface | Action | Why |
|---|---|---|
| `workbook/reviews/JOB-B3-ARCHIVE-20260530/` | Write now | This is the durable B3 archive bundle. |
| `pitfalls.md` | Append one boundary lesson | Future sessions need the B3/B4 separation reminder. |
| Local `CURRENT_STATUS.md` (`/Users/pagemacmini/Documents/New project/CURRENT_STATUS.md`) | No B3 write in this pass | It already carries the latest audit summary and the active Codex handoff. |
| Local `tasks/INVESTOS_RESEARCH_METHOD_UPGRADE_20260529.md` | No B3 write in this pass | The task card already records the owner approvals and the active next step. |

## Only Handoff Advice

- The provisional `continue / pause / refactor` split should be treated as a review request, not as a final system-patrol verdict.
- The active implementation flow should continue in Codex only after the archive is acknowledged.
- Any further runtime change should be written by the runtime-owning agent after verification, not by this archive pass.

## Do Not Touch

- Runtime logs.
- Launchd plists.
- Dispatcher registration.
- DB files.
- Secrets, `.env`, tokens, cookies.
- Broker / order state.
- Publishing surfaces.
