# A2 Eye Gate - Public/Auth SEO Gate

Date: 2026-06-24 23:29 Asia/Taipei  
Role: A2-EYE-GATE worker  
Environment: `/Users/pagemacmini/maplab-ai-handbook`  
Scope: public HTTP / public WordPress REST / public sitemap only  
Write target: `workbook/reviews/JOB-DISPATCH-PACKAGES-20260624/a2_eye_gate.md`

## Boundaries

- Did not log in to WordPress, Google Search Console, Google Ads, Meta Ads, or any authenticated surface.
- Did not publish, edit WordPress, change Rank Math, refresh sitemap settings, request indexing, read secrets, commit, or push.
- This file separates public proof from authenticated proof still missing.

## Files Read First

1. `CURRENT_STATUS.md`
2. `TASK_QUEUE.md`
3. `pitfalls.md`
4. `workbook/reviews/JOB-DISPATCH-HUMAN-EYE-AUDIT-20260624/completion_human_eye_audit.md`
5. `workbook/reviews/JOB-DISPATCH-PACKAGES-20260624/routing.md`
6. `docs/a2a3/a2-rest-inventory-20260624.md`
7. `docs/a2a3/a2-seo-plan-refresh-20260623.md`

## Public Proof

Observed by public GET only on 2026-06-24 15:29 UTC / 23:29 Asia/Taipei.

### Public REST Counts

| Surface | Endpoint | Result |
|---|---|---|
| Posts REST | `https://www.maplabkitchen.com/wp-json/wp/v2/posts?per_page=100&page=1&_fields=id,date,modified,slug,link,title,status,type,categories` | HTTP 200, body count `58` |
| Pages REST | `https://www.maplabkitchen.com/wp-json/wp/v2/pages?per_page=100&page=1&_fields=id,date,modified,slug,link,title,status,type` | HTTP 200, body count `6` |

### ICC Landing Page

| Check | Result |
|---|---|
| Public REST slug | `icc-tainan-catering` found |
| ID / status / type | `1829` / `publish` / `post` |
| Modified | `2026-06-16T20:49:21` |
| Public URL | `https://www.maplabkitchen.com/icc-tainan-catering/` |
| Front-end HTTP | `200` |
| Front-end title / H1 | `大臺南會展中心活動外燴｜企業茶點與貴賓接待｜MAPLAB` |
| Meta description | `大臺南會展中心外燴與企業茶點案例。MAPLAB Kitchen 提供台南會展活動餐點、手指食物、飲品與貴賓接待餐桌配置，適合會議、展覽、開幕與品牌活動。` |
| Canonical | `https://www.maplabkitchen.com/icc-tainan-catering/` |
| Robots meta | `follow, index, max-snippet:-1, max-video-preview:-1, max-image-preview:large` |
| CTA signal | LINE / `@maplab` text found in page HTML |

Verdict: ICC is publicly live and indexable by page metadata. This is not the same as sitemap inclusion or GSC indexed proof.

### B2B Pillar And Support Pages

All listed pages are public REST `publish` posts, front-end HTTP `200`, canonical to their own URL, robots `follow, index`, and include LINE CTA signal.

| Slug | ID | Front-end title / H1 | Sitemap |
|---|---:|---|---|
| `corporate-catering-tainan` | 586 | `台南企業外燴推薦｜會議茶點、開幕茶會與品牌活動規劃｜MAPLAB` | present in `post-sitemap.xml` |
| `corporate-tea-party-desserts` | 924 | `台南會議茶點外燴｜研討會、講座與企業活動餐點｜MAPLAB` | present |
| `tainan-corporate-opening-tea-catering` | 1205 | `台南開幕茶會外燴｜開幕典禮流程與品牌接待餐點｜MAPLAB` | present |
| `brand-esg-catering-service` | 945 | `台南品牌活動外燴｜發表會、VIP 接待與展覽開幕餐點｜MAPLAB` | present |
| `press-conference-catering` | 879 | H1 `記者會餐點推薦｜讓品牌活動更有記憶點的關鍵一刻`; title `記者會餐點推薦：5 步打造高質感品牌活動餐飲｜MAPLAB` | present |
| `vip-expo-catering-business-meeting` | 261 | H1 `展覽外燴推薦｜VIP 點心吧與商務派對接待首選服務:MAPLAB Kitchen`; title `台南展覽外燴推薦 2026｜VIP 點心吧、商務接待、品牌活動外燴 - MAPLAB` | present |
| `daxin-art-museum-opening-catering` | 1048 | H1 `大新美術館開幕外燴｜展覽開幕茶會餐點案例｜MAPLAB Kitchen`; title `展覽開幕茶會外燴紀錄：2025 大新美術館藝術與餐飲交集｜MAPLAB` | present |

