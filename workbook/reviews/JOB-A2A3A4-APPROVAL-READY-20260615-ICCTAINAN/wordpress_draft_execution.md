# WordPress Draft Execution — A2-SEO-ICCTN-001

Date: 2026-06-15
Status: `execution_done`
Approved scope: create WordPress unpublished post draft only; do not publish.

## Intended Draft

- Post type: `post`
- Status: `draft`
- Slug: `icc-tainan-catering`
- Title: `大臺南會展中心活動外燴｜企業茶點與貴賓接待｜MAPLAB`
- Source content: `wordpress_draft_content.md`

## Attempted Routes

### Route 1 — Owner Chrome / WordPress admin

- Opened: `https://www.maplabkitchen.com/wp-admin/post-new.php`
- Result: redirected to `wp-login.php?redirect_to=...&reauth=1`
- Interpretation: current Chrome session does not have usable WordPress admin login state.

### Route 2 — Existing Chrome tabs

- Checked open Chrome tabs for active MAPLAB / WordPress admin context.
- Result: no logged-in WordPress editor/admin tab was available to claim.

### Route 3 — Credential skill + Notion vault

- Read `skills/credentials/wordpress-api.md`.
- Confirmed WordPress Application Password route is documented there.
- Owner instructed Codex to use Notion for the login/API method.
- Fetched the Notion API Keys 保管室 page as an Owner-approved credential vault / index.
- Confirmed the page contains WordPress Email + Application Password fields for the MAPLAB WordPress REST route.

### Route 4 — WordPress REST draft creation

- Prepared a non-secret JSON payload from `wordpress_draft_content.md`.
- Used an echo-disabled temporary helper and FIFO curl config so the WordPress credential did not appear in the shell command line.
- First sandboxed helper attempt could not resolve `www.maplabkitchen.com`; reran the same no-secret helper with escalated network access.
- Created the approved unpublished draft.
- Ran a second authenticated slug check; it returned the same post instead of creating a duplicate.

## Result

- Post ID: `1829`
- Status: `draft`
- Slug: `icc-tainan-catering`
- Link: `https://www.maplabkitchen.com/?p=1829`
- Edit URL: `https://www.maplabkitchen.com/wp-admin/post.php?post=1829&action=edit`
- Verification: authenticated slug check returned `exists`, ID `1829`, status `draft`, slug `icc-tainan-catering`.

## Boundary Observed

Secret handling rule for the corrected route:

- Do not write the WordPress Email, Application Password, Basic auth header, token, cookie, nonce, OTP, or backup code to repo, memory, logs, review bundles, Chrome side panel, or final replies.
- Use the credential only ephemerally for the approved `status=draft` WordPress REST operation.
- Do not publish, upload media, alter Rank Math, Ads, GTM, Pixel, budgets, or switches.

No WordPress content was published. No media was uploaded. No Rank Math, Ads, GTM, Pixel, budgets, switches, or payment settings were changed.

## Next Action

```text
Owner can review the unpublished draft:
https://www.maplabkitchen.com/wp-admin/post.php?post=1829&action=edit
```

Publishing, media upload, Rank Math, Ads, GTM, Pixel, budget, audience, or switch changes require separate explicit approval.
