# Review Request — JOB-A2-ADS-SEO-WP-PATROL-20260608

Date: 2026-06-08
Owner: A2 patrol automation

## What Is Ready

- Brand memory check is refreshed from the current repo truth files.
- Patrol findings are split into `VERIFIED / REASONABLE INFERENCE / MISSING DATA`.
- The current A2 frontier is narrowed to:
  - existing live To-B URLs
  - WordPress draft `post=1696`
  - 30 local WebP assets waiting on file URL access
  - proposal-only Google/Meta landing alignment

## What Still Needs Fresh Evidence

1. Public freshness for the remaining route URLs:
   - `/tainan-corporate-opening-tea-catering/`
   - `/brand-esg-catering-service/`
   - `/daxin-art-museum-opening-catering/`
2. WordPress backend freshness after 2026-05-27
3. Google Ads final URL / ad-level routing freshness after 2026-05-26
4. Meta B ad set detail / destination freshness after 2026-05-26
5. Whether Codex Chrome extension file URL access is now enabled

## Owner / A1 Decision Points

1. Whether to request a new Owner Chrome read-only bridge round for WordPress + Google Ads + Meta Ads.
2. Whether to keep proposal work paused until the `post=1696` media blocker is cleared.
3. Whether external brand / venue / logo handling should be approved for the next implementation-facing round.

## If You Want The Next Minimal Patrol Step

Run this repo-only prep command first:

```bash
cd /Users/pagemacmini/maplab-ai-handbook
rtk sed -n '1,220p' workbook/reviews/JOB-A2-B2B-CASE-ADS-20260526/reports/wp_draft_round_009.md
```

If the goal is freshness proof rather than reread, the next action should be:

- reopen Owner Chrome read-only evidence flow for WP / Google Ads / Meta Ads
- verify file URL access state before any upload retry
- keep all actions read-only unless Owner/A1 explicitly approves a later implementation round

## Approval Boundary Reminder

Without Owner/A1 approval:

- do not publish WordPress
- do not change Google Ads / Meta Ads
- do not change Rank Math paid/settings state
- do not read secrets/cookies/keys