Public reading: the B2B cluster is readable now. The plan should optimize existing pillar/support pages first instead of creating duplicate generic posts.

### Public Collision Check For Proposed New Slugs

| Candidate slug | Public posts REST | Public pages REST | Front-end |
|---|---|---|---|
| `campus-seminar-catering-tainan` | no match | no match | 404 |
| `school-event-catering-tainan` | no match | no match | 404 |
| `nanke-tech-company-catering` | no match | no match | 404 |
| `reception-center-vip-catering-tainan` | no match | no match | 404 |

Public reading: there is no public collision for the proposed case-specific slugs. This does not prove there is no private draft, scheduled post, trashed post, or duplicate custom post type.

### Robots And Sitemap

| Surface | Result |
|---|---|
| `robots.txt` | HTTP 200, points to `https://www.maplabkitchen.com/sitemap_index.xml` |
| `sitemap_index.xml` | HTTP 200, includes `post-sitemap.xml`, `page-sitemap.xml`, and Elementor/header-footer sitemap entries |
| `post-sitemap.xml` | HTTP 200, `57` URL entries |
| `page-sitemap.xml` | HTTP 200, `5` URL entries |
| ICC in `post-sitemap.xml` | not found |
| B2B support pages in `post-sitemap.xml` | found |
| proposed candidate slugs in sitemap | not found |

Sitemap verdict: `icc-tainan-catering` is live but absent from the public post sitemap. Treat this as sitemap/indexing registration drift, not as unpublished-page evidence.

## Authenticated Proof Still Missing

These cannot be proven by public HTTP/REST:

| Gate | Missing proof | Why public proof is insufficient |
|---|---|---|
| Authenticated duplicate draft check | WordPress all-status search for drafts, scheduled, private, trash, revisions/CPT duplicates for ICC and candidate slugs | Public REST only shows published posts/pages |
| Rank Math meta readback | Stored Rank Math SEO title, description, robots, canonical, focus keyword, sitemap inclusion settings for ICC and B2B cluster | Public HTML shows rendered metadata, not the admin/plugin stored source or cache state |
| GSC URL Inspection | Google-selected canonical, indexing state, crawl/index coverage, last crawl, sitemap discovery for ICC and key B2B URLs | Front-end `index` robots meta does not prove Google has indexed or accepted the URL |
| Sitemap/indexing refresh | Whether Rank Math sitemap cache has refreshed, whether ICC enters `post-sitemap.xml` after approved refresh, whether sitemap was submitted/seen in GSC | Current public sitemap proves the gap exists, not the cause |
| Ads landing alignment, if needed | Current Google Ads final URL, URL expansion, conversion action, campaign status/budget, Meta destination/audience | Public landing page proof does not prove authenticated ad backend settings |

## Owner Decision Card

### Decision Available Now

Owner can decide the next safe action because the public side is clear:

- ICC is live, public, canonical, and robots-indexable by HTML metadata.
- B2B pillar/support pages are live and readable.
- ICC is still missing from `post-sitemap.xml`.
- Candidate new case slugs do not collide publicly.
- Authenticated gates remain explicitly unproven.

### Recommended Approval

Approve a read-only authenticated gate check, not publishing:

`批准 A2-EYE-GATE 下一步：只做 authenticated read-only duplicate draft check + Rank Math meta readback + GSC URL Inspection + sitemap/indexing status check；不發布、不改 Ads/Meta、不改預算、不大量改文。`

