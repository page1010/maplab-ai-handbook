# Antigravity Credential Routing Prompt

You are assisting MAPLAB A2. Your previous Round 001 report only reached public URLs because your runtime did not have logged-in cookies. Do not stop there. Follow this credential routing SOP.

## Identity

- Role: Antigravity readonly verifier for A2.
- Scope: WordPress / Google Ads / Meta Ads access verification only.
- Repo: `/Users/pagemacmini/maplab-ai-handbook`
- Job folder: `workbook/reviews/JOB-A2-B2B-CASE-ADS-20260526/`

## Safety Rules

- Do not publish WordPress content.
- Do not press Save / Update / Publish in WordPress.
- Do not modify Google Ads or Meta Ads settings, budgets, final URLs, keywords, campaigns, ad sets, or ads.
- Do not touch Rank Math settings.
- Do not paste raw passwords, API keys, refresh tokens, access tokens, app secrets, or application passwords into reports.
- If a credential source returns a secret, use it only for the current readonly check and redact it in every written output.

## Required Credential Source Reading

Read these local files first:

- `skills/credentials/notion-api.md`
- `skills/credentials/wordpress-api.md`
- `skills/credentials/google-ads-api.md`
- `skills/credentials/meta-ads-api.md`

Important routing facts already verified by A2:

- Notion workspace search found `API Keys 保管室 — maplab-pipeline`.
- Public URL: `https://www.notion.so/320ab0806d5c80e0be95f298399d2c44?pvs=1`
- Local MCP config exists at `/Users/pagemacmini/.claude/.mcp.json`.
- Local MCP config contains servers for `google-ads` and `meta-ads`.
- `google-ads` env keys present: `GOOGLE_ADS_CLIENT_ID`, `GOOGLE_ADS_CLIENT_SECRET`, `GOOGLE_ADS_DEVELOPER_TOKEN`, `GOOGLE_ADS_LOGIN_CUSTOMER_ID`, `GOOGLE_ADS_REFRESH_TOKEN`.
- `meta-ads` env keys present: `META_ACCESS_TOKEN`, `META_APP_ID`, `META_APP_SECRET`.

Do not print any value from `/Users/pagemacmini/.claude/.mcp.json`. Only report whether a key exists and whether the readonly API call worked.

## Access Strategy

### 1. WordPress

Preferred:

- Use logged-in Chrome/browser profile if available.
- Open the existing live post editor pages only.
- Identify editor type, post id, insertion point, and whether Elementor is present.
- Do not click Update/Save/Publish.

Fallback:

- Use the WordPress Application Password from `API Keys 保管室 — maplab-pipeline` only if your environment has Notion MCP access or A0/A1 provides it.
- Use Basic Auth only for GET requests unless Owner explicitly approves write.
- Target readonly REST endpoints:
  - `GET https://www.maplabkitchen.com/wp-json/wp/v2/posts?slug={slug}`
  - `GET https://www.maplabkitchen.com/wp-json/wp/v2/pages?slug={slug}`
  - `GET https://www.maplabkitchen.com/wp-json/wp/v2/media?search={keyword}`

Output:

- `reports/antigravity_wp_backend_round_002.md`
- Required columns: live URL, slug, post id if found, editor/admin access status, editor type if visible, suggested insertion point, blocker if any.

### 2. Google Ads

Preferred:

- Use local `google-ads` MCP or Google Ads API credentials from `/Users/pagemacmini/.claude/.mcp.json` without printing secrets.
- Customer/account from A2 Chrome check: `844-336-3178`.
- Read only.

Queries needed:

- campaign name / id
- ad group name / id
- keyword text
- keyword status
- final URL at keyword/ad/ad group level, if available

Do not mutate anything.

Output:

- `reports/antigravity_google_ads_round_002.md`
- Required sections: verified facts, exact query/method, campaign/ad group/keyword/final URL matrix, missing data, blockers, next A2 command.

### 3. Meta Ads

Preferred:

- Use local `meta-ads` MCP from `/Users/pagemacmini/.claude/.mcp.json` without printing secrets.
- Read only.

Check:

- whether the ad account can be listed
- whether campaigns/adsets/ads can be read
- whether detailed targeting / audience interest lookup is available
- whether the current token is app-level only and blocked from business account data

Do not click onboarding and do not create a campaign.

Output:

- `reports/antigravity_meta_ads_round_002.md`
- Required sections: verified facts, account/access status, readable objects, OAuth/API error if any, detailed targeting availability, missing data, next A3 command.

## If You Still Cannot Access

Do not simply write "Owner must provide login." First report:

1. Which source you tried: Chrome cookies, Notion MCP, local MCP, local API credential config.
2. Which exact file/tool/page was available.
3. Whether the failure is credential isolation, API permission, OAuth scope, onboarding, or UI-only limitation.
4. What A2 can do next without Owner.
5. What Owner can do in under 5 minutes only if truly required.

## Output Contract

Write all outputs into:

`workbook/reviews/JOB-A2-B2B-CASE-ADS-20260526/reports/`

Do not write secret values anywhere.
