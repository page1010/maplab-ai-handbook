# MAPLAB SEO priority matrix — 2026-09-01

Scope: public/read-only. No WordPress, Ads, Rank Math, customer messaging, or credential action was performed.

## Decision

`DETAIL_ACTION` first. The smallest verified defect is the invalid FAQ JSON-LD on post 879. The broader content/cannibalization work remains a plan until fresh GSC query-page evidence is available.

| Priority | Evidence | Finding | Route | Acceptance |
|---|---|---|---|---|
| P1 | `VERIFIED` | `/press-conference-catering/` has 1 invalid JSON-LD block: 2/3 parse, raw control character at position 441 | One-variable preview-only patch proposal | candidate parses 3/3; visible/SEO holdout unchanged |
| P1 | `VERIFIED` | The same page has 0 inbound sources among 64 sitemap post/page URLs | Internal-link plan after schema proposal | identify 2-3 context-fit source pages; no live edits |
| P2 | `VERIFIED` | `elementor-hf-sitemap.xml` exposes 2 template URLs that are index/follow but canonical to home | Technical plan | remove/exclude templates from sitemap only after exact setting/rollback approval |
| P2 | `VERIFIED` | 3 sitemap pages have multiple H1; `/工商代購服務/` lacks meta description | URL-specific detail queue | one URL and one changed variable per approved action |
| P3 | `VERIFIED` | Corporate/Daxin images reuse generic alt; VIP has filename-like alt | Accessibility/image-context plan | source-specific alt proposals, no keyword stuffing |
| P3 | `VERIFIED` | Corporate hub schema is valid but thinner than peer pages | Plan only | add schema only when page type/source authority is explicit |
| — | `MISSING` | GSC URL Inspection, query/page clicks, impressions, CTR, position, CWV | Do not infer rankings | obtain a dated exact window before strategy experiment |

## Baseline anchors

- robots SHA-256: `786328b38f3e84b4cfdee38841c44fac4f114912effaec009faee7f3b6c560d6`
- sitemap-index SHA-256: `b0846685bc378dfeed2db304e07e6221eb460b3fb0a409f80f0d54d49e298b19`
- post sitemap: 58 URLs; URL-set SHA-256 `6aeaf814acb2c5a9a4350779a8ed1603689a3fa0ecacd6072fca5922c2b56b25`
- page sitemap: 6 URLs; URL-set SHA-256 `6e32f560e09adc660ac569d212c8a9b127ab188ba93015deac443b17b4614000`
- normalized probe method fingerprint: `cd028320bc30cba1c78da38ef1cb2be6a02a11c91b3873b47192463b047de5a0`
- all-corpus audit method fingerprint: `bb802a57fcb5ebcfa9fed1a5cd99b6e5fe3992488c1cee6e52e0e90888aea083`
- replayable evidence: `public_seo_no_delta_receipt.json` and `public_seo_corpus_audit.json`

Full page body hashes remain diagnostic only. They do not trigger Hermes because dynamic HTML can change without an SEO-semantic delta.

## Why not write another general article

The live site already has overlapping generic, corporate, venue, tea, opening, and cost clusters. Without fresh GSC query-page overlap, a new generic slug risks cannibalization. Current work therefore fixes a concrete parser defect first, then requests evidence for cluster planning.