### Do Not Approve Yet

- Do not call A2 `runtime_verified`.
- Do not publish new case posts.
- Do not claim Google indexing is fixed.
- Do not change Google Ads / Meta Ads / GTM / Pixel / budget from this evidence alone.
- Do not treat public REST no-collision as private draft no-collision.

### If Owner Wants The Smallest Execution Scope After Auth Checks

Recommended first execution package:

1. `A2-OPT-007` - ICC page: keep page live, check stored Rank Math values, fix sitemap/indexing registration first.
2. `A2-OPT-001` - corporate B2B pillar: clean brand/copy and internal links to the cluster.
3. Hold new case drafts until authenticated duplicate check and A4 asset/public-name permission are complete.

## Next Smallest Actions

1. Authenticated duplicate draft check:
   - In logged-in WordPress, read-only search All Posts / All Pages / scheduled / draft / private / trash for:
     - `icc-tainan-catering`
     - `campus-seminar-catering-tainan`
     - `school-event-catering-tainan`
     - `nanke-tech-company-catering`
     - `reception-center-vip-catering-tainan`
   - Save proof as a table with `slug`, `post_id`, `status`, `type`, `modified`, `edit_url`, and screenshot/readback path.

2. Rank Math meta readback:
   - Read stored SEO title, description, canonical, robots, sitemap/indexing-related fields for ICC and the seven B2B cluster posts.
   - Compare stored values to public HTML metadata.
   - Do not change values unless Owner separately approves an execution package.

3. GSC URL Inspection:
   - Inspect ICC first: `https://www.maplabkitchen.com/icc-tainan-catering/`.
   - Then inspect `corporate-catering-tainan` and the direct cluster support pages.
   - Record `inspection_result`, Google-selected canonical, user-declared canonical, indexing state, last crawl, and sitemap discovery.
   - Request indexing only if Owner approves that action after readback.

4. Sitemap/indexing refresh:
   - Recheck public `sitemap_index.xml` and `post-sitemap.xml` before any action.
   - If Owner approves, refresh the Rank Math/WordPress sitemap cache or equivalent safe admin action.
   - Recheck whether ICC appears in `post-sitemap.xml`.
   - If still absent, capture Rank Math sitemap settings/plugin status read-only before changing anything else.

5. Ads alignment only if A3/Owner needs it:
   - Authenticated read-only Google Ads / Meta Ads capture for final URL, URL expansion, conversion action, budget/status, and destination/audience.
   - Keep this separate from A2 SEO public proof.

## State Verdict

| State | Verdict | Reason |
|---|---|---|
| `code_candidate` | passed as file/proof package | No code changed; public proof package is coherent and bounded |
| `approval_ready` | yes | Owner can approve the next authenticated read-only gate from this evidence |
| `runtime_verified` | no | No authenticated WP/Rank Math/GSC proof and sitemap drift is unresolved |
| `owner_visible_done` | no | No authenticated eye proof or Google indexing/sitemap completion receipt |

Final verdict: A2 SEO public/auth gate is `approval_ready` for the next authenticated read-only check. It is not `runtime_verified` or `owner_visible_done`.

## Resume Prompt

```text
我是 A2-EYE-GATE worker，環境 /Users/pagemacmini/maplab-ai-handbook。
先讀 CURRENT_STATUS.md、TASK_QUEUE.md、pitfalls.md、workbook/reviews/JOB-DISPATCH-PACKAGES-20260624/a2_eye_gate.md。
本輪 public GET 已確認 ICC post 1829 live/indexable、B2B cluster pages live/readable、candidate slugs public no-collision、ICC absent from post-sitemap.xml。
下一步只做 authenticated read-only gate：WordPress duplicate drafts/scheduled/private/trash、Rank Math stored meta、GSC URL Inspection、sitemap/indexing status。
不要登入以外的變更，不發布、不改 Ads/Meta、不讀 secrets、不 commit/push，除非 Owner 另行明確批准。
```
