# Owner Approval Card

TASK_ID: T-A2-006 / ICCTAINAN-20260615
ROLE: A2 Ads SEO WordPress Patrol + A3 Ads + A4 Assets
STATUS: approval_ready

## A2-SEO-ICCTN-001

WHY:

大臺南會展中心 is a narrow venue-intent keyword cluster. MAPLAB already has strong B2B pages, and the new Drive folder gives a real venue case to support a dedicated landing page.

EVIDENCE:

- Official venue site and services page confirm the venue and catering-service context.
- MAPLAB has live B2B pages for corporate catering, meeting tea, opening tea, and expo/VIP reception.
- Drive folder `1wTu2cfZVSUMwSb0avEhSAd6sdVZZa2pT` contains a recent 大台南會展中心 case candidate with 22 media files.

PLAN:

- Create a WordPress unpublished draft:
  - Slug: `icc-tainan-catering`
  - SEO title: `大臺南會展中心活動外燴｜企業茶點與貴賓接待｜MAPLAB`
  - H1: `大臺南會展中心活動外燴｜企業茶點與貴賓接待規劃`
- Use public-safe case label until Owner confirms whether the full institutional name can appear.
- Add internal links to the four existing B2B pages.
- Keep page unpublished until Owner review.

EXPECTED_EFFECT:

- Capture venue-specific long-tail search intent.
- Give Google Ads a page-specific final URL.
- Turn the new event material into SEO proof instead of a generic gallery.

IMPACT_SCOPE:

- New WordPress draft only.
- No existing live page changes.
- No Rank Math paid setting change.
- No publish action.

RISKS:

- Search volume may be small.
- Full event/institutional name may be sensitive.
- Photos may contain people, private slides, badges, or visible internal materials.

ROLLBACK:

- Delete or keep the draft unpublished.
- Do not publish until Owner approves final copy and image selection.

VALIDATION:

- Draft exists and is unpublished.
- Draft page checklist passes title/meta/FAQ/CTA/internal-link/image-alt requirements.
- No private data or internal date appears in public copy.

OWNER_DECISION:

```text
批准 A2-SEO-ICCTN-001，只建立 WordPress 未發布草稿，不發布。
```

or:

```text
退回 A2-SEO-ICCTN-001，先補完整圖片 QA。
```

## A4-ASSET-ICCTN-001

WHY:

The Drive folder has enough still images and video files to build a case asset set, but it needs visual QA before public use.

EVIDENCE:

- 11 JPG, 3 HEIC, 6 MP4, 2 MOV listed from the folder.

PLAN:

- Select 6-10 still images and optional 1 short reel cut.
- Exclude faces, private meeting material, badges, QR codes, and dominant third-party logos.
- Convert selected images to WebP sizes for hero, case body, Meta 4:5, and optional story cover.
- Produce final alt/caption mapping.

EXPECTED_EFFECT:

- Give the SEO page and Meta creative a venue-specific visual proof layer.

IMPACT_SCOPE:

- Drive read-only review.
- Local converted assets only after approval.
- No WordPress upload until A2 publish/draft workflow is approved.

RISKS:

- Image content may be unsuitable for public use.
- HEIC and video files may require conversion tooling and visual review time.

ROLLBACK:

- Keep all Drive files untouched.
- Discard local converted derivatives if Owner rejects them.

VALIDATION:

- Asset manifest lists selected file IDs, filenames, dimensions, alt text, public/private status, and destination slot.

OWNER_DECISION:

```text
批准 A4-ASSET-ICCTN-001，只做圖片 QA 與本機 WebP 轉檔，不上傳 WordPress。
```

## A3-GADS-ICCTN-001

WHY:

Venue-specific terms are high-intent and likely low-volume. A small Search test can guard the first page without entering broad `台南外燴` competition.

EVIDENCE:

- Public search observation did not show a dense cluster of dedicated caterer SEO pages for exact venue terms.
- Existing MAPLAB pages can support related event intent.
- Keyword Planner / live Google Ads CPC data is still missing.

PLAN:

- After the venue page is published, create a small exact/phrase Search test:
  - Daily cap: NT$100-200.
  - Keywords: venue exact terms and `ICC Tainan` variants.
  - Final URL: `icc-tainan-catering` with UTM.
  - Add hard negative keywords for便當, 團膳, 便宜, 停車, 交通, 門票, 場租, etc.
- Keep broad `台南外燴` terms out of this first test.

EXPECTED_EFFECT:

- Capture bottom-funnel venue search.
- Collect search terms for better negative-keyword refinement.

IMPACT_SCOPE:

- Google Ads campaign/ad group/keyword/final URL/negative keyword settings.
- Budget cap only within the exact approved amount.

RISKS:

- Low search volume.
- Without a published page, ad launch should wait.
- Negative keywords can accidentally block relevant buffet-style searches if applied too broadly.

ROLLBACK:

- Pause the new campaign/ad group.
- Remove newly added keywords and negatives from the new test.
- Revert final URLs to prior state if any existing campaign is touched.

VALIDATION:

- Campaign/ad group visible.
- Daily cap matches approval.
- Search terms reviewed after 14 days.
- No irrelevant便當/團膳/venue-info queries dominate spend.

OWNER_DECISION:

```text
批准 A3-GADS-ICCTN-001，但等 A2 頁面發布後才開，日預算上限 NT$200。
```

or:

```text
只批准關鍵字與否定字清單，不上線。
```

## A3-META-ICCTN-001

WHY:

Meta can build memory for `MAPLAB = 台南會展中心企業茶點 / 品牌接待`, especially after the new case images pass QA.

EVIDENCE:

- Existing B2B Meta seeds exist in prior Round 006/008 reports.
- A corporate decision-maker seed has evidence; B PR detail remains incomplete.
- New Drive folder can provide venue-specific creative.

PLAN:

- Do not modify current engagement campaigns.
- Build proposal for retargeting or a new landing-page traffic campaign after image QA.
- Use the venue page as destination only after publish.
- Do not use B PR seed for launch until UI detail is captured.

EXPECTED_EFFECT:

- Warm up enterprise/event organizer memory.
- Support future retargeting from website visitors and social engagers.

IMPACT_SCOPE:

- Meta campaign/ad set/creative/audience/budget only if explicitly approved.

RISKS:

- Meta interest targeting may be unstable.
- Public image rights and identifiable people must be cleared.

ROLLBACK:

- Pause the new campaign/ad set.
- Remove creative from ads.
- Keep existing campaigns unchanged.

VALIDATION:

- Landing URL loads with UTM.
- Creative has no private data.
- Pixel/GA4 pageview and CTA tracking are checked read-only if available.

OWNER_DECISION:

```text
批准 A3-META-ICCTN-001，只做素材與受眾 proposal，不上線。
```

or:

```text
批准 A3-META-ICCTN-001，上線前再送一次最終廣告預覽。
```
