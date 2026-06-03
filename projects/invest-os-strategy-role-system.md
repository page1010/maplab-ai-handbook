# Investment OS Strategy Role System

Last updated: 2026-06-03

This document lets MAPLAB Chrome Extension role modules summon Investment OS
strategy owners without loading the whole Investment OS repo into context.

Canonical Investment OS files:

- `/Users/pagemacmini/Documents/New project/config/investment_os_role_registry.json`
- `/Users/pagemacmini/Documents/New project/docs/INVESTMENT_OS_ROLE_WORKSPACES.md`
- `/Users/pagemacmini/Documents/New project/tasks/INVESTMENT_OS_ROLE_WORKSPACES_20260603.md`
- `/Users/pagemacmini/Documents/New project/app/dashboard/streamlit_app.py`

## Principle

Strategy owner owns the whole loop. Telegram and Dashboard are delivery
surfaces, not the owners of strategy logic.

If a strategy output is bad, route to the strategy owner first:

- KOL output bad -> IOS-KOL
- Momentum output stale -> IOS-MOMENTUM
- Real position risk unclear -> IOS-INVENTORY
- Macro card wrong -> IOS-MACRO
- Polymarket or cross-source alpha noisy -> IOS-ALPHA or IOS-BLACKSWAN
- Shared Markdown/card layout broken across many strategies -> IOS-SURFACE
- Dirty worktree and keep/drop needed -> IOS-HYGIENE

## Shared Startup

Every IOS role must start with:

```text
我是 [role_id] [role_name]，環境 [runtime]，任務 [task]。
```

Then read:

1. Investment OS `AGENT_CORE.md`
2. Investment OS `CURRENT_STATUS.md`
3. Investment OS `pitfalls.md`
4. Investment OS `config/investment_os_role_registry.json`
5. Investment OS `docs/INVESTMENT_OS_ROLE_WORKSPACES.md`
6. role-specific required reads from the registry

## Worker Roles

OpenClaw:
Browser operator for logged-in web UI work, ChatGPT/Gemini/NotebookLM
copy-paste, screenshots, and raw evidence packets.

Hermes:
Cold-path chief of staff for summaries, question packs, deterministic report
scaffolds, and bounded Computer Use smoke checks.

Local model:
Cheap preprocessing and shadow draft. It needs Codex/B2 scoring before formal
reports.

External GPT/Gemini:
Second opinion and web-model research. Output remains evidence until a strategy
owner integrates it.

## B1-B4 Loop

- B1 Builder: build or repair scoped implementation.
- B2 Reviewer: review dataflow, freshness, report contract, and surface proof.
- B3 Archivist: archive review bundle, task card, resume prompt, and pitfalls.
- B4 System Patrol: decide stop/continue/refactor/cleanup when roles drift or
  the system gets too broad.

## Output Expectations

Every IOS role should return file-backed evidence when doing real work:

- strategy-specific output, for example `kol_digest.md` or `momentum_shortlist.md`
- `source_freshness_matrix.md` or equivalent freshness proof
- `telegram_readback.md` or `dashboard_freshness_check.md` when owner-facing
  surfaces are touched
- `b1_b4_handoff.md` when repair, archive, patrol, or cleanup is needed
- `review_request.md`
