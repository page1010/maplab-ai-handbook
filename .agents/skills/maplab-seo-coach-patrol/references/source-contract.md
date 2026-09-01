# SEO source contract

## Authority order

1. Current live HTTP/WordPress public REST readback.
2. Current authenticated GSC/analytics readback when already authorized and locally available.
3. The newest dated, verified review receipt.
4. `docs/seo-keyword-map.md` and `docs/a2a3/live-wordpress-audit.md` as planning context.
5. Older notes and model memory only as leads, never current truth.

When sources conflict, retain both observations, use the newer direct evidence, and correct the durable truth source.

## Required public fields

- `robots.txt` status and sitemap declaration.
- sitemap status, child sitemap URLs, URL count, and latest `lastmod` when present.
- WordPress published post/page counts from response headers.
- For the fixed monitored URL set: final URL, HTTP status, title, meta description, robots directive, canonical, H1 count/value, JSON-LD block count, image count, missing-alt count, and body hash.
- Method fingerprint: probe version, fixed URL set, checks, timeout, and acceptance contract.

Whole-corpus availability and inbound-link claims require the exact stdout of `scripts/public_seo_corpus_audit.py`. The receipt must bind the post/page sitemap URLs and hashes, method fingerprint, complete URL count, per-page status/body hash/internal-link set, inbound-source map, and zero-inbound list. A fixed monitored sample is not sufficient evidence for a whole-corpus statement.

A no-delta decision requires a second same-method probe or a compact derivative receipt that binds the saved baseline path and SHA-256, both method fingerprints, the exact comparison decision, and zero external effects. A baseline with `previous=null` is not a no-delta receipt.

## Performance fields

Use GSC/analytics only when the exact date window, property, dimensions, and freshness are recorded. Minimum comparison fields are query, page, clicks, impressions, CTR, average position, current window, previous comparable window, and extraction timestamp.

If access is absent or stale, label performance `MISSING`. Public indexing or page health does not prove traffic or Ads performance.

## Content and claim authority

Current prices, availability, discounts, client names, event counts, testimonials, certifications, food-safety guarantees, and performance claims require a current named source. Otherwise keep them `MISSING` and exclude them from drafts.

MAPLAB copy must obey the repo brand/safety references, including the prohibitions on medical-grade dietary claims and unsupported ESG/certification language.

## Privacy routing

Public pages and synthetic fixtures may be processed by public-safe workers. Customer records, LINE conversations, Drive originals with personal information, authenticated browser state, credentials, and private commercial documents remain in the local domain and are never included in a Hermes/public research packet.
