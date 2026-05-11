# Live WordPress / Rank Math Fact Check — 2026-05-11

> 原則：repo 記錄只用來減少斷點；現況必須以 WordPress / Rank Math 接口與前台輸出為準。

## Interface Sources Used

- WordPress site root: `GET https://www.maplabkitchen.com/wp-json/`
- WordPress pages: `GET /wp-json/wp/v2/pages?per_page=100`
- WordPress posts: `GET /wp-json/wp/v2/posts?per_page=100`
- WordPress slug lookup: `GET /wp-json/wp/v2/pages?slug=<slug>` and `GET /wp-json/wp/v2/posts?slug=<slug>`
- Rank Math route discovery: `GET /wp-json/`, filtered for `/rankmath/v1/*`
- Rank Math public status route: `GET /wp-json/rankmath/v1/status`
- Rank Math private endpoints tested:
  - `GET /wp-json/rankmath/v1/dashboardWidget`
  - `GET /wp-json/rankmath/v1/an/post/1250`
  - `GET /wp-json/rankmath/v1/an/postsRows`
  - `GET /wp-json/rankmath/v1/links/posts`
- Frontend HTML head checked for Rank Math output:
  - homepage
  - `corporate-catering-tainan`
  - `catering-one-year-old-party-tainan`
  - `tainan-corporate-opening-tea-catering`
  - `brand-esg-catering-service`
  - `corporate-tea-party-desserts`

## Hard Facts From Live WordPress

### Published content counts

- Published pages visible via public REST: **6**
- Published posts visible via public REST: **57**
- Homepage `page_on_front`: **1250**
- Homepage live URL: `https://www.maplabkitchen.com/`

### Published pages

| ID | Slug | URL | Title |
|---:|------|-----|-------|
| 1674 | `privacy-policy` | `https://www.maplabkitchen.com/privacy-policy/` | 隱私權政策 |
| 1250 | `homepage-v2` | `https://www.maplabkitchen.com/` | 台南外燴｜MAPLAB Kitchen CATERING SERVICE |
| 209 | `join-maplab-catering-partner` | `https://www.maplabkitchen.com/join-maplab-catering-partner/` | 外燴加盟合作平台-加入我們 |
| 44 | `about-us-maplabkitchen` | `https://www.maplabkitchen.com/about-us-maplabkitchen/` | About us |
| 46 | encoded Chinese slug | `https://www.maplabkitchen.com/工商代購服務/` | 工商代購服務 |
| 15 | `tainan-party-venue` | `https://www.maplabkitchen.com/tainan-party-venue/` | 派對流程怎麼規劃？場地、餐點、預算一次搞懂！ |

## Planned Slugs Are Not Live

These planned workbench slugs returned **0 matches** in both `pages` and `posts`, and front-end requests returned 404:

| Planned slug | Live WP match |
|--------------|---------------|
| `catering-corporate-tainan` | 0 |
| `catering-birthday-party-tainan` | 0 |
| `catering-wedding-tainan` | 0 |
| `opening-event-catering-tainan` | 0 |
| `meeting-refreshment-catering-tainan` | 0 |
| `brand-event-catering` | 0 |
| `school-event-catering-tainan` | 0 |

This means the A2/A3 workbench slugs are **not currently published WordPress URLs**.

## Existing Live Pages/Posts That Actually Own The Intent

| Intent | Live slug | Type | ID | URL |
|--------|-----------|------|---:|-----|
| B2B / corporate catering | `corporate-catering-tainan` | post | 586 | `https://www.maplabkitchen.com/corporate-catering-tainan/` |
| Opening tea party | `tainan-corporate-opening-tea-catering` | post | 1205 | `https://www.maplabkitchen.com/tainan-corporate-opening-tea-catering/` |
| Brand / ESG / VIP event | `brand-esg-catering-service` | post | 945 | `https://www.maplabkitchen.com/brand-esg-catering-service/` |
| Meeting / corporate tea desserts | `corporate-tea-party-desserts` | post | 924 | `https://www.maplabkitchen.com/corporate-tea-party-desserts/` |
| Week one / zhuazhou | `catering-one-year-old-party-tainan` | post | 498 | `https://www.maplabkitchen.com/catering-one-year-old-party-tainan/` |

## Rank Math Facts

### Rank Math is active on frontend

The checked frontend pages include:

- `<!-- Search Engine Optimization by Rank Math PRO - https://rankmath.com/ -->`
- `<!-- /Rank Math WordPress SEO plugin -->`

### Rank Math REST routes exist

`GET /wp-json/` exposes many `/rankmath/v1/*` routes, including:

- `/rankmath/v1/status`
- `/rankmath/v1/updateMeta`
- `/rankmath/v1/updateMetaBulk`
- `/rankmath/v1/updateSchemas`
- `/rankmath/v1/an/post/(?P<id>\d+)`
- `/rankmath/v1/an/postsRows`
- `/rankmath/v1/links/posts`
- `/rankmath/v1/link-genius/*`

### Rank Math private analytics/score endpoints require authentication

Without WordPress auth, these endpoints returned 401:

- `/wp-json/rankmath/v1/dashboardWidget`
- `/wp-json/rankmath/v1/an/post/1250`
- `/wp-json/rankmath/v1/an/postsRows`
- `/wp-json/rankmath/v1/links/posts`
- `/wp-json/rankmath/v1/link-genius/posts`

Current shell environment has no WordPress auth variables:

