# ROUND 002 — Antigravity Credential Routing Command

日期：2026-05-26
管理方：A2

## Give This To Antigravity

Use:

`workbook/reviews/JOB-A2-B2B-CASE-ADS-20260526/ANTIGRAVITY_CREDENTIAL_ROUTING_PROMPT.md`

Goal:

- Re-run backend / ads access verification with credential routing.
- Do not stop at "no cookies".
- Read local credential skills and local MCP presence.
- Use Notion/MCP/Chrome only in readonly mode.
- Do not print secrets.

## Expected Reports

- `reports/antigravity_wp_backend_round_002.md`
- `reports/antigravity_google_ads_round_002.md`
- `reports/antigravity_meta_ads_round_002.md`

## A2 Acceptance Criteria

- Report names exist.
- Each report separates verified facts, reasonable inferences, missing data, blockers, and next command.
- No secret values are present.
- No WordPress / Google Ads / Meta Ads setting was changed.
- If access fails again, the report must say which route failed: Chrome cookies, Notion MCP, local MCP, OAuth permission, or onboarding.
