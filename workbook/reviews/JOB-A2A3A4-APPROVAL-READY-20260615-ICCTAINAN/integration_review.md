# Integration Review

Date: 2026-06-15
Status: proposal_done

## What Was Verified

1. A2 role and boundaries
   - Local and remote A2 JSON identify this role as Ads SEO WordPress Patrol.
   - External changes need Owner/A1 approval.

2. Current task frontier
   - `T-A2-006` requires approval-ready planning, not stopping at "needs approval".
   - `T-A2A3-001-B` still has a saved WordPress draft frontier at `post=1696`, but this new venue plan is a separate landing-page opportunity.
   - Old planned slugs remain unsafe.

3. Drive asset source
   - Folder metadata and direct children were listed.
   - The folder is a real 2026-06-12 大台南會展中心 case candidate.

4. Public web source
   - Official venue site and service pages confirm venue/service context.
   - Existing MAPLAB pages cover corporate catering, meeting tea, expo/VIP reception, and opening tea.

5. Search-competition framing
   - This session did not verify live CPC or volume.
   - Public search observation supports treating the exact venue cluster as low-visible-competition, high-intent long tail.
   - Final spend decisions still require Google Ads read-only data or a capped test.

## Dependency Order

1. Owner approves public case-name level.
2. A4 performs visual QA and local WebP conversion.
3. A2 creates WordPress unpublished draft.
4. Owner reviews draft copy and images.
5. Owner approves publish, or keeps page draft-only.
6. After publish, A3 can launch a small Google Search test.
7. Meta retargeting / landing-page traffic can follow after image QA and page publish.

## Recommended First Move

Create the WordPress draft only.

Reason:

- It does not spend money.
- It creates the missing landing-page surface.
- It lets Owner review public naming and visual risks before Ads.
- It gives A3 a clean final URL later.

## Risks

- Search-volume risk: exact venue keywords may be small.
- Privacy risk: folder may include identifiable people or meeting materials.
- Brand risk: overusing `精緻` / hard-selling language would make the page sound generic.
- Ads risk: negative keywords need careful match types so relevant buffet-style event queries are not blocked.
- Evidence risk: public search observation is not the same as Keyword Planner CPC.

## No-Action Boundaries

No external changes were made:

- No WordPress publish or edit.
- No media upload.
- No Google Ads or Meta Ads changes.
- No Rank Math, GTM, Pixel, budget, switch, or payment changes.
- No secrets, cookies, or `.env` read.

## Resume Prompt

```text
你是 MAPLAB A2 Ads SEO WordPress Patrol，接手 JOB-A2A3A4-APPROVAL-READY-20260615-ICCTAINAN。

先讀：
1. CURRENT_STATUS.md
2. pitfalls.md
3. handoff/tasks/T-A2-006-ads-seo-wordpress-patrol.md
4. projects/a2a3a4-approval-ready-automation.md
5. workbook/reviews/JOB-A2A3A4-APPROVAL-READY-20260615-ICCTAINAN/README.md
6. workbook/reviews/JOB-A2A3A4-APPROVAL-READY-20260615-ICCTAINAN/owner_approval_card.md
7. workbook/reviews/JOB-A2A3A4-APPROVAL-READY-20260615-ICCTAINAN/a4_asset_manifest.md
8. workbook/reviews/JOB-A2A3A4-APPROVAL-READY-20260615-ICCTAINAN/a2_seo_wordpress_plan.md
9. workbook/reviews/JOB-A2A3A4-APPROVAL-READY-20260615-ICCTAINAN/a3_ads_strategy_plan.md

目前狀態：
- 已完成 approval-ready bundle。
- Drive folder 已核到：0612大台南會展中心-工研院在宅醫療科技推動計畫跨部會工作小組會議。
- 只做 metadata/listing，尚未下載、轉檔、上傳或發布。
- 建議第一步只批准 A2-SEO-ICCTN-001：建立 WordPress 未發布草稿，slug `icc-tainan-catering`。
- 廣告需等頁面發布後才上線；Google Ads 先 exact/phrase，小額測試；Meta 先做記憶點和再行銷 proposal。

Blockers / decisions:
- Owner 需決定完整活動名稱是否可公開。
- Owner 需批准是否先做 A4 圖片 QA 與本機 WebP 轉檔。
- 未經 Owner/A1 批准，不發布、不改 Ads、不動 Rank Math/GTM/Pixel/預算/開關。
```
