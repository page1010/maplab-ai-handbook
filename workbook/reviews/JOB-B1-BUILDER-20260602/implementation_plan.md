# B1 Builder Implementation Plan

- job_id: `JOB-B1-BUILDER-20260602`
- role: `B1 Investment OS Builder`
- runtime_target: `codex`
- maplab_repo: `/Users/pagemacmini/maplab-ai-handbook`
- investment_os_repo: `/Users/pagemacmini/Documents/New project`
- date: `2026-06-02`

## Startup Check

B1 is the correct role for this run because the Owner asked for an Investment OS feature build:

- daily post-market hedge risk control;
- black-swan SOP;
- TW/US hedge tool table;
- runtime/report surface wiring;
- verifiable repo change and commit.

Review-only, archive-only, and patrol-only work should still route to B2, B3, or B4 respectively.

## Plan Executed

1. Read MAPLAB B1 governance sources and confirm B1 module state.
2. Sync MAPLAB `main` with `origin/main` as requested by Owner (`git該更新的更新`).
3. Resolve the MAPLAB `CURRENT_STATUS.md` merge conflict by preserving both A1 patrol status and B1 dashboard freshness repair status.
4. Cold-start Investment OS repo from `AGENT_CORE.md`, `CURRENT_STATUS.md`, `pitfalls.md`, task protocol, risk master, and workflow docs.
5. Build the v0.1 post-market hedge / black-swan SOP module in Investment OS:
   - task card;
   - config;
   - report generator;
   - tests;
   - task index entry;
   - repo report;
   - runtime-local smoke report;
   - review bundle and status writeback.
6. Commit the Investment OS implementation and status checkpoint.
7. Write this MAPLAB B1 review bundle.

## Safety Boundary

- No WordPress publishing.
- No push to main.
- No secrets, `.env`, API keys, or cookies read.
- No broker calls.
- No real or simulated broker orders.
- No Telegram trade instructions.
