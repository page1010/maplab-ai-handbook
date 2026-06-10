# A2 Ads / SEO / WordPress Patrol Report

Date: 2026-06-08
Mode: read-only patrol + safe repo/report updates only

## Patrol Scope Executed

- Read cold-start truth files and patrol contract.
- Rechecked patrol bundle `JOB-A2-ADS-SEO-WP-PATROL-20260601`.
- Rechecked latest A2 B2B evidence bundle `JOB-A2-B2B-CASE-ADS-20260526`.
- Reviewed current proposal-only files:
  - `google_ads_change_plan.md`
  - `wordpress_update_plan.md`
  - `meta_landing_page_proposal_round_007.md`
- Re-validated a partial public live URL set on 2026-06-08 through external web fetch:
  - `/corporate-catering-tainan/`
  - `/corporate-tea-party-desserts/`
  - `/press-conference-catering/`
  - `/vip-expo-catering-business-meeting/`
- No external systems were opened or changed in this run.

## VERIFIED

- `T-A2-006-ads-seo-wordpress-patrol` remains ACTIVE and bounded to read-only external checks plus safe repo/proposal edits.
- MAPLAB brand memory remains anchored to `skills/brand-voice-guide.md` and `skills/maplab-visual-spec.md`.
- Latest known WordPress draft frontier is still post `1696`, saved as draft, reload-verified, containing 21 case blocks plus image slot/alt/caption mapping.
- Latest verified live To-B routing still points to the 7 known live URLs from the 2026-05-26 evidence set; old planned slugs remain excluded.
- A fresh public fetch on 2026-06-08 succeeded for 4 live To-B URLs:
  - `corporate-catering-tainan`
  - `corporate-tea-party-desserts`
  - `press-conference-catering`
  - `vip-expo-catering-business-meeting`
- Latest verified Google Ads backend evidence still shows 13 visible keywords under one campaign/ad group, with keyword-row final URL shown as `—`.
- Latest verified Meta backend evidence still shows:
  - `互動廣告組合 A 企業窗口` is an engagement/follow objective, not a WordPress landing-page traffic ad.
  - `互動廣告組合 B 公關公司窗口` remains a running B2B seed with detail pane still incomplete.
- Rank Math remains frozen in the current workflow; no new RM work is authorized.

## REASONABLE INFERENCE

- The active A2 frontier is no longer missing-report recovery. It is Owner review of draft/proposal assets plus the media-upload permission blocker on `post=1696`.
- Google Ads and Meta planning are structurally aligned around the same live To-B routes, but freshness is stale because the authenticated evidence dates from 2026-05-26 to 2026-05-27.
- Existing live posts remain the correct landing surfaces; creating new top-level slugs would reopen a pitfall already documented.

## MISSING DATA

- No complete 2026-06-08 live HTTP recheck for all 7 public To-B URLs in this run.
- No fresh 2026-06-08 public proof yet for:
  - `/tainan-corporate-opening-tea-catering/`
  - `/brand-esg-catering-service/`
  - `/daxin-art-museum-opening-catering/`
- No fresh 2026-06-08 WordPress backend read-only capture.
- No fresh 2026-06-08 Google Ads UI capture for ad-level final URL, URL expansion, or conversion state.
- No fresh 2026-06-08 Meta UI capture for B ad set targeting, destination, or any pixel/custom-audience state.
- No proof that the Chrome extension file URL permission has been enabled since the `Not allowed` upload failure.
- Shell-side direct network checks were blocked in this environment, so public freshness proof in this run is limited to external web fetch output.

## Patrol Verdict

- Status: partial, evidence-consistent
- Reason: repo evidence is coherent and the current frontier is clear, but external-state freshness was not renewed in this run

## Safe Repo Actions This Run

- Created the 2026-06-08 patrol bundle.
- Re-stated the current frontier using `VERIFIED / REASONABLE INFERENCE / MISSING DATA`.
- Added partial 2026-06-08 live URL freshness proof for 4 public To-B pages.
- Kept the review focused on the latest draft/media blocker rather than reopening Round 001 completeness.

## Next Concrete Command

```bash
cd /Users/pagemacmini/maplab-ai-handbook
rtk sed -n '1,220p' workbook/reviews/JOB-A2-B2B-CASE-ADS-20260526/reports/wp_draft_round_009.md
```

If freshness proof is required next, the follow-up should be an Owner Chrome read-only bridge round, not a repo-only reread.
