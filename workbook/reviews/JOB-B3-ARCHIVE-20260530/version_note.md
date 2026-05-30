# B3 Version Note — Investment OS Overbuild Archive Snapshot

- role: B3 Investment OS Archivist
- date: 2026-05-30 Asia/Taipei
- scope: docs-only archive; no runtime logs, DB, launchd, dispatcher, or secrets were touched
- source roots: `/Users/pagemacmini/Documents/New project` and `/Users/pagemacmini/maplab-ai-handbook`

## Snapshot

The system is not a Phase-0 scaffold. It is a Phase 6 / v6.0 runtime with real scheduling, a central dispatcher, a command board, a canonical SQLite DB, and multiple owner-facing surfaces. The overbuild risk is therefore not raw feature count alone. The real risk is truth-source drift, orphan paths surviving beside the real scheduler, and new layers being added before the proof chain exists.

## Provisional Continue / Pause / Refactor

### Continue

- Canonical DB `.sqlite3` as the one runtime truth source.
- `agent_command_center.py` + receipt loop as the durable handoff layer.
- `launchd` + `run_invest_os_background_job.py` as the only scheduler.
- Existing `left/right/rumour/chip/convergence` stack as the current runtime base.
- `research_inbox` as the L1 intake surface.
- The research-method layer only as a gated overlay after smoke, Shadow QA, and approval.

### Pause

- Any new dashboard panel or Telegram surface without owner-facing proof.
- Any new daily job beyond the approved smoke-gated set.
- Any parallel scheduler or cron revival.
- Any extra table or pipeline that duplicates existing runtime lanes before it is clearly disambiguated.

### Refactor

- Stale scaffold docs that still point at the old world-view should be marked superseded.
- `openclaw_tasks/cron.yml` should stay treated as orphan / superseded unless it is explicitly migrated.
- `.db` versus `.sqlite3` ambiguity should remain pinned to the canonical `.sqlite3`.
- B3 archive should stay separate from B4 patrol verdicts.
- The data flow should remain one-way: `research_inbox -> narrative_cards -> Shadow QA -> status`.

## Current Nuance

The local task card now records that the 5-table schema has been approved and applied. That means the pause recommendation here is **not** "freeze all research-method work forever". It means "do not keep expanding the system faster than the smoke and evidence chain can keep up."