- `WP_BASE_URL`: unset
- `WP_USERNAME`: unset
- `WP_APP_PASSWORD`: unset
- `WP_USER`: unset

Therefore current session can verify public REST, frontend meta, schemas, and live slug status, but cannot verify private drafts, Rank Math score rows, or internal Rank Math analytics until authenticated.

## Frontend Meta Output Checked

### Homepage `/`

- Title: `台南外燴推薦｜週歲派對・婚禮・企業活動｜MAPLAB Kitchen`
- H1: `台南外燴｜MAPLAB Kitchen CATERING SERVICE`
- Canonical: `https://www.maplabkitchen.com/`
- Robots: `follow, index`
- Schema includes: `FoodEstablishment`, `Organization`, `WebSite`, `WebPage`, `Article`, `Service`, `Offer`

### Existing corporate post `/corporate-catering-tainan/`

- Title: `台南企業外燴推薦｜2026 品牌活動、展會、記者會規劃 - MAPLAB`
- H1: `台南企業外燴推薦｜品牌活動、展會、同學會一站式規劃`
- Canonical: `https://www.maplabkitchen.com/corporate-catering-tainan/`
- Robots: `follow, index`
- Schema includes: `FoodEstablishment`, `Organization`, `BreadcrumbList`, `FAQPage`

### Week-one post `/catering-one-year-old-party-tainan/`

- Title: `台南週歲派對外燴推薦｜菜單、場地、費用完整懶人包 2026`
- H1: `【2026 最新】台南週歲派對外燴懶人包｜菜單、場地、價格一次搞懂！`
- Canonical: `https://www.maplabkitchen.com/catering-one-year-old-party-tainan/`
- Robots: `follow, index`
- Schema includes: `FoodEstablishment`, `Organization`, `BreadcrumbList`, `WebPage`, `BlogPosting`

### Existing opening post `/tainan-corporate-opening-tea-catering/`

- Title: `台南企業開幕茶會外燴｜2026 讓品牌第一印象加分的餐飲規劃`
- H1: `台南企業開幕茶會外燴｜讓品牌第一印象加分的餐飲規劃`
- Canonical: `https://www.maplabkitchen.com/tainan-corporate-opening-tea-catering/`
- Robots: `follow, index`
- Schema includes: `FoodEstablishment`, `Organization`, `BreadcrumbList`, `WebPage`, `BlogPosting`

### Existing brand post `/brand-esg-catering-service/`

- Title: `品牌ESG活動外燴：3 大類型從頒獎典禮到科技發表｜MAPLAB`
- H1: `台南企業品牌活動外燴｜品牌開幕、記者會、VIP 接待全方位服務`
- Canonical: `https://www.maplabkitchen.com/brand-esg-catering-service/`
- Robots: `follow, index`
- Schema includes: `FoodEstablishment`, `Organization`, `BreadcrumbList`, `WebPage`, `BlogPosting`

### Existing meeting/tea post `/corporate-tea-party-desserts/`

- Title: `企業茶會點心外燴推薦：2026 精緻茶飲規劃｜MAPLAB Kitchen`
- H1: `企業茶會點心外燴推薦｜精緻甜點＋茶飲點心規劃｜MAPLAB Kitchen`
- Canonical: `https://www.maplabkitchen.com/corporate-tea-party-desserts/`
- Robots: `follow, index`
- Schema includes: `FoodEstablishment`, `Organization`, `BreadcrumbList`, `WebPage`, `BlogPosting`, `FAQPage`

## What Actually Happened

1. The A2/A3 workbench invented or prepared slugs that are not live WordPress objects.
2. The live site already has posts covering the same or adjacent intents.
3. The current public site structure is not "8 landing pages"; it is 6 pages + 57 posts.
4. Rank Math PRO is active and outputs frontend SEO tags/schema.
5. Rank Math private analytics and scoring cannot be verified without authenticated WP REST access.
6. The workbench must stop treating local draft slugs as if they are live WordPress pages.

## Correct Next Action

Do not create new public pages blindly.

Next A2 action should be:

1. Authenticate WordPress REST if private drafts and Rank Math score rows must be inspected.
2. Pull current live post/page inventory from WP REST before writing.
3. Map planned B2B work to existing live owners:
   - `corporate-catering-tainan`
   - `tainan-corporate-opening-tea-catering`
   - `brand-esg-catering-service`
   - `corporate-tea-party-desserts`
4. Decide per intent:
   - update existing post,
   - convert existing post into stronger landing-style post,
   - create a new page only if it has a unique intent and canonical/internal-link plan.
5. Only then prepare Rank Math updates.

## Resume Prompt

```
角色：A2 / A1 fact-check
任務：WordPress + Rank Math 現況接口核對
現場事實：
- WP public REST: 6 published pages, 57 published posts
- homepage page_on_front: 1250
- planned slugs catering-corporate-tainan / opening-event-catering-tainan / meeting-refreshment-catering-tainan / brand-event-catering / school-event-catering-tainan are not live; REST slug lookup returns 0 and frontend is 404
- existing live intent owners: corporate-catering-tainan, tainan-corporate-opening-tea-catering, brand-esg-catering-service, corporate-tea-party-desserts, catering-one-year-old-party-tainan
- Rank Math PRO is active on frontend and outputs meta/schema
- Rank Math analytics/link endpoints return 401 without WP auth
不要再靠 repo 紀錄判斷 live site。先用接口查，再規劃。
```
