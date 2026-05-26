# Antigravity Meta Account Recheck Prompt

You are assisting A2. The active path is Owner Chrome UI evidence, not API token access.

## Why This Round Exists

Owner clarified that Meta Ads is visible in Owner Chrome and is meant for A2 to inspect. A2 then rechecked Meta Ads Manager by Chrome UI and found a current-account discrepancy:

- Earlier evidence had `318634712` with 13 visible campaigns.
- Current Chrome UI now lands on `2441634989673207`, shows one ad account in the account selector, and has no visible campaigns.
- Searching the account selector for `318634712` returns `查無結果`.
- A2 did not click Accept on the nondiscrimination policy modal and did not modify ads.

## Read First

Read:

- `workbook/reviews/JOB-A2-B2B-CASE-ADS-20260526/reports/meta_ads_chrome_round_002_account_recheck.md`
- `workbook/reviews/JOB-A2-B2B-CASE-ADS-20260526/reports/meta_ads_chrome_round_001.md`
- `workbook/reviews/JOB-A2-B2B-CASE-ADS-20260526/reports/a3_meta_round_001.md`
- `workbook/reviews/JOB-A2-B2B-CASE-ADS-20260526/reports/antigravity_chrome_ui_analysis_round_003.md`

## Output

Create:

`workbook/reviews/JOB-A2-B2B-CASE-ADS-20260526/reports/antigravity_meta_account_recheck_round_004.md`

## Required Sections

1. Verified facts from A2 Chrome UI
2. Account-context discrepancy
   - what was visible before
   - what is visible now
   - what cannot be claimed yet
3. Corrected Meta Ads plan for this job
   - path if `318634712` can be restored in Chrome UI
   - path if only `2441634989673207` is available
4. B2B interest planning without pretending current ad sets were verified
   - proposal-only interest clusters
   - existing-audience reuse status
   - retargeting prerequisites
5. Exact next Chrome UI check for A2
   - where to click
   - what text or screenshot evidence is enough
   - what not to click
6. Updated instruction to A3 Meta worker
7. Updated owner review question, if any

## Guardrails

- Do not ask Owner for API tokens, OAuth refresh, app secrets, or passwords.
- Do not call the task blocked just because Antigravity cannot control Owner Chrome directly.
- Do not claim the 13 campaigns are currently visible unless the latest Chrome UI report proves it.
- Do not propose accepting policy dialogs without explicit Owner approval.
- Do not publish, save, create, duplicate, or edit Meta campaigns.
- Keep all targeting as proposal-only until UI evidence confirms actual ad set settings.
