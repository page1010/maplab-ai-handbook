# Review Request

- requester: `B1 Investment OS Builder`
- job_id: `JOB-B1-BUILDER-20260602`
- requested_role: `B2 Reviewer`
- status: `ready_for_review`

## Review Questions

1. Does the Investment OS module clearly state that hedging is risk reduction, not bearish trade advice?
2. Does it avoid implying that futures, puts, CSP, or covered calls are executable without Owner approval?
3. Does the default redaction policy adequately protect live account and position details from git history?
4. Should `market_weakening` and `black_swan` risk-state thresholds be stricter before dashboard/Telegram exposure?
5. Are advanced strategies (`0DTE`, dispersion, synthetic hedge, long gamma) sufficiently locked to research-only?

## Evidence

- Investment OS review bundle: `/Users/pagemacmini/Documents/New project/reviews/POST-MARKET-HEDGE-BLACK-SWAN-SOP-20260602/`
- Investment OS commits:
  - `1af2253 feat: add post-market hedge risk control`
  - `1c45ec8 docs: record hedge risk control checkpoint`
- MAPLAB merge/sync commit: `69f2335 merge: sync origin main patrol status`

## Boundary

This is a B1 build handoff, not final investment approval and not an order workflow.
