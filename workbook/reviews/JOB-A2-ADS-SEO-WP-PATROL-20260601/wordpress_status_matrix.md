# WordPress Status Matrix

Date: 2026-06-01
Mode: Read-only evidence patrol

## VERIFIED

- Task `T-A2-006-ads-seo-wordpress-patrol` is ACTIVE in [`CURRENT_STATUS.md`](../../../CURRENT_STATUS.md).
- A2 previously verified 7 To-B live URLs as HTTP 200 on 2026-05-26; 5 planned slugs were 404 (source: `workbook/reviews/JOB-A2-B2B-CASE-ADS-20260526/review_request.md`).
- WP draft exists: Post ID `1696`, title `MAPLAB 企業外燴與活動茶點案例審核草稿 Round 008`, status `草稿` (source: `reports/wp_draft_round_009.md`, 2026-05-27).
- Draft persistence was reloaded and confirmed in prior run; no publish action recorded.
- `pitfalls.md` explicitly requires live URL verification before writing and warns against planned-slug drift.

## REASONABLE INFERENCE

- Current To-B content architecture is usable for ads/SEO landing alignment without creating new top-level pages first.
- Immediate value is in case-proof enrichment (images/alt/captions/case blocks) on existing live URLs rather than new slug expansion.

## MISSING DATA (2026-06-01 run)

- No fresh 2026-06-01 live HTTP recheck executed in this run.
- No new authenticated WP backend visual capture in this run.
- No proof yet that 30 WebP assets were uploaded (previously blocked by Chrome extension file chooser permission).

## Next Concrete Command

```bash
cd /Users/pagemacmini/maplab-ai-handbook
python3 - <<'PY'
import requests
urls = [
  "https://www.maplabkitchen.com/corporate-catering-tainan/",
  "https://www.maplabkitchen.com/corporate-tea-party-desserts/",
  "https://www.maplabkitchen.com/tainan-corporate-opening-tea-catering/",
  "https://www.maplabkitchen.com/brand-esg-catering-service/",
  "https://www.maplabkitchen.com/press-conference-catering/",
  "https://www.maplabkitchen.com/vip-expo-catering-business-meeting/",
  "https://www.maplabkitchen.com/daxin-art-museum-opening-catering/",
]
for u in urls:
    try:
        print(requests.get(u, timeout=12).status_code, u)
    except Exception as e:
        print("ERR", u, e)
PY
```
