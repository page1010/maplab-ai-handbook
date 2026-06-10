# WordPress Status Matrix

Date: 2026-06-08
Mode: read-only evidence patrol

| Surface | Last verified state | Source date | Source file | Freshness in this run | Notes |
|---|---|---:|---|---|---|
| Patrol contract | `T-A2-006-ads-seo-wordpress-patrol` ACTIVE | 2026-06-01 | `CURRENT_STATUS.md` | repo-verified | read-only external checks + safe repo/proposal edits only |
| Live To-B route set | 7 live URLs are still the canonical route set; 4 had fresh public fetch success in this run | 2026-06-08 / 2026-05-26 | `review_request.md` + current patrol web fetch | partial refresh | fresh public proof: `corporate-catering-tainan`, `corporate-tea-party-desserts`, `press-conference-catering`, `vip-expo-catering-business-meeting` |
| Planned slug exclusion | 5 planned slugs are 404 and must stay excluded | 2026-05-26 | `review_request.md`, `pitfalls.md` | repo-verified | do not reopen old slug path |
| WordPress public structure | 6 pages / 57 posts; B2B entry is published posts, not pages | 2026-05-24 | `CURRENT_STATUS.md` | stale | useful context, not fresh site proof |
| Draft post | post `1696`, title `MAPLAB 企業外燴與活動茶點案例審核草稿 Round 008`, status `草稿` | 2026-05-27 | `reports/wp_draft_round_009.md` | stale | reload-verified in prior run |
| Draft content continuity | 21 case blocks + image slot/filename/alt/caption mapping present | 2026-05-27 | `reports/wp_draft_round_009.md` | stale | no publish action recorded |
| Image upload state | 30 WebP files still not uploaded to WP media library | 2026-05-27 | `reports/wp_draft_round_009.md` | stale | expected upload URLs were 404 then |
| Upload blocker | Chrome extension file chooser returned `Not allowed` | 2026-05-27 | `reports/wp_draft_round_009.md` | stale | needs file URL access before retry |
| Rank Math state | subscription cancelled / settings frozen | 2026-05-24 onward | `CURRENT_STATUS.md`, `pitfalls.md` | repo-verified | not part of this patrol's edit scope |

## VERIFIED

- The correct WordPress frontier is existing live posts plus the saved draft `post=1696`.
- The correct blocker is media-upload permission, not missing copy or missing routing logic.
- The patrol must not treat planned slugs as live targets.
- Public fetch succeeded on 2026-06-08 for 4 live To-B posts, so the route set is not repo-only stale.

## MISSING DATA

- No complete live HTTP status check for all 7 route URLs in this run.
- No fresh public fetch proof in this run for `tainan-corporate-opening-tea-catering`, `brand-esg-catering-service`, or `daxin-art-museum-opening-catering`.
- No fresh WordPress REST count recheck in this run.
- No fresh backend proof that file URL access is now enabled.
- Shell `curl` validation was blocked by the environment, so public freshness proof had to come from external web fetch rather than local command output.

## Next Concrete Command

```bash
cd /Users/pagemacmini/maplab-ai-handbook
rtk rg -n "post=1696|Not allowed|404|file URL access" \
  workbook/reviews/JOB-A2-B2B-CASE-ADS-20260526/reports/wp_draft_round_009.md \
  workbook/reviews/JOB-A2-B2B-CASE-ADS-20260526/execution_loop.md \
  CURRENT_STATUS.md
```
