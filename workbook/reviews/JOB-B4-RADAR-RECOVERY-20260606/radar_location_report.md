# Radar Location Report — JOB-B4-RADAR-RECOVERY-20260606

- role: B4 System Patrol / Codex
- generated_at: 2026-06-06T21:42+08:00
- canonical_repo: `/Users/pagemacmini/maplab-ai-handbook`
- investment_os_repo: `/Users/pagemacmini/Documents/New project`

## Cold Start

- Investment OS cold start read: `AGENT_CORE.md`, `CURRENT_STATUS.md`, `pitfalls.md`, `docs/TASK_CARD_PROTOCOL.md`, `ai_team/README.md`, `docs/OPENCLAW_ROUNDTABLE_AND_TRUMP_MONITOR_PROTOCOL.md`.
- MAPLAB cold start read: `CURRENT_STATUS.md`, `pitfalls.md`.
- MAPLAB `AGENT_CORE.md` / `AGENTS.md` were not present at repo root; treated as missing context, not a blocker.
- MAPLAB fit check read: `workbook/reviews/JOB-B4-PATROL-20260530/fit_check.md`.

## Radar Code And Data

- Main radar code: `/Users/pagemacmini/Documents/New project/scripts/run_convergence_engine.py`
- Runtime dispatcher: `/Users/pagemacmini/.local/share/investmentos-telegram-operator/scripts/run_invest_os_background_job.py convergence-engine`
- Runtime radar report truth: `/Users/pagemacmini/.local/share/investmentos-telegram-operator/data/convergence_all.md`
- Repo mirror report: `/Users/pagemacmini/Documents/New project/data/convergence_all.md`
- Runtime launchd log: `/Users/pagemacmini/.local/share/investmentos-telegram-operator/data/logs/convergence_engine_launchd.out.log`

## Evidence

- `launchctl print gui/501/com.investmentos.convergence-engine`: state `running`, `runs = 254`, `last exit code = 0`, interval `900 seconds`.
- Runtime `convergence_all.md`: mtime `Jun 6 21:31`, current BSI `0/100`.
- Repo `data/convergence_all.md`: mtime `Jun 2 07:26`, stale mirror; not the live truth source.
- Runtime SQLite 90-minute source activity: `Polymarket=9`, `r/Economics=6`, `r/investing=8`, latest rows around `2026-06-06 13:20 UTC`.
- Historical BSI=78 evidence exists in runtime launchd out log:
  - line 21396: `黑天鵝指數：78/100`
  - line 22896: `黑天鵝指數：78/100`
  - line 37794: `黑天鵝指數：78/100`

## Finding

The convergence radar is active in runtime. The correct integration path is to read the runtime `data/convergence_all.md` first and use the repo copy only as a secondary mirror. The 06/03 BSI=78 event is preserved in runtime logs, but the latest runtime report is BSI=0.
