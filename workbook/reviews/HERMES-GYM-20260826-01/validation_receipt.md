# Hermes Gym Validation Receipt

- run_id: `HERMES-GYM-20260826-01`
- mode: local synthetic dry-run
- external customer data: none
- network calls: 0
- Telegram sends: 0
- Google Sheet/GAS writes: 0

## First Hermes attempt

Hermes completed a ten-field fictional intake and correctly kept `quoted_amount=null`, `menu=[]`, and `promises=[]` until the A5 handoff. The run exposed a real parser defect: after `60人`, the dietary note `4位吃素` was incorrectly treated as total headcount by the prior Case Store and A5 parsers.

## Corrections added

- Added deterministic intake state and quote-ready gate.
- Dietary/staff counts no longer overwrite attendee headcount.
- Chinese Gregorian dates such as `2026年10月15日` are normalized.
- Nut allergy is recognized as a hard dietary restriction.
- Added a local Hermes Gym runner and regression tests.

## Acceptance

- Hermes dialogue collection: PASS (fictional case, no commercial promise)
- Full-field quote-ready gate: PASS
- A5 local payload handoff: PASS
- Formal quote / live Sheet / customer send: NOT RUN; remains approval-gated
