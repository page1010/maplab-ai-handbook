# P0 Curriculum — SEO ranking / keyword tracking

- curriculum id: `P0-SEO-RANKING-KEYWORD`
- target tier: `G1 -> G2`
- baseline model: `qwen2.5:14b`
- eval size: `20`
- data mode: synthetic, de-identified, read-only

## What

Teach a local model to separate live ranking evidence from strategy matrices,
planned slugs, stale checks, wrong locale/device, and publishing/Ads actions.

## So What

The existing A2 matrix is useful strategy metadata but is not current GSC rank
evidence. Treating it as live performance would fabricate progress and route
work to the wrong page or keyword.

## Now What

The 20 fixed cases cover:

1. live URL versus planned slug;
2. wrong keyword rank;
3. stale rank timestamp;
4. locale/device mismatch;
5. missing GSC evidence;
6. strategy matrix versus live observation;
7. cannibalization;
8. conversion-setting write boundary;
9. Ads mutation boundary;
10. content-publish boundary;
11. missing search-volume source;
12. branded versus non-branded query;
13. query/landing-page mismatch;
14. missing indexation evidence;
15. 404 page handling;
16. missing comparison period;
17. private customer-data exclusion;
18. target keyword is not achieved rank;
19. unsupported competitor claims;
20. rank-delta calculation with fixed dates.

Candidate v0.1 filters entity/date/source/sensitivity metadata before the model,
then validates the JSON contract. It does not publish, modify Ads, or write GSC.

## Rubric and promotion

The same eight checks and safety gate in the Investment curriculum apply. A
promotion additionally requires live public/GSC evidence to be labeled by
source and timestamp. Strategy-only rows must never be promoted to observed rank.

## Loop Back

Weekly review can add a synthetic hard negative when a verified live page,
query, date, locale, or indexation mismatch escapes the gate. Raw customer or
account-level query data is excluded by default.
