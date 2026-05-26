# Antigravity Visual Bridge Meta Prompt — Round 004

You are assisting A2. You cannot see the Owner Chrome UI directly, so you must treat A2's visual bridge packet as the source of truth.

## Read First

Read:

- `workbook/reviews/JOB-A2-B2B-CASE-ADS-20260526/reports/meta_ads_owner_chrome_visual_bridge_round_004.md`
- `workbook/reviews/JOB-A2-B2B-CASE-ADS-20260526/visual_evidence_round_004/meta_ads_owner_chrome_campaigns_round_004_cropped.png`
- `workbook/reviews/JOB-A2-B2B-CASE-ADS-20260526/reports/a3_meta_round_001.md`
- `workbook/reviews/JOB-A2-B2B-CASE-ADS-20260526/wordpress_update_plan.md`
- `workbook/reviews/JOB-A2-B2B-CASE-ADS-20260526/google_ads_change_plan.md`

## Important Correction

Do not use:

- `reports/meta_ads_chrome_round_002_account_recheck.md` as live evidence.
- Any conclusion that says current Meta Ads account is `2441634989673207`.
- Any conclusion that says `318634712` is unavailable.

Owner corrected that the previous read came from an agent Facebook / Chrome window, not the MAPLAB Owner Chrome window. The current verified Meta Ads context is:

- ad account `318634712 (318634712)`
- business/global scope `215690449213844`
- 13 visible campaign rows

## Output

Create:

`workbook/reviews/JOB-A2-B2B-CASE-ADS-20260526/reports/antigravity_visual_bridge_meta_round_004.md`

## Required Sections

1. Visual bridge protocol
   - how A2 should continue giving you UI state
   - what screenshot/text facts are sufficient
   - what you cannot infer without a new packet
2. Verified current Meta campaign facts
   - account context
   - date range
   - 13 campaign rows
   - active vs closed state
3. B2B usefulness ranking
   - likely useful campaigns
   - likely To C/noise campaigns
   - unknown campaigns needing ad set inspection
4. Next read-only UI instructions for A2
   - exact layer to open next
   - priority campaign order
   - columns/fields to capture
   - forbidden actions
5. Updated A3 Meta instruction
   - proposal-only interest clusters
   - which existing campaign surfaces are candidates
   - which facts remain `Needs UI Check`
6. Updated dashboard / loop status
   - what can now move forward
   - what remains blocked by missing UI data

## Guardrails

- Do not ask Owner for API tokens, OAuth refresh tokens, app secrets, or passwords.
- Do not ask A2 to click `檢查並發佈`, `捨棄草稿`, save, publish, duplicate, accept policy dialogs, edit campaign settings, or change toggles.
- Do not claim ad set interests, pixel, custom audience, or destination URLs are verified until A2 provides a new visual bridge packet for those screens.
- Do not treat outdated or superseded reports as live facts.
- Keep all Meta changes proposal-only.
