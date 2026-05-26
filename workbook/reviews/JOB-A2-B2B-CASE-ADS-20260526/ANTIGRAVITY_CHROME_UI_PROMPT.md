# Antigravity Chrome UI Evidence Prompt

Your previous Round 002 conclusion is superseded for this job.

Important correction from Owner:

- The credentials are not for an agent API route.
- Owner's Chrome already has Meta Ads, Google Ads, and WordPress backend access.
- A2 can read the logged-in Chrome UI and provide evidence.
- Your job is to analyze A2's Chrome UI evidence and tell A2 exactly which UI screens to inspect next.

Do not ask Owner to refresh Google Ads OAuth, generate Meta User Access Token, or extract WordPress Application Password for this task. Those may be useful for future API automation, but they are not the active path now.

## Read First

Read:

- `workbook/reviews/JOB-A2-B2B-CASE-ADS-20260526/reports/a2_chrome_ui_access_round_002.md`
- `workbook/reviews/JOB-A2-B2B-CASE-ADS-20260526/reports/google_ads_chrome_round_001.md`
- `workbook/reviews/JOB-A2-B2B-CASE-ADS-20260526/reports/meta_ads_chrome_round_001.md`
- `workbook/reviews/JOB-A2-B2B-CASE-ADS-20260526/google_ads_change_plan.md`
- `workbook/reviews/JOB-A2-B2B-CASE-ADS-20260526/wordpress_update_plan.md`

## Output

Create:

`workbook/reviews/JOB-A2-B2B-CASE-ADS-20260526/reports/antigravity_chrome_ui_analysis_round_003.md`

## Required Sections

1. Verified Chrome UI facts
2. Corrections to your Round 002 API/token conclusion
3. Meta campaign triage
   - B2B useful
   - To C useful later
   - noise / ignore for this job
4. Which Meta UI screen A2 should inspect next
   - exact tab/layer name
   - what field to read
   - what screenshot/text evidence is enough
5. Which Google Ads UI screen A2 should inspect next
   - exact navigation path
   - final URL field priority
   - what must not be clicked
6. Which WordPress UI screen A2 should inspect next
   - exact post/editor target
   - what to read
   - what must not be saved
7. Next command for A2

## Guardrails

- Do not ask for API tokens or passwords.
- Do not publish WordPress.
- Do not modify Google Ads or Meta Ads.
- Do not touch Rank Math settings.
- Do not treat API token failure as UI access failure.
- Do not include any secret values in the report.
