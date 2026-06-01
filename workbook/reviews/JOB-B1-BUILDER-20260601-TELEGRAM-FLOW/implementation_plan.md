# B1 Implementation Plan - Telegram Conversation Flow

JOB_ID: JOB-B1-BUILDER-20260601-TELEGRAM-FLOW
ROLE: B1 Investment OS Builder
DATE: 2026-06-01

## User Need

Owner asked B1 to look at the Telegram conversation behind `@page_trading_bot`
and optimize the process and program/agent division behind the conversation.

## Scope Decision

This is partly B1 and partly B2/B3/B4:

- B1 owns the repo/runtime wiring fix for a concrete message flow.
- B2 should review dataflow freshness, gateway metadata, and allowlist coverage.
- B3 should archive the runtime readback and resume prompt after the next live send.
- B4 should patrol whether realtime convergence belongs in Telegram or should be
  dashboard-only unless a threshold is hit.

## Implementation Plan

1. Cold-start from Investment OS and MAPLAB governance docs before editing.
2. Use Chrome read-only Telegram Web evidence to inspect the latest owner-facing
   messages without sending Telegram or reading secrets.
3. Identify a concrete high-noise flow that B1 can safely fix: Convergence
   `Investment OS 跨源共振雷達`.
4. Separate full evidence report generation from Telegram phone-card rendering.
5. Add a regression test that proves Telegram output is short, file-backed, and
   does not expose prompt paths or full matrix rows.
6. Update Investment OS truth surfaces and this MAPLAB review bundle.
7. Sync the scoped runtime script only after repo/runtime diff parity check.

## Out Of Scope

- No Telegram test spam.
- No broker/order changes.
- No `.env`, token, cookie, or secret reads.
- No global gateway/allowlist refactor in this pass.
- No publishing or WordPress work.

