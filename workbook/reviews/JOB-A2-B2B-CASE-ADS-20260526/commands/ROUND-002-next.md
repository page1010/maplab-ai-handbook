# ROUND 002 — Next Commands

日期：2026-05-26
管理方：A2

## Current Round 001 State

- Antigravity used `Gemini 3.1 Pro (High)` and confirmed 7 public live URLs, but failed logged-in WP / Google Ads / Meta access due cookie isolation.
- A2 used logged-in Chrome and captured Google Ads keyword table: 13 keyword rows, all in one campaign / ad group.
- A2 used logged-in Chrome and captured Meta Ads state: Ads Manager redirects to onboarding surface.
- A3, A4, A2 Round 001 reports are present.
- Hourly automation `a2-b2b-case-ads-loop-check` is active.

## Command To A2 — Google Ads Proposal Only

Create:

`workbook/reviews/JOB-A2-B2B-CASE-ADS-20260526/google_ads_change_plan.md`

Rules:

- Proposal only. Do not edit Google Ads.
- Use `reports/google_ads_chrome_round_001.md`.
- Split the current single ad group into proposed intent groups:
  - 會議茶點 / 研討會
  - 開幕茶會 / 辦公室
  - 企業 / 品牌 / 公關
  - To C 暫放
- For each keyword, specify:
  - current keyword
  - current status
  - proposed ad group
  - recommended final URL
  - whether to keep, pause later, or move later
  - reason

## Command To A2 — WordPress Update Plan

Create:

`workbook/reviews/JOB-A2-B2B-CASE-ADS-20260526/wordpress_update_plan.md`

Rules:

- Existing post update plan only. Do not publish, save, or touch Rank Math.
- Use `reports/a2_case_copy_round_001.md` and `asset_conversion_manifest_round_001.csv`.
- For each live URL, specify:
  - section title
  - copy block
  - image slot
  - alt / caption / description
  - internal link target
  - CTA
  - owner approval status

## Command To A4

Prepare local image outputs from `asset_conversion_manifest_round_001.csv`.

First pass:

- `brand_vip`
- `opening_tea`
- `corporate_meeting`

Output only to a local review folder under this job. Do not overwrite original images, do not upload WordPress, and do not use alcohol-first assets.

## Command To A3

Keep all Meta detailed targeting as `Needs UI Check`.

Do not click Meta onboarding. Wait for Owner/A3 decision on:

- business portfolio
- ad account availability
- pixel / custom audience
- whether to create or reuse campaign surfaces

## Owner Review Queue

1. Review `reports/a2_case_copy_round_001.md`.
2. Confirm whether external brand / school / venue names can stay in public website copy.
3. Confirm whether logo-heavy images should be site-only or ad-safe crop.
