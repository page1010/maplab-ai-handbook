# ROUND 004 — Antigravity Visual Bridge Meta Command

日期：2026-05-26
管理方：A2

## Why This Command Exists

Antigravity cannot directly see A2's Owner Chrome UI. A2 will therefore provide a visual bridge packet: a cropped screenshot plus structured UI facts.

Owner corrected that the prior account-recheck path read the wrong browser context: an agent Facebook / Chrome window, not MAPLAB's Owner Chrome Ads Manager.

## Give This To Antigravity

Use:

`workbook/reviews/JOB-A2-B2B-CASE-ADS-20260526/ANTIGRAVITY_VISUAL_BRIDGE_META_PROMPT.md`

## Expected Output

`workbook/reviews/JOB-A2-B2B-CASE-ADS-20260526/reports/antigravity_visual_bridge_meta_round_004.md`

## Acceptance Criteria

- It treats `reports/meta_ads_owner_chrome_visual_bridge_round_004.md` as current source of truth.
- It ignores the superseded `2441634989673207` account-recheck conclusion.
- It confirms current verified account `318634712 (318634712)`.
- It ranks which visible campaigns are B2B-useful vs To C/noise vs unknown.
- It gives A2 the next read-only UI packet request for ad set targeting and destination URLs.
- It keeps all Meta changes proposal-only.
- It does not request API tokens/passwords and does not ask A2 to publish, save, edit, duplicate, accept dialogs, or change toggles.
