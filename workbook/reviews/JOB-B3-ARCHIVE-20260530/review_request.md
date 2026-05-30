# Review Request — Investment OS Overbuild Archive

## 已讀來源

- `CURRENT_STATUS.md`
- `pitfalls.md`
- `projects/invest-os-b-role-system.md`
- `projects/b3-invest-os-archivist.md`
- `workbook/reviews/README.md`
- `tasks/INVESTOS_RESEARCH_METHOD_UPGRADE_20260529.md`
- `reviews/JOB-INVESTOS-AUDIT-20260529/CURRENT_STATE_AUDIT.md`
- `reviews/JOB-INVESTOS-AUDIT-20260529/OPENCLAW_ROLE_BOUNDARY.md`
- `reviews/JOB-INVESTOS-AUDIT-20260529/OPENCLAW_TASK_PROPOSAL.md`
- `reviews/JOB-INVESTOS-AUDIT-20260529/SHADOW_QA_PROTOCOL.md`
- `reviews/JOB-INVESTOS-AUDIT-20260529/TASK_DELEGATION_PLAN.md`
- `reviews/JOB-INVESTOS-AUDIT-20260529/narrative_cards_top10_draft.md`

## 已驗證事實

- The system is already Phase 6 / v6.0, not a small scaffold.
- `launchd` + `run_invest_os_background_job.py` is the real scheduler.
- OpenClaw is a bounded browser operator, not the scheduler.
- `openclaw_tasks/cron.yml` is orphan / superseded unless explicitly migrated.
- Canonical DB is `data/investment_os.sqlite3`; `.db` variants are stale / orphan copies.
- The research-method layer was missing at audit time, and the audit correctly treated it as a new gated overlay rather than a parallel scheduler.
- The local task card now records that the 5-table schema has been approved and applied, so the remaining concern is expansion discipline, not the migration itself.

## 合理推論

- The system is overbuilt when parallel truth surfaces outpace proof and review.
- Existing runtime primitives should be kept, while expansion should stay smoke-gated.
- The approved research-method layer should remain a discipline overlay, not a second copy of the existing runtime stack.

## 缺資料

- Whether the approved daily jobs have already passed their smoke gates end-to-end.
- Whether B4 wants the provisional list to stay archive-only or be mirrored into a patrol verdict file.
- Whether the next owner-visible writeback should be limited to the archive bundle or also mirrored into a short status note.

## Continue / Pause / Refactor

### Continue

- Canonical DB `.sqlite3`.
- `agent_command_center.py` + receipt board.
- `launchd` + dispatcher.
- Existing left/right/rumour/chip/convergence lanes.
- The research-method layer as a smoke-gated overlay.

### Pause

- New dashboard panels without proof.
- New Telegram surfaces without readback.
- Any extra daily job beyond the approved smoke-gated set.
- Any parallel scheduler path that revives the orphan `cron.yml` world.

### Refactor

- Stale scaffold docs and superseded pointers.
- DB path ambiguity.
- Orphan cron plan.
- B3 archive versus B4 patrol boundary.
- One-way intake: `research_inbox -> narrative_cards -> Shadow QA -> status`.

## 高風險需批准

- Any further schema apply beyond the already-approved 5 tables.
- Any new launchd job or dispatcher command.
- Any direct runtime mutation of DB, scheduler, or publishing surface.

## 產出路徑

- `workbook/reviews/JOB-B3-ARCHIVE-20260530/version_note.md`
- `workbook/reviews/JOB-B3-ARCHIVE-20260530/handoff_checkpoint.md`
- `workbook/reviews/JOB-B3-ARCHIVE-20260530/resume_prompt.md`
- `workbook/reviews/JOB-B3-ARCHIVE-20260530/status_writeback_plan.md`
- `workbook/reviews/JOB-B3-ARCHIVE-20260530/review_request.md`

## 下一步

- B4 should review the provisional continue / pause / refactor split.
- Codex should continue the active `web_cdp` backend task after the archive is acknowledged.
- No one should treat this archive as a new scheduler design.
