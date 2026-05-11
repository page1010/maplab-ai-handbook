# A2 Rank Math Keyword Recovery — 2026-05-11

執行 Agent：A1/Codex acting as A2 live SEO repair

## Purpose

依 Owner 指令，停止依賴 repo 紀錄推斷 WordPress 現況，改用 live WordPress REST / Rank Math REST / 前台 HTML 驗證來修復下滑關鍵字。

## Live Targets Updated

| Intent | Live owner | WP object | Update |
|---|---|---:|---|
| 台南外燴推薦 / 台南到府外燴 / 台南派對外燴 | `/` | page 1250 | Rank Math title / description / focus keyword |
| 台南到府外燴 / 台南派對外燴 | `/tainan-catering-guide/` | post 683 | post title + Rank Math + support block + stale link repair |
| 台南企業外燴 | `/corporate-catering-tainan/` | post 586 | post title + Rank Math + B2B hub internal links |
| 台南開幕茶會 / 開幕茶會流程 | `/tainan-corporate-opening-tea-catering/` | post 1205 | post title + Rank Math + flow section |
| 台南品牌活動外燴 | `/brand-esg-catering-service/` | post 945 | post title + Rank Math + brand-event support block |
| 台南會議茶點 | `/corporate-tea-party-desserts/` | post 924 | post title + Rank Math + meeting-refreshment support block |
| 台南週歲派對外燴 | `/catering-one-year-old-party-tainan/` | post 498 | Rank Math + link bridge to gender reveal / guide |
| 性別揭曉派對 / Gender Reveal Party | `/gender-reveal-party-tips/` | post 332 | post title + Rank Math; post_content marker added but Elementor body overrides rendering |

## What Changed

1. Created `tools/wp_rankmath_recovery.py`.
2. Used authenticated WP REST to confirm administrator access.
3. Used Rank Math REST `/wp-json/rankmath/v1/updateMeta` for SEO title, meta description, and focus keyword.
4. Updated selected post titles where the live H1 / SERP title was misaligned with target intent.
5. Added small marked support blocks to live owner posts, not new competing pages.
6. Repaired stale internal links pointing at draft / 404 slugs:
   - `/catering-corporate-tainan/` → `/corporate-catering-tainan/`
   - `/catering-birthday-party-tainan/` → `/catering-one-year-old-party-tainan/`
   - `/opening-event-catering-tainan/` → `/tainan-corporate-opening-tea-catering/`
   - `/meeting-refreshment-catering-tainan/` → `/corporate-tea-party-desserts/`
   - `/brand-event-catering/` → `/brand-esg-catering-service/`

## Verification

Review bundle:

`workbook/reviews/JOB-A2-RANKMATH-LIVE3-20260511/`

Verified:

- Rank Math REST updates returned OK for all 8 targets.
- WP REST content/title updates returned OK for 7 content targets.
- Frontend `<title>` and `<meta name="description">` now contain the intended keyword owner terms.
- Frontend stale link check across the 8 target URLs returned 0 stale slug hits.
- Support block markers render on all non-Elementor target posts.

Known limitation:

- `/gender-reveal-party-tips/` is rendered by Elementor data rather than normal `post_content`; Rank Math meta/title updates are live, but the appended `post_content` support block does not render on the frontend. Do not treat post_content-only edits as sufficient for Elementor pages.

## Next SEO Actions

1. In Rank Math Analytics, monitor query/page movement for:
   - 台南到府外燴
   - 台南派對外燴
   - 台南會議茶點
   - 台南品牌活動外燴
   - 開幕茶會流程
   - 性別揭曉派對
2. If planned workbench slugs were submitted or linked externally, add 301 redirects to the live owner URLs.
3. For Elementor-rendered posts, edit through Elementor data or wp-admin UI, not only WP REST post content.
4. Re-check GSC after Google recrawl; do not judge ranking movement on the same day.

## Google Discovery / Recrawl Evidence

Review bundle:

`workbook/reviews/JOB-A2-GOOGLE-RECRAWL-20260511/`

Done:

- Verified `robots.txt` allows public crawling and points to `https://www.maplabkitchen.com/sitemap_index.xml`.
- Verified all 8 updated URLs are present in Rank Math sitemaps:
  - homepage in `page-sitemap.xml`
  - 7 post URLs in `post-sitemap.xml`
- Verified all 8 URLs return HTTP 200, are not `noindex`, have meta descriptions, and include the Rank Math frontend marker.
- Submitted all 8 URLs through Rank Math Instant Indexing endpoint:
  - endpoint: `/wp-json/rankmath/v1/in/submitUrls`
  - accepted response: `Successfully submitted 8 URLs.`

Boundary:

- Google Search Console URL Inspection API / sitemap API could not be used from the current local credential set: `google-token.json` only has Drive/Sheets scopes, and the configured `mcp-server-gsc` expects a service-account credential (`private_key` + `client_email`) rather than the current OAuth client file.
- Google's old sitemap ping endpoint is deprecated; do not use it as a submission path.
- For normal WordPress pages, Google Search Console's "Request Indexing" remains a UI action, while URL Inspection API is for status inspection.
