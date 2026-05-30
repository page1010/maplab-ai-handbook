# Stop / Continue / Refactor Recommendations — JOB-B4-PATROL-20260530

## Continue

- Keep `CURRENT_STATUS.md` and task cards as the single durable state layer.
- Keep the Chrome Extension summon flow and B-role auto-selection.
- Keep Agent Office as the desktop control-plane surface.
- Keep Telegram + Dashboard as the owner-facing mobile and first-screen surfaces.
- Keep the B1-B4 split, because it reduces role confusion and makes handoff easier.
- Keep Hermes and OpenClaw only as bounded evidence / cold-path tools.

## Pause

- Pause any attempt to revive the old broker-simulation route.
- Pause further expansion of OpenClaw into full macOS autonomy until the end-to-end receipt chain exists.
- Pause further expansion of Hermes into hot-path authority; it should stay read-only / bounded.
- Pause the research_method_layer migration; it is still a draft, not a runtime contract.
- Pause any return to InnerFlowLab content publishing unless Owner/A1 explicitly reopens it.

## Refactor

- Refactor cloud mirrors, share pages, and exports so they are always regenerated from committed GitHub HEAD.
- Refactor the owner-facing surfaces so each one has one job only:
  - Telegram = mobile brief / bell
  - Dashboard = first-screen status
  - Agent Office = desktop control-plane
  - Task cards = durable work ledger
  - Review bundles = evidence and handoff
- Refactor new research layers so they only land when there is a current owner problem to solve, not because the schema looks elegant.

## Archive

- Archive `proposed_orders` + `execute_open_orders.py` + `sj.Shioaji(simulation=True)` as a legacy semantics path.
- Archive any stale or orphan state that is no longer part of the active truth source.
- Archive the old B1 content publishing branch unless Owner explicitly reopens it.

## Practical Rule

- Do not add a new surface unless it removes a real owner pain point or replaces an existing duplicate surface.
- If the new surface does not replace anything, it is probably overbuild.

## Recommended Freeze Boundary

Freeze all new experimental surface growth until the current critical lanes settle. The system already has enough control planes. What it needs now is proof, pruning, and cleanup.
